# 🎬 YouTube → Instagram Reels Automation

A fully automated **YouTube-to-Instagram Reels pipeline** built with **n8n**, **Flask**, **yt-dlp**, **FFmpeg**, and **Supabase**.
This system fetches the latest YouTube videos from a channel, downloads and converts them into **Instagram-safe MP4 Reels**, stores metadata in a database, and publishes them automatically to Instagram.

---

## ✨ What This Project Does

* ⏱️ Runs **every hour** (Cron-based)
* 📺 Fetches latest videos from a YouTube channel
* 🧠 Avoids duplicates using database checks
* 📥 Downloads videos via a custom Flask service
* 🎞️ Re-encodes videos to Instagram-compliant MP4
* ☁️ Serves files via secure temporary URLs
* 📸 Uploads & publishes Instagram Reels automatically
* 🧾 Logs every step for full traceability

---

## 🏗️ Architecture Overview

```
YouTube API
   ↓
n8n Cron Workflow
   ↓
Supabase (videos + logs)
   ↓
Flask Downloader Service (yt-dlp + FFmpeg)
   ↓
Temporary Public MP4 URL
   ↓
Instagram Graph API (Reels)
```

---

## 🧰 Tech Stack

* **Backend**: Flask (Python)
* **Downloader**: yt-dlp + FFmpeg
* **Automation**: n8n
* **Database**: Supabase (PostgreSQL)
* **APIs**:

  * YouTube Data API v3
  * Instagram Graph API
* **Hosting**:

  * Flask exposed via Cloudflare Tunnel
  * n8n (self-hosted or cloud)

---

## 📁 Project Structure

```
server/
 ├── app.py              # Flask downloader service
 ├── downloads/          # Temporary video storage

n8n/
 ├── workflow.json       # n8n automation workflow

supabase/
 ├── schema.sql          # Database schema
```

---

## 🔑 Required Credentials (What & Where to Get Them)

### 1️⃣ YouTube Data API Key

**Used for**: Fetching latest videos from a channel

**Steps to get**:

1. Go to Google Cloud Console
2. Create a new project
3. Enable **YouTube Data API v3**
4. Go to *Credentials* → Create API Key

**Used in n8n node**:

* `Fetch YouTube Videos`

---

### 2️⃣ Instagram Graph API (Reels Publishing)

**Used for**: Uploading and publishing Instagram Reels

**Requirements**:

* Instagram **Business** or **Creator** account
* Facebook Page connected to Instagram

**Steps**:

1. Go to Meta for Developers
2. Create an App (Business type)
3. Add **Instagram Graph API** product
4. Generate a **Long-Lived Access Token**
5. Get your **Instagram User ID**

**APIs Used**:

* `/media` → Upload Reel
* `/media_publish` → Publish Reel

---

### 3️⃣ Supabase Credentials

**Used for**:

* Storing video metadata
* Tracking workflow status
* Preventing duplicate uploads

**Steps**:

1. Create a project at supabase.com
2. Copy:

   * Project URL
   * Anon/Public API Key
3. Run provided SQL schema

**Tables Used**:

* `videos`
* `workflow_logs`

---

### 4️⃣ Cloudflare Tunnel URL

**Used for**:

* Exposing Flask downloader publicly
* Providing Instagram-accessible MP4 URLs

**Steps**:

1. Install `cloudflared`
2. Run:

   ```bash
   cloudflared tunnel --url http://localhost:5000
   ```
3. Copy the generated `https://*.trycloudflare.com` URL
4. Set it as `BASE_URL`

---

## ⚙️ Flask Downloader Service Setup

### 📦 Requirements

```bash
pip install flask flask-cors yt-dlp
sudo apt install ffmpeg
```

### ▶️ Run Server

```bash
python3 app.py
```

Server will start on:

```
http://0.0.0.0:5000
```

### 📥 Download Endpoint

```
GET /download?url=<youtube_url>
```

**Response**:

```json
{
  "success": true,
  "downloadUrl": "https://.../get_file/final_instagram.mp4",
  "filename": "final_instagram.mp4",
  "fileSize": 12345678,
  "title": "Video Title",
  "duration": 120
}
```

---

## 🎞️ Instagram-Safe Video Encoding

Every video is **force re-encoded** using FFmpeg:

* Codec: H.264 (libx264)
* Profile: High
* Level: 4.0
* Audio: AAC 128 kbps
* Fast Start enabled

