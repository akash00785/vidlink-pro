# VidLink Pro 🎬

> Multi-platform video downloader — TikTok, Instagram, YouTube, Facebook, Twitter
> Zero server bandwidth · Direct download · No new tab

**Live site:** তোমার Render URL (বা পরে বসানো custom domain)

---

## Architecture

শুধু ২টা সার্ভিস — InfinityFree আর দরকার নেই। Render একই সাথে frontend
(static site) আর backend (API) দুটোই সার্ভ করে।

```
Browser
    ↓  GET /                (Render থেকেই frontend সার্ভ হয়)
    ↓  POST /api/info       (2KB JSON only)
Render (Flask)  ←  yt-dlp / RapidAPI দিয়ে CDN URL বের করে
    ↓  returns CDN URL to browser
Browser
    ↓  GET <worker>?url=CDN_URL
Cloudflare Worker  ←  streams video/audio from CDN
    ↓
File downloads directly ✅
```

**Render bandwidth: ~2KB per request (zero video)**
**Cloudflare: unlimited free bandwidth**

TikTok-এর জন্য **Normal/SD সবসময় ফ্রি yt-dlp দিয়ে সাথে সাথে** আসে (কোনো
API key লাগে না)। `RAPIDAPI_KEY` সেট থাকলে একটা আলাদা **"HD (No
Watermark)"** বাটন দেখা যায় — সেটাতে ক্লিক করলে তখনই RapidAPI কল হয়
(lazy resolve, কোটা বাঁচাতে)। TikTok ফটো/স্লাইডশো পোস্ট (`/photo/` URL)
সবসময় RapidAPI দিয়েই হয়, কারণ yt-dlp এগুলোর ছবি বের করতে পারে না।

---

## Folder Structure

```
vidlink-pro/
├── frontend/           ← Render থেকেই সার্ভ হয় (backend/app.py এটা পড়ে)
│   ├── index.html
│   └── assets/
│       ├── style.css
│       └── main.js
│
├── backend/            ← Render-এ deploy করো (frontend+API দুটোই এখান থেকে চলে)
│   ├── app.py
│   ├── requirements.txt
│   ├── render.yaml
│   └── services/
│       ├── ytdlp_handler.py
│       └── api_handler.py
│
└── cloudflare-worker/  ← Cloudflare Workers-এ paste করো (video/audio proxy)
    └── worker.js
```

---

## Setup Guide

### Step 1: Render Deploy (frontend + backend একসাথে)

1. GitHub-এ এই repo fork/push করো
2. https://render.com → New Web Service → GitHub repo connect করো
3. `render.yaml` থাকায় Render নিজে থেকেই root directory (`backend`), build
   command, start command detect করে নেবে (Blueprint হিসেবে দেখাবে)
4. Environment Variables:
   - `RAPIDAPI_KEY` = তোমার RapidAPI key (TikTok HD/ফটো পোস্ট/audio-এর
     জন্য, optional)। একাধিক key থাকলে কমা দিয়ে দাও, যেমন:
     `RAPIDAPI_KEY=keyA,keyB,keyC` — একটা key rate-limit (429) খেলে
     backend নিজে থেকেই পরের key-তে সুইচ করবে।
5. Deploy করো → URL পাবে (যেমন: `https://vidlink-pro.onrender.com`)
6. এই একই URL-এ গেলে পুরো ওয়েবসাইট দেখা যাবে — আলাদা frontend hosting লাগবে না

### Step 2: Cloudflare Worker Deploy

1. https://dash.cloudflare.com → Workers & Pages → Create
2. `cloudflare-worker/worker.js` এর content paste করো
3. Deploy করো → Worker URL পাবে

### Step 3: Frontend Config Update

`frontend/assets/main.js` এ Worker URL update করো (API_BASE খালি রাখো —
same-origin এ কাজ করবে):

```js
const API_BASE  = "";  // Render নিজেই frontend+API সার্ভ করে
const CF_WORKER = "https://vidlink-worker.xxx.workers.dev"; // তোমার Worker URL
```

### Step 4 (ঐচ্ছিক): Custom Domain

