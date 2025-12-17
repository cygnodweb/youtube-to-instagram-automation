-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.videos (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  youtube_video_id text NOT NULL UNIQUE,
  title text NOT NULL,
  description text,
  thumbnail_url text,
  youtube_url text NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  downloaded boolean DEFAULT false,
  download_url text,
  download_filename text,
  posted_to_instagram boolean DEFAULT false,
  instagram_post_id text,
  instagram_post_url text,
  processed_at timestamp with time zone,
  error_message text,
  channelTitle text,
  CONSTRAINT videos_pkey PRIMARY KEY (id)
);
CREATE TABLE public.workflow_logs (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  workflow_name text NOT NULL DEFAULT 'youtube_to_instagram'::text,
  video_id uuid,
  youtube_video_id text,
  step_name text NOT NULL,
  status text NOT NULL,
  message text,
  data jsonb,
  created_at timestamp with time zone DEFAULT now(),
  youtube_url text,
  CONSTRAINT workflow_logs_pkey PRIMARY KEY (id),
  CONSTRAINT workflow_logs_video_id_fkey FOREIGN KEY (video_id) REFERENCES public.videos(id)
);
CREATE TABLE public.youtube_videos (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  video_id text NOT NULL UNIQUE,
  title text NOT NULL,
  description text,
  thumbnail_url text,
  video_url text NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  downloaded boolean DEFAULT false,
  download_url text,
  download_filename text,
  posted_to_instagram boolean DEFAULT false,
  instagram_post_id text,
  instagram_post_url text,
  processed_at timestamp with time zone,
  error_message text,
  CONSTRAINT youtube_videos_pkey PRIMARY KEY (id)
);
CREATE TABLE public.youtube_workflow_logs (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  workflow_name text NOT NULL DEFAULT 'youtube_to_instagram'::text,
  video_ref uuid,
  video_id text,
  step_name text NOT NULL,
  status text NOT NULL,
  message text,
  data jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT youtube_workflow_logs_pkey PRIMARY KEY (id),
  CONSTRAINT youtube_workflow_logs_video_ref_fkey FOREIGN KEY (video_ref) REFERENCES public.youtube_videos(id)
);
