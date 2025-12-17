# YouTube → Instagram Reels Automation (n8n + Supabase + Render)

A **simple, public-ready automation system** to manage and publish Instagram Reels using **n8n**, **Supabase**, and **Render (Free Tier)**.

This repository is written so **anyone can clone it and set it up easily**, without prior DevOps knowledge.

---

## ✨ What This Project Does

- Uses **n8n** as the automation engine
- Uses **Supabase Postgres** as the persistent database for workflows
- Runs fully on **Render Free Tier** using **Existing Docker Image**
- Stores credentials securely using environment variables
- No custom backend services required

---

## 🧠 High-Level Architecture

```
User / Cron Trigger
      ↓
Render (n8n Docker Container)
      ↓
Supabase Postgres (Workflow DB)
      ↓
Instagram Graph API
```

---

## ☁️ Deployment Platform

- **Render** → hosts n8n (Free Tier)
- **Supabase** → managed PostgreSQL database

No self-hosted database. No VPS. No Docker Compose.

---

## 🐳 n8n on Render (Using Existing Image)

Render already supports running Docker images directly.
You only need to paste the image URL and set environment variables.

### Docker Image

```
docker.io/n8nio/n8n:latest
```

---

## 🚀 Render Setup (Step-by-Step)

1. Go to **Render Dashboard**
2. Click **New → Web Service**
3. Select **Existing Image**
4. Paste Docker image:

```
docker.io/n8nio/n8n:latest
```

5. Instance Type: **Free**
6. Port: `5678`

---

## 🔐 Environment Variables (Safe Template)

> ⚠️ **Important**: The values below are **placeholders**.
> Replace them with your own Supabase credentials.

### Database Configuration (Supabase Postgres)

```
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=your-project.pooler.supabase.com
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=postgres
DB_POSTGRESDB_USER=postgres.xxxxx
DB_POSTGRESDB_PASSWORD=your_password_here
DB_POSTGRESDB_SSL=true
```

These variables allow n8n to store:
- Workflows
- Executions
- Credentials

inside Supabase instead of local storage.

---

## 🗄️ Supabase Setup

1. Create a project at **Supabase**
2. Go to **Project Settings → Database**
3. Copy **Transaction Pooler** credentials
4. Use those values in Render environment variables

No schema creation is required — n8n manages tables automatically.

---

## 🌐 Accessing n8n

After deployment completes:

```
https://your-service-name.onrender.com
```

First load may take **20–30 seconds** due to free-tier cold start.

---

## ⚠️ Render Free Tier Notes

- Services sleep after inactivity
- Cold start delay is normal
- Data is safe because it lives in Supabase
- You can add an external cron ping to keep it awake

---

## 🔒 Security Notes

- Never commit real credentials
- Always use environment variables
- Rotate Supabase passwords if exposed

---

## 📦 What This Repo Does NOT Include

- No video downloader service
- No media processing backend
- No hardcoded secrets

This is **automation-only**, clean and minimal.

---

## 📜 License

MIT License — free to use, modify, and share.

---

## ✅ Ready for GitHub

This README is:
- Public-safe
- Beginner-friendly
- Free-tier compatible
- Production-structured

You can now push this repository publicly without changes.

