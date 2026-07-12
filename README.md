# VidLink Pro 🎬

> Multi-platform video downloader — TikTok, Instagram, YouTube, Facebook, Twitter
> Zero server bandwidth · Direct download · No new tab

**Live site:** https://vidlink.10001mb.com

---

## Architecture

```
Browser (InfinityFree)
    ↓  POST /api/info  (2KB JSON only)
Render Backend  ←  yt-dlp extracts CDN URL
    ↓  returns CDN URL to browser
Browser
    ↓  GET /?url=CDN_URL
Cloudflare Worker  ←  streams video from CDN
    ↓
File downloads directly ✅
```

**Render bandwidth: ~2KB per request (zero video)**
**Cloudflare: unlimited free bandwidth**

---

## Folder Structure

```
vidlink-pro/
├── frontend/          ← InfinityFree-তে upload করো
│   ├── index.html
│   └── assets/
│       ├── style.css
│       └── main.js
│
├── backend/           ← Render-এ deploy করো
│   ├── app.py
│   ├── requirements.txt
│   ├── render.yaml
│   └── services/
│       ├── ytdlp_handler.py
│       └── api_handler.py
│
└── cloudflare-worker/  ← Cloudflare Workers-এ paste করো
    └── worker.js
```

---

## Setup Guide

### Step 1: Render Backend Deploy

1. GitHub-এ এই repo fork করো
2. https://render.com → New Web Service
3. GitHub repo connect করো
4. **Root directory:** `backend`
5. **Build command:** `pip install -r requirements.txt`
6. **Start command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
7. Environment Variables:
   - `RAPIDAPI_KEY` = তোমার RapidAPI key
8. Deploy করো → URL পাবে (যেমন: `https://vidlink-api.onrender.com`)

### Step 2: Cloudflare Worker Deploy

1. https://dash.cloudflare.com → Workers & Pages → Create
2. `cloudflare-worker/worker.js` এর content paste করো
3. `ALLOWED_ORIGIN` = `https://vidlink.10001mb.com` (already set)
4. Deploy করো → Worker URL পাবে

### Step 3: Frontend Config Update

`frontend/assets/main.js` এ দুটো URL update করো:

```js
const API_BASE  = "https://vidlink-api.onrender.com";   // তোমার Render URL
const CF_WORKER = "https://vidlink-worker.xxx.workers.dev"; // তোমার Worker URL
```

### Step 4: InfinityFree Upload

1. `frontend/` folder-এর সব file upload করো
2. `index.html` → root-এ
3. `assets/` folder → root-এ

---

## Features

- ✅ TikTok (no watermark)
- ✅ Instagram (Reels, Posts)
- ✅ YouTube
- ✅ Facebook
- ✅ Twitter / X
- ✅ Audio extract (MP3/M4A)
- ✅ Multi-resolution (4K → 360p)
- ✅ Language switcher (বাংলা / English)
- ✅ Direct download (no new tab)
- ✅ Zero server bandwidth

---

## Environment Variables (Render)

| Key | Value | Required |
|-----|-------|----------|
| `RAPIDAPI_KEY` | RapidAPI key | Optional (HD only) |

---

*© 2025 VidLink Pro — Personal use only*
