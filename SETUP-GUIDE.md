# VidLink Pro — সম্পূর্ণ Setup গাইড 🇧🇩

## এই প্রজেক্টে কী কী আছে?

```
Browser
  → Render (frontend সার্ভ করে + video URL বের করে, API)
  → Cloudflare Worker (video/audio stream করে, bandwidth ফ্রি)
```

শুধু ২টা জায়গায় deploy করলেই হয় — **InfinityFree আর লাগে না।** Render
এখন frontend (ওয়েবসাইট) আর backend (API) দুটোই একসাথে সার্ভ করে।

---

## ⏳ Step by Step

---

### STEP 1: Render-এ Deploy করো (frontend + backend একসাথে)

1. GitHub repo push করা থাকলে https://render.com → **New → Blueprint**
   (অথবা New Web Service) → repo connect করো
2. `render.yaml` আছে বলে Render নিজে থেকেই root directory (`backend`),
   build/start command detect করবে
3. Environment Variables-এ যোগ করো:
   - `RAPIDAPI_KEY` = তোমার RapidAPI key (TikTok HD + আসল audio track-এর
     জন্য দরকার — না দিলেও চলবে, তখন yt-dlp দিয়ে fallback হবে)
4. Deploy করো → URL পাবে, যেমন: `https://vidlink-pro.onrender.com`
5. এই একই URL খুললেই পুরো ওয়েবসাইট দেখা যাবে

---

### STEP 2: Cloudflare Video Proxy Worker বানাও

**কেন দরকার:** এটা ছাড়া video/audio সরাসরি ডিভাইসে download হবে না
(অনেক CDN ব্রাউজার থেকে সরাসরি request block করে দেয়, Worker সেটা proxy
করে সঠিক headers দিয়ে পাঠায়)।

1. https://dash.cloudflare.com → Workers & Pages → **Create application**
2. **"Start with Hello World!"** ট্যাপ করো
3. নাম যা দেয় রাখো → **"Deploy"** ট্যাপ করো
4. Deploy হলে → **"Edit code"** বাটনে ট্যাপ করো
5. Editor-এ সব code মুছে `cloudflare-worker/worker.js` এর নতুন content
   paste করো, তারপর **"Deploy"**
6. তোমার Worker URL note করো (যেমন: `https://little-king-7521....workers.dev`)

---

### STEP 3: main.js-এ Worker URL দাও

`frontend/assets/main.js`-এ:

```js
const API_BASE  = "";   // ✅ same-origin — কিছু বদলাতে হবে না
const CF_WORKER = "https://xxxxx.workers.dev"; // ← তোমার Worker URL দাও
```

(GitHub push করে দিলে Render নিজে থেকেই redeploy করে নেবে, autoDeploy
চালু আছে।)

---

### STEP 4 (ঐচ্ছিক): নিজের ডোমেইন বসানো

Render dashboard → Settings → **Custom Domain** → নিজের কেনা ডোমেইন যোগ
করো এবং তোমার domain provider-এ CNAME/A record বসাও (Render এই ধাপে
সঠিক value দেখিয়ে দেবে)। যোগ হয়ে গেলে পুরো সাইট (frontend + API) সেই
ডোমেইন থেকেই চলবে — কোথাও কোনো কনফিগ বদলাতে হবে না, কারণ CORS/Worker
origin আগে থেকেই খোলা রাখা হয়েছে।

---

### STEP 5: Test করো

1. তোমার Render URL (বা বসানো custom domain) খোলো
2. TikTok/YouTube/Facebook যেকোনো লিংক paste করো
3. Resolution বেছে Download করো, তারপর Audio ট্যাবেও চেক করো

---

## 🔧 কোনো সমস্যা হলে

| সমস্যা | সমাধান |
|--------|---------|
| "ভিডিও তথ্য বের করতে পারিনি" দেখাচ্ছে | লিংকটা সঠিক platform-এর কিনা, এবং ভিডিওটা public কিনা দেখো |
| Download শুরু হচ্ছে না | CF_WORKER URL ঠিক আছে কিনা, আর Worker deploy হয়েছে কিনা চেক করো |
| Audio বাটন বন্ধ দেখাচ্ছে | এই ভিডিওতে সত্যিকারের আলাদা audio track নেই (TikTok/Facebook-এর অনেক ভিডিওতেই এটা স্বাভাবিক) — RAPIDAPI_KEY দিলে TikTok-এর জন্য কাজ করবে |
| Render slow | প্রথমবার ৩০ সেকেন্ড লাগে (free plan spin-up) |

---

## 📁 File Structure

```
vidlink-pro/
├── frontend/
│   ├── index.html          ← Website UI (Render থেকেই সার্ভ হয়)
│   └── assets/
│       ├── style.css       ← Design
│       └── main.js         ← Logic (CF_WORKER এখানে)
├── backend/
│   ├── app.py              ← Flask API + frontend সার্ভিং (Render-এ চলছে)
│   ├── render.yaml         ← Render deploy config
│   ├── requirements.txt
│   └── services/
│       ├── ytdlp_handler.py
│       └── api_handler.py
├── cloudflare-worker/
│   └── worker.js           ← Video/audio proxy (Cloudflare Worker-এ দিতে হবে)
└── SETUP-GUIDE.md          ← এই গাইড
```