Render dashboard → Settings → Custom Domain-এ নিজের কেনা ডোমেইন যোগ করলে
পুরো সাইট (frontend + API) সেই ডোমেইন থেকেই চলবে। CORS/Worker কনফিগ ওপেন
রাখা হয়েছে বলে ডোমেইন বদলালে কোথাও আলাদা করে কিছু বদলাতে হবে না।

---

## Features

- ✅ TikTok — Normal/SD সবসময় ফ্রি yt-dlp দিয়ে; `RAPIDAPI_KEY` সেট থাকলে
  আলাদা lazy "HD (No Watermark)" বাটন + ফটো/স্লাইডশো পোস্ট সাপোর্ট
- ✅ একাধিক RapidAPI key rotation (comma-separated) + 45 মিনিটের
  in-memory response cache — quota বাঁচাতে
- ✅ Instagram (Reels, Posts)
- ✅ YouTube (progressive formats — এখানে ৭২০p পর্যন্ত পাওয়া যায়, কারণ
  ১০৮০p+ আলাদা video/audio merge (ffmpeg) দরকার হয় যা zero-bandwidth
  আর্কিটেকচারে ইচ্ছাকৃতভাবে এড়ানো হয়েছে)
- ✅ Facebook
- ✅ Twitter / X
- ✅ Audio extract (MP3/M4A) — শুধু তখনই দেখানো হয় যখন সত্যিকারের আলাদা
  audio-only track পাওয়া যায় (নাহলে honestly অনুপলব্ধ দেখানো হয়, পুরো
  ভিডিও চালিয়ে দেওয়া হয় না)
- ✅ প্রতিটা resolution বাটন সত্যিই আলাদা ফাইল/quality — ডুপ্লিকেট url
  থাকলে বাদ দেওয়া হয়
- ✅ Multi-resolution (4K → 360p, উপলব্ধ থাকলে)
- ✅ Language switcher (বাংলা / English)
- ✅ Direct download (no new tab)
- ✅ Zero server bandwidth

---

## Environment Variables (Render)

| Key | Value | Required |
|-----|-------|----------|
| `RAPIDAPI_KEY` | RapidAPI key — comma-separated for multiple keys (`keyA,keyB`) | Optional (HD + TikTok photo posts only) |
| `YOUTUBE_COOKIES` | তোমার লগ-ইন করা YouTube অ্যাকাউন্টের `cookies.txt` (Netscape format) ফাইলের পুরো কনটেন্ট | Optional, কিন্তু ছাড়া YouTube প্রায়ই "Sign in to confirm you're not a bot" এরর দেবে (নিচে দেখো) |

### কেন YouTube মাঝে মাঝে/প্রায়ই কাজ করে না

Render/AWS/Heroku-এর মতো cloud সার্ভারের IP থেকে আসা রিকোয়েস্ট YouTube
এখন খুব কঠোরভাবে bot হিসেবে detect করে ফেলে — এটা yt-dlp আপডেট করলেও,
বা player client পাল্টালেও অনেক সময় পুরোপুরি ঠিক হয় না, কারণ এটা
YouTube-এর IP-reputation-ভিত্তিক ব্লক, কোনো কোড বাগ না। সবচেয়ে
নির্ভরযোগ্য সমাধান হলো তোমার নিজের (আসল, লগ-ইন করা) YouTube অ্যাকাউন্টের
cookies ব্যবহার করা:

1. Browser-এ একটা cookies export extension ইনস্টল করো (যেমন "Get
   cookies.txt LOCALLY" — Chrome/Firefox উভয়েই পাওয়া যায়)।
2. youtube.com-এ লগ-ইন করা অবস্থায় extension দিয়ে cookies export করে
   `cookies.txt` ফাইল ডাউনলোড করো।
3. সেই ফাইলের **পুরো কনটেন্ট** কপি করে Render dashboard → Environment →
   `YOUTUBE_COOKIES` নামে একটা নতুন env var বানিয়ে paste করো।
4. Redeploy করো।

⚠️ এই cookies তোমার YouTube অ্যাকাউন্টের অ্যাক্সেস দেয় — বিশ্বাসযোগ্য
জায়গা ছাড়া কারো সাথে শেয়ার কোরো না। মাঝে মাঝে (কয়েক সপ্তাহ/মাস পর)
cookies expire হয়ে গেলে আবার নতুন করে export করে বসাতে হতে পারে।

---

*© 2025 VidLink Pro — Personal use only*
