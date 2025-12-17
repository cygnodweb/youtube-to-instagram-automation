from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import glob
import threading
import time
import shutil

app = Flask(__name__)
CORS(app)

# --- Configuration ---
DOWNLOAD_ROOT = "downloads"
BASE_URL = os.environ.get("BASE_URL", "https://welcome-laden-oriented-villas.trycloudflare.com")
FILE_TTL_SECONDS = 60 * 60  # keep files for 1 hour by default
CLEANUP_INTERVAL = 10 * 60  # run cleanup every 10 minutes

# Instagram-friendly yt-dlp options (still need final ffmpeg pass below)
YTDL_INSTAGRAM_OPTIONS = {
    'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'quiet': False,
    'no_warnings': True,
    'prefer_ffmpeg': True,
    'merge_output_format': 'mp4',
    'outtmpl': '%(title).40s.%(ext)s',
    'postprocessors': [
        {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
    ],
    'postprocessor_args': [
        '-c:v', 'libx264',
        '-profile:v', 'high',
        '-level', '4.0',
        '-preset', 'veryfast',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart'
    ],
    'retries': 3,
    'fragment_retries': 3,
    'skip_unavailable_fragments': True,
}

# fallback
YTDL_SIMPLE_OPTIONS = {
    'format': 'mp4/best[height<=720]/best',
    'restrictfilenames': True,
    'noplaylist': True,
}

file_store = {}


def start_cleanup_thread():
    def cleanup_loop():
        while True:
            try:
                now = time.time()
                removed = []
                for fname, meta in list(file_store.items()):
                    created = meta.get('created_time', 0)
                    if now - created > FILE_TTL_SECONDS:
                        path = meta.get('path')
                        try:
                            if path and os.path.exists(path):
                                os.remove(path)
                        except Exception:
                            pass
                        file_store.pop(fname, None)
                        removed.append(fname)

                # Remove empty session folders
                for session_dir in glob.glob(os.path.join(DOWNLOAD_ROOT, '*')):
                    try:
                        if os.path.isdir(session_dir) and not os.listdir(session_dir):
                            shutil.rmtree(session_dir)
                    except Exception:
                        pass

            except Exception:
                app.logger.exception("Cleanup thread error")

            time.sleep(CLEANUP_INTERVAL)


@app.route('/download', methods=['GET', 'POST'])
def download():
    url = request.form.get('url') if request.method == 'POST' else request.args.get('url')
    if not url:
        return jsonify({"success": False, "error": "Missing url parameter"}), 400

    os.makedirs(DOWNLOAD_ROOT, exist_ok=True)
    session_id = uuid.uuid4().hex[:8]
    session_folder = os.path.join(DOWNLOAD_ROOT, session_id)
    os.makedirs(session_folder, exist_ok=True)

    short_template = os.path.join(session_folder, "ig_%(title).40s.%(ext)s")

    try:
        app.logger.info(f"Starting download for {url} in session {session_id}")
        opts = YTDL_INSTAGRAM_OPTIONS.copy()
        opts['outtmpl'] = short_template

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Try to locate file
        if not os.path.exists(filename):
            mp4s = glob.glob(os.path.join(session_folder, '*.mp4'))
            if mp4s:
                filename = mp4s[0]
            else:
                anyf = glob.glob(os.path.join(session_folder, '*'))
                if anyf:
                    filename = anyf[0]
                else:
                    raise FileNotFoundError("Output file missing")

        # --- FORCE FINAL INSTAGRAM-SAFE RE-ENCODE ---
        final_output = os.path.join(session_folder, "final_instagram.mp4")

        ffmpeg_cmd = (
            f'ffmpeg -y -i "{filename}" '
            f'-c:v libx264 -profile:v high -level 4.0 '
            f'-preset veryfast -crf 23 '
            f'-c:a aac -b:a 128k '
            f'-movflags +faststart "{final_output}"'
        )

        os.system(ffmpeg_cmd)
        filename = final_output

        file_basename = os.path.basename(filename)
        file_size = os.path.getsize(filename)
        download_url = f"{BASE_URL}/get_file/{file_basename}"

        file_store[file_basename] = {
            'path': filename,
            'created_time': time.time(),
            'session_id': session_id,
            'file_size': file_size
        }

        return jsonify({
            'success': True,
            'downloadUrl': download_url,
            'filename': file_basename,
            'fileSize': file_size,
            'title': info.get('title'),
            'duration': info.get('duration')
        })

    except Exception as e:
        app.logger.exception("Primary download failed")

        try:
            opts = YTDL_SIMPLE_OPTIONS.copy()
            opts['outtmpl'] = os.path.join(session_folder, "fallback_%(id)s.%(ext)s")

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            if not os.path.exists(filename):
                anyf = glob.glob(os.path.join(session_folder, '*'))
                if anyf:
                    filename = anyf[0]
                else:
                    raise FileNotFoundError("Fallback file missing")

            # Fallback also re-encode to safe mp4
            final_output = os.path.join(session_folder, "final_instagram_fallback.mp4")
            os.system(
                f'ffmpeg -y -i "{filename}" -c:v libx264 -profile:v high -level 4.0 '
                f'-preset veryfast -crf 23 -c:a aac -b:a 128k '
                f'-movflags +faststart "{final_output}"'
            )
            filename = final_output

            file_basename = os.path.basename(filename)
            file_size = os.path.getsize(filename)
            download_url = f"{BASE_URL}/get_file/{file_basename}"

            file_store[file_basename] = {
                'path': filename,
                'created_time': time.time(),
                'session_id': session_id,
                'file_size': file_size
            }

            return jsonify({
                'success': True,
                'downloadUrl': download_url,
                'filename': file_basename,
                'fileSize': file_size,
                'title': info.get('title'),
                'duration': info.get('duration'),
                'note': 'Fallback used'
            })

        except Exception:
            app.logger.exception("Fallback failed")
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/get_file/<filename>', methods=['GET'])
def get_file(filename):
    if filename not in file_store:
        search_pattern = os.path.join(DOWNLOAD_ROOT, '**', filename)
        files_found = glob.glob(search_pattern, recursive=True)
        if files_found:
            file_path = files_found[0]
            file_store[filename] = {
                'path': file_path,
                'created_time': time.time(),
                'session_id': os.path.basename(os.path.dirname(file_path)),
                'file_size': os.path.getsize(file_path)
            }
        else:
            return jsonify({'error': 'File not found'}), 404

    file_path = file_store[filename]['path']

    if not os.path.exists(file_path):
        return jsonify({'error': 'File missing'}), 404

    try:
        return send_file(file_path, as_attachment=True, download_name=filename)
    except TypeError:
        return send_file(file_path, as_attachment=True, attachment_filename=filename)


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'active_downloads': len(file_store),
        'timestamp': time.time()
    })


@app.route('/debug')
def debug():
    files_info = [
        {
            'filename': fn,
            'path': meta['path'],
            'size': meta.get('file_size', 0),
            'exists': os.path.exists(meta['path'])
        }
        for fn, meta in file_store.items()
    ]
    return jsonify({
        'file_store_count': len(file_store),
        'files': files_info,
        'downloads_folder_exists': os.path.exists(DOWNLOAD_ROOT)
    })


@app.route('/cleanup', methods=['DELETE'])
def cleanup():
    try:
        deleted_count = 0
        for filename, info in list(file_store.items()):
            try:
                if os.path.exists(info['path']):
                    os.remove(info['path'])
                    deleted_count += 1
            except Exception:
                pass
            file_store.pop(filename, None)

        for session_dir in glob.glob(os.path.join(DOWNLOAD_ROOT, '*')):
            try:
                if os.path.isdir(session_dir) and not os.listdir(session_dir):
                    shutil.rmtree(session_dir)
            except Exception:
                pass

        return jsonify({'success': True, 'deleted_count': deleted_count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    os.makedirs(DOWNLOAD_ROOT, exist_ok=True)
    t = threading.Thread(target=start_cleanup_thread, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
