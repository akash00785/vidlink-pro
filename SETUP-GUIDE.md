# VidLink Pro — সম্পূর্ণ Setup গাইড 🇧🇩

## এই প্রজেক্টে কী কী আছে?

```
Browser (তোমার website) 
  → Render (শুধু video URL বের করে)
  → Cloudflare Worker (video stream করে, bandwidth ফ্রি)
```

---

## ✅ কী কী হয়ে গেছে

- [x] GitHub repo তৈরি: https://github.com/akash00785/vidlink-pro
- [x] Render backend deploy: https://vidlink-pro.onrender.com
- [x] Frontend Cloudflare-এ: https://vidlink-pro.renakashkhan0196581.workers.dev

---

## ⏳ এখন যা করতে হবে — Step by Step

---

### STEP 1: Cloudflare Video Proxy Worker বানাও

**কেন দরকার:** এটা ছাড়া video download হবে না।

1. https://dash.cloudflare.com → Workers & Pages → **Create application**
2. **"Start with Hello World!"** ট্যাপ করো
3. নাম যা দেয় রাখো (যেমন: `little-king-7521`) → **"Deploy"** ট্যাপ করো
4. Deploy হলে → **"Edit code"** বাটনে ট্যাপ করো
5. Editor-এ সব code মুছে নিচের URL থেকে code copy-paste করো:

```
https://raw.githubusercontent.com/akash00785/vidlink-pro/main/cloudflare-worker/worker.js
```

6. Paste করার পর → **"Deploy"** বাটন ট্যাপ করো
7. তোমার Worker URL দেখাবে, যেমন:
   ```
   https://little-king-7521.renakashkhan0196581.workers.dev
   ```
8. এই URL টা note করো

---

### STEP 2: main.js আপডেট করো

`frontend/assets/main.js` এর ৫ ও ৯ নম্বর লাইন:

```js
const API_BASE  = "https://vidlink-pro.onrender.com";   // ✅ হয়ে গেছে
const CF_WORKER = "https://little-king-7521.renakashkhan0196581.workers.dev"; // ← তোমার Worker URL দাও
```

**সহজ পদ্ধতি:** Replit Agent-কে Worker URL পাঠাও, সে নিজেই GitHub-এ push করে দেবে।

---

### STEP 3: Website Access করো

Frontend এখন live আছে দুই জায়গায়:

**Cloudflare (রেকমেন্ডেড):**
```
https://vidlink-pro.renakashkhan0196581.workers.dev
```

**InfinityFree (optional):**
- GitHub থেকে `frontend/` folder download করো
- InfinityFree cPanel → File Manager → htdocs/ এ upload করো
- তারপর: https://vidlink.10001mb.com

---

### STEP 4: Test করো

1. https://vidlink-pro.renakashkhan0196581.workers.dev খোলো
2. যেকোনো YouTube/TikTok link paste করো
3. Resolution বেছে Download করো

---

## 🔧 কোনো সমস্যা হলে

| সমস্যা | সমাধান |
|--------|---------|
| "API error" দেখাচ্ছে | Render URL ঠিক আছে কিনা চেক করো |
| Download হচ্ছে না | CF_WORKER URL ঠিক আছে কিনা চেক করো |
| Render slow | প্রথমবার ৩০ সেকেন্ড লাগে (free plan spin-up) |

---

## 📁 File Structure

```
vidlink-pro/
├── frontend/
│   ├── index.html          ← Website UI
│   └── assets/
│       ├── style.css       ← Design
│       └── main.js         ← Logic (API_BASE ও CF_WORKER এখানে)
├── backend/
│   ├── app.py              ← Flask API (Render-এ চলছে)
│   └── requirements.txt
├── cloudflare-worker/
│   └── worker.js           ← Video proxy (Cloudflare Worker-এ দিতে হবে)
└── SETUP-GUIDE.md          ← এই গাইড
```

---

## 🌐 সব URL একজায়গায়

| সার্ভিস | URL |
|---------|-----|
| GitHub | https://github.com/akash00785/vidlink-pro |
| Render API | https://vidlink-pro.onrender.com |
| Website | https://vidlink-pro.renakashkhan0196581.workers.dev |
| Video Proxy | (STEP 1 করার পর পাবে) |