This guarantees **maximum Instagram compatibility**.

---

## 🧠 n8n Workflow Logic (High Level)

1. ⏰ Cron triggers every hour
2. 🔍 Fetch latest YouTube videos
3. ❌ Skip videos already in database
4. 📝 Insert new video record
5. 📥 Call Flask downloader
6. ✅ Update download status
7. 📸 Upload Reel to Instagram
8. 🚀 Publish Reel
9. 📊 Log every step

---

## 🗄️ Database Schema

### `videos`

Stores the lifecycle of each video.

Key fields:

* `youtube_video_id`
* `download_url`
* `downloaded`
* `posted_to_instagram`

### `workflow_logs`

Stores detailed workflow execution logs.

---

## 🧹 Automatic Cleanup

* Files auto-delete after **1 hour**
* Empty session folders removed
* Manual cleanup available:

```
DELETE /cleanup
```

---

## 🩺 Health & Debug Endpoints

* `GET /health` → Service status
* `GET /debug` → File & state inspection

---

## 🚀 Deployment Tips

* Run Flask behind **Cloudflare Tunnel** or **Nginx**
* Use **PM2 / Supervisor** for persistence (non-Docker)
* Store tokens as environment variables
* Limit Instagram API rate usage

---

## ☁️ Render (Free Tier) Deployment Guide

Render already supports **Existing Docker Images**, so you **do not need to build or push your own Docker image** if you use official images.

You only need to:

* Select **Existing Image**
* Paste the Docker image name
* Add environment variables

That’s it — Render handles the rest.

---

## 🐳 Render Setup Using Existing Docker Images (Recommended)

### ✅ Option 1: n8n on Render (Existing Image)

**Docker Image**:

```
docker.io/n8nio/n8n:latest
```

### Steps

1. Go to **Render Dashboard** → **New Web Service**
2. Choose **Existing Image**
3. Paste image:

```
docker.io/n8nio/n8n:latest
```

4. Instance Type: **Free**
5. Port: `5678`

### 🔐 Environment Variables (Very Important)

Add these in Render → *Environment*:

```
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=your-project.pooler.supabase.com
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=postgres
DB_POSTGRESDB_USER=postgres.xxxxx
DB_POSTGRESDB_PASSWORD=your_password_here
DB_POSTGRESDB_SSL=true
```

After deploy, access n8n at:

```
https://your-n8n.onrender.com
```

---

### ✅ Option 2: Flask Downloader on Render (Existing Image)

For Flask, you **do need a custom image** because:

* FFmpeg is required
* yt-dlp is required

But you **do not need Docker Compose**.

You can:

* Build once
* Push to Docker Hub
* Reuse forever

**Example Image**:

```
yourdockerhub/flask-yt-dlp-instagram
```

---

### Flask Render Setup Steps

1. New Web Service → **Existing Image**
2. Paste your image name
3. Port: `5000`
4. Instance: **Free**

### 🌍 Flask Environment Variables

```
BASE_URL=https://your-flask.onrender.com
```

Deploy and you’re done.

---

## 🗄️ Supabase Configuration (Render Friendly)

Supabase runs **outside Render** and is only connected via API keys.

### Add Supabase Keys

In **n8n → Credentials → Supabase** OR Render Env (if used in code):

```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=public-anon-key
```

No database hosting needed on Render.

---

## 🔄 Final Render Flow (Simple)

```
Render n8n (Existing Image)
   ↓
Supabase (Managed DB)
   ↓
Render Flask (Docker Image)
   ↓
Public MP4 URL
   ↓
Instagram Graph API
```

---

## ⚠️ Render Free Tier Notes

* Services sleep after inactivity

* Cold start: ~20–30 seconds

* Cron keeps n8n awake

* Instagram fetch works fine with public URLs

* Services sleep after inactivity

* First request may take ~30s

* Keep Cron active to avoid sleep

* Video files are temporary (auto-cleaned)

---

## 🔐 Security Notes

* Temporary file URLs only
* Files auto-expire
* No permanent public storage
* Avoid committing API keys

---

## 🎉 Final Notes

This system is designed for **hands-free content repurposing**.
Once configured, it quietly works in the background—fetching, converting, uploading, and logging everything automatically.

Perfect for creators, media teams, and automation enthusiasts.

---

## ⭐ If You Found This Useful

Give the repo a ⭐ and feel free to fork, extend, or optimize it further.

Happy automating 🤖🚀
