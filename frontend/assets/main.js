/* ══════════════════════════════════════════════
   VidLink Pro — main.js
   ══════════════════════════════════════════════ */

// ── Config ──────────────────────────────────────
// Frontend আর API এখন একই Render service থেকে সার্ভ হয় (InfinityFree আর
// লাগে না), তাই API_BASE খালি রেখে same-origin relative path ব্যবহার
// করা হচ্ছে — /api/info নিজে থেকেই সঠিক domain-এ যাবে।
const API_BASE = "";

// তোমার Cloudflare Worker URL এখানে দাও (video/audio proxy — এটা এখনো
// আলাদা domain-এ থাকে, কারণ CDN streaming Cloudflare-এই ফ্রি + unlimited)
const CF_WORKER = "https://little-king-7521.renakashkhan0196581.workers.dev";

// ── i18n ────────────────────────────────────────
const LANGS = {
  bn: {
    tagline: "যেকোনো Platform — একটাই বক্স",
    hero1: "যেকোনো ভিডিও",
    hero2: "সরাসরি নামাও",
    subtitle: "TikTok, Instagram, YouTube, Facebook — লিংক দাও, resolution বেছে নাও, সরাসরি নামবে।",
    placeholder: "লিংক paste করো... (যেকোনো platform)",
    fetchBtn: "Fetch করো",
    fetching: "খুঁজছি...",
    demoHint: '💡 Demo: "tiktok.com/video" লিখে দেখো',
    fetchingMsg: "ভিডিও তথ্য বের করছি...",
    foundBadge: "পাওয়া গেছে",
    resLabel: "Resolution বেছে নাও",
    audioQualityLabel: "Audio Quality বেছে নাও",
    videoTab: "ভিডিও",
    audioTab: "অডিও (MP3)",
    downloadVideo: "ভিডিও নামাও — সরাসরি",
    downloadAudio: "MP3 নামাও — সরাসরি",
    noNewTab: "🔒 কোনো নতুন ট্যাব খুলবে না · সরাসরি আপনার ডিভাইসে",
    feat1Title: "Server Bypass", feat1Desc: "Server-এ কোনো bandwidth খরচ হয় না",
    feat2Title: "No Watermark", feat2Desc: "Watermark ছাড়া ডাউনলোড",
    feat3Title: "Audio Extract", feat3Desc: "MP3/M4A বের করো যেকোনো ভিডিও থেকে",
    feat4Title: "5 Platforms", feat4Desc: "TikTok, Instagram, YouTube, Facebook, Twitter",
    telegramBot: "Telegram Bot",
    features: "Features", howItWorks: "কীভাবে কাজ করে", supported: "Supported",
    howTitle: "কীভাবে কাজ করে?",
    step1Title: "লিংক দাও", step1Desc: "যেকোনো platform-এর video লিংক paste করো",
    step2Title: "Resolution বেছে নাও", step2Desc: "4K থেকে 360p পর্যন্ত যেটা চাও",
    step3Title: "সরাসরি নামবে", step3Desc: "কোনো নতুন ট্যাব ছাড়া সরাসরি ডিভাইসে",
    footerNote: "শুধু ব্যক্তিগত ব্যবহারের জন্য",
    errorGeneric: "কিছু একটা সমস্যা হয়েছে। আবার চেষ্টা করো।",
    errorInvalid: "লিংকটি সঠিক মনে হচ্ছে না।",
    errorUnsupported: "এই platform এখনো supported নয়।",
    audioUnavailable: "এই ভিডিওর জন্য আলাদা অডিও ট্র্যাক পাওয়া যায়নি, তাই MP3 বের করা সম্ভব হচ্ছে না।",
    hdLabel: "HD (No Watermark)",
    hdResolving: "HD খোঁজা হচ্ছে...",
    hdFailed: "HD লিংক বের করা যায়নি। একটু পর আবার চেষ্টা করো।",
    tiktokDirectOpenHint: "ভিডিও নতুন ট্যাবে খুলেছে — এখন লং-প্রেস করে বা ব্রাউজারের মেনু থেকে \"Download video\" চেপে সেভ করো।",
    photoLabel: "ছবিগুলো — একেকটা আলাদাভাবে নামাও",
    photoDownload: "নামাও",
    photoDownloadAll: "সব ছবি নামাও",
  },
  en: {
    tagline: "Any Platform — One Box",
    hero1: "Download Any Video",
    hero2: "Directly to Your Device",
    subtitle: "TikTok, Instagram, YouTube, Facebook — paste a link, pick a resolution, download instantly.",
    placeholder: "Paste link here... (any platform)",
    fetchBtn: "Fetch",
    fetching: "Fetching...",
    demoHint: '💡 Demo: type "tiktok.com/video" to see it work',
    fetchingMsg: "Extracting video info...",
    foundBadge: "Found",
    resLabel: "Choose Resolution",
    audioQualityLabel: "Choose Audio Quality",
    videoTab: "Video",
    audioTab: "Audio (MP3)",
    downloadVideo: "Download Video — Direct",
    downloadAudio: "Download MP3 — Direct",
    noNewTab: "🔒 No new tab · Directly to your device",
    feat1Title: "Server Bypass", feat1Desc: "Zero bandwidth cost on server",
    feat2Title: "No Watermark", feat2Desc: "Clean watermark-free downloads",
    feat3Title: "Audio Extract", feat3Desc: "Extract MP3/M4A from any video",
    feat4Title: "5 Platforms", feat4Desc: "TikTok, Instagram, YouTube, Facebook, Twitter",
    telegramBot: "Telegram Bot",
    features: "Features", howItWorks: "How it works", supported: "Supported",
    howTitle: "How does it work?",
    step1Title: "Paste the link", step1Desc: "Paste any video link from any platform",
    step2Title: "Choose resolution", step2Desc: "4K down to 360p — you choose",
    step3Title: "Downloads directly", step3Desc: "No new tab — straight to your device",
    footerNote: "For personal use only",
    errorGeneric: "Something went wrong. Please try again.",
    errorInvalid: "This doesn't look like a valid link.",
    errorUnsupported: "This platform is not supported yet.",
    audioUnavailable: "This video has no separate audio track, so MP3 extraction isn't available.",
    hdLabel: "HD (No Watermark)",
    hdResolving: "Resolving HD...",
    hdFailed: "Couldn't get the HD link. Please try again shortly.",
    tiktokDirectOpenHint: "Video opened in a new tab — long-press it or use your browser's \"Download video\" option to save it.",
    photoLabel: "Photos — download each one separately",
    photoDownload: "Download",
    photoDownloadAll: "Download all photos",
  }
};

// ── Platform Detection ───────────────────────────
const PLATFORMS = {
  tiktok:    { name: "TikTok",      color: "#fe2c55", icon: "🎵" },
  instagram: { name: "Instagram",   color: "#e1306c", icon: "📸" },
  youtube:   { name: "YouTube",     color: "#ff0000", icon: "▶️"  },
  facebook:  { name: "Facebook",    color: "#1877f2", icon: "👍" },
  twitter:   { name: "Twitter / X", color: "#1d9bf0", icon: "🐦" },
};

function detectPlatform(url) {
  if (/tiktok\.com/i.test(url))                return "tiktok";
  if (/instagram\.com/i.test(url))             return "instagram";
  if (/youtube\.com|youtu\.be/i.test(url))     return "youtube";
  if (/facebook\.com|fb\.watch/i.test(url))    return "facebook";
  if (/twitter\.com|x\.com/i.test(url))        return "twitter";
  return null;
}

// ── State ────────────────────────────────────────
let currentLang = "bn";
let currentPlatformKey = null;
let currentFormats = [];
let selectedResIndex = 0;
let selectedAudioFmt = "320";
let currentAudioUrl = null;
let currentUrl = null;       // সর্বশেষ fetch করা URL — HD lazy resolve-এর জন্য লাগে
let isResolvingHd = false;   // HD ডাউনলোড বাটনে ডাবল-ক্লিক/রেসের বিরুদ্ধে গার্ড

// ── DOM Refs ─────────────────────────────────────
const urlInput        = document.getElementById("urlInput");
const fetchBtn        = document.getElementById("fetchBtn");
const platformTag     = document.getElementById("platformTag");
const globeIcon       = document.getElementById("globeIcon");
const inputWrap       = document.getElementById("inputWrap");
const demoHint        = document.getElementById("demoHint");
const loadingArea     = document.getElementById("loadingArea");
const errorBox        = document.getElementById("errorBox");
const errorMsg        = document.getElementById("errorMsg");
const resultArea      = document.getElementById("resultArea");
const videoThumb      = document.getElementById("videoThumb");
const platformLabel   = document.getElementById("platformLabel");
const videoTitleEl    = document.getElementById("videoTitle");
const videoDuration   = document.getElementById("videoDuration");
const videoUploader   = document.getElementById("videoUploader");
const resolutionGrid  = document.getElementById("resolutionGrid");
const downloadVideoBtn = document.getElementById("downloadVideoBtn");
const downloadVideoLabel = document.getElementById("downloadVideoLabel");
const downloadAudioBtn = document.getElementById("downloadAudioBtn");
const tabVideo        = document.getElementById("tabVideo");
const tabAudio        = document.getElementById("tabAudio");
const panelVideo      = document.getElementById("panelVideo");
const panelAudio      = document.getElementById("panelAudio");
const langBtn         = document.getElementById("langBtn");
const langDropdown    = document.getElementById("langDropdown");
const langFlag        = document.getElementById("langFlag");
const langLabel       = document.getElementById("langLabel");
const videoAudioSection = document.getElementById("videoAudioSection");
const photoSection    = document.getElementById("photoSection");
const photoGrid       = document.getElementById("photoGrid");

// ── Language ─────────────────────────────────────
function applyLang(lang) {
  currentLang = lang;
  const t = LANGS[lang];
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    if (t[key]) el.textContent = t[key];
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    if (t[key]) el.placeholder = t[key];
  });
  document.documentElement.lang = lang === "bn" ? "bn" : "en";
  // Update lang switcher display
  if (lang === "bn") { langFlag.textContent = "🇧🇩"; langLabel.textContent = "বাংলা"; }
  else               { langFlag.textContent = "🌐";  langLabel.textContent = "English"; }
  document.querySelectorAll(".lang-option").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.lang === lang);
  });
  // Update dynamic labels
  if (downloadVideoLabel && currentFormats.length) {
    const fmt = currentFormats[selectedResIndex];
    downloadVideoLabel.textContent = `${fmt.label} ${t.downloadVideo}`;
  }
}

document.querySelectorAll(".lang-option").forEach(btn => {
  btn.addEventListener("click", () => {
    applyLang(btn.dataset.lang);
    langDropdown.classList.remove("open");
  });
});

langBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  langDropdown.classList.toggle("open");
});
document.addEventListener("click", () => langDropdown.classList.remove("open"));

// ── URL Input ────────────────────────────────────
urlInput.addEventListener("input", () => {
  const url = urlInput.value.trim();
  const key = detectPlatform(url);
  currentPlatformKey = key;

  if (key) {
    const p = PLATFORMS[key];
    platformTag.textContent = `${p.icon} ${p.name}`;
    platformTag.style.cssText = `
      background:${p.color}20;
      border:1px solid ${p.color}40;
      color:${p.color};
    `;
    platformTag.classList.remove("hidden");
    globeIcon.classList.add("hidden");
    inputWrap.style.borderColor = p.color + "60";
  } else {
    platformTag.classList.add("hidden");
    globeIcon.classList.remove("hidden");
    inputWrap.style.borderColor = "";
  }

  // Reset result if URL changed
  if (!resultArea.classList.contains("hidden")) {
    resultArea.classList.add("hidden");
    errorBox.classList.add("hidden");
    demoHint.classList.remove("hidden");
  }
});

urlInput.addEventListener("keydown", e => {
  if (e.key === "Enter") fetchVideo();
});

// ── Fetch Video ──────────────────────────────────
fetchBtn.addEventListener("click", fetchVideo);

async function fetchVideo() {
  const url = urlInput.value.trim();
  const t = LANGS[currentLang];

  if (!url) return;
  if (!detectPlatform(url)) {
    showError(t.errorInvalid);
    return;
  }

  currentUrl = url;
  setState("loading");

  try {
    const resp = await fetch(`${API_BASE}/api/info`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!resp.ok) {
      const data = await resp.json().catch(() => ({}));
      throw new Error(data.error || t.errorGeneric);
    }

    const data = await resp.json();
    showResult(data);

  } catch (err) {
    showError(err.message || t.errorGeneric);
  }
}

// ── State Management ─────────────────────────────
function setState(state) {
  loadingArea.classList.add("hidden");
  errorBox.classList.add("hidden");
  resultArea.classList.add("hidden");
  demoHint.classList.add("hidden");

  if (state === "loading") {
    loadingArea.classList.remove("hidden");
    fetchBtn.disabled = true;
  } else {
    fetchBtn.disabled = false;
  }
}

function showError(msg) {
  loadingArea.classList.add("hidden");
  fetchBtn.disabled = false;
  errorMsg.textContent = msg;
  errorBox.classList.remove("hidden");
}

// ── Show Result ──────────────────────────────────
function showResult(data) {
  const t = LANGS[currentLang];
  setState("result");
  resultArea.classList.remove("hidden");

  // Thumbnail
  if (data.thumbnail) {
    videoThumb.innerHTML = `<img src="${data.thumbnail}" alt="thumbnail" onerror="this.parentElement.textContent='🎬'" />`;
  } else {
    videoThumb.textContent = currentPlatformKey ? PLATFORMS[currentPlatformKey].icon : "🎬";
  }

  // Platform label
  if (currentPlatformKey) {
    const p = PLATFORMS[currentPlatformKey];
    platformLabel.textContent = `${p.icon} ${p.name}`;
    platformLabel.style.cssText = `color:${p.color};background:${p.color}20;`;
  }

  // Title & stats
  videoTitleEl.textContent = data.title || "Video";
  videoDuration.textContent = data.duration ? `⏱ ${formatDuration(data.duration)}` : "";
  videoUploader.textContent = data.uploader ? `👤 ${data.uploader}` : "";

  // TikTok ফটো/স্লাইডশো পোস্ট — ভিডিও/অডিও ট্যাব লুকিয়ে ছবির গ্রিড দেখানো হয়
  if (data.is_photo) {
    videoAudioSection.classList.add("hidden");
    photoSection.classList.remove("hidden");
    buildPhotoGrid(data.images || []);
    return;
  }
  photoSection.classList.add("hidden");
  videoAudioSection.classList.remove("hidden");

  // Audio URL — audio_available সত্যি না হলে audio_url থাকলেও ব্যবহার
  // করা হবে না (server-side এখন honest, কিন্তু ডাবল-চেক হিসেবে রাখা হলো)
  const audioAvailable = !!data.audio_available && !!data.audio_url;
  currentAudioUrl = audioAvailable ? data.audio_url : null;
  updateAudioAvailability(audioAvailable);

  // Formats / resolutions — Normal/SD সবসময় yt-dlp থেকে আসে (ফ্রি, সাথে
  // সাথে)। TikTok-এ hd_available সত্যি হলে একটা lazy "HD (No Watermark)"
  // এন্ট্রি জুড়ে দেওয়া হয় — এটাতে ক্লিক করলেই তখন RapidAPI কল হবে।
  currentFormats = [...(data.formats || [])];
  if (data.hd_available) {
    currentFormats.push({
      label: LANGS[currentLang].hdLabel,
      badge: "HD",
      badgeColor: "#3b82f6",
      lazyHd: true,
    });
  }
  buildResolutionGrid();

  // Default to first resolution
  selectedResIndex = 0;
  updateDownloadVideoLabel();

  // Switch to video tab
  switchTab("video");
}

// ── Photo / Slideshow Grid (TikTok ছবি পোস্ট) ────
function buildPhotoGrid(images) {
  const t = LANGS[currentLang];
  photoGrid.innerHTML = "";
  images.forEach((imgUrl, i) => {
    const item = document.createElement("div");
    item.className = "photo-item";
    const img = document.createElement("img");
    img.src = imgUrl;
    img.alt = `photo-${i + 1}`;
    img.loading = "lazy";
    const btn = document.createElement("button");
    btn.className = "photo-download-btn";
    btn.textContent = `${t.photoDownload} ${i + 1}`;
    btn.addEventListener("click", () => triggerDownload(imgUrl, `tiktok_photo_${i + 1}.jpg`));
    item.appendChild(img);
    item.appendChild(btn);
    photoGrid.appendChild(item);
  });
}

// ── Audio Availability ───────────────────────────
// আগে আলাদা audio track না থাকলেও চুপচাপ পুরো ভিডিও "audio.mp3" নামে
// নেমে যেত। এখন সেই বদলে বাটন বন্ধ রেখে স্পষ্ট কারণ দেখানো হয়।
function updateAudioAvailability(available) {
  const t = LANGS[currentLang];
  downloadAudioBtn.disabled = !available;
  downloadAudioBtn.classList.toggle("disabled", !available);
  let note = panelAudio.querySelector(".audio-unavailable-note");
  if (!available) {
    if (!note) {
      note = document.createElement("p");
      note.className = "audio-unavailable-note";
      panelAudio.insertBefore(note, panelAudio.firstChild);
    }
    note.textContent = t.audioUnavailable;
  } else if (note) {
    note.remove();
  }
}

// ── Resolution Grid ──────────────────────────────
function buildResolutionGrid() {
  resolutionGrid.innerHTML = "";
  currentFormats.forEach((fmt, i) => {
    const btn = document.createElement("button");
    btn.className = "res-btn" + (i === 0 ? " active" : "");
    btn.innerHTML = fmt.label + (fmt.badge
      ? ` <span class="res-badge" style="color:${fmt.badgeColor};background:${fmt.badgeColor}25">${fmt.badge}</span>`
      : "");
    btn.addEventListener("click", () => {
      document.querySelectorAll(".res-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedResIndex = i;
      updateDownloadVideoLabel();
    });
    resolutionGrid.appendChild(btn);
  });
}

function updateDownloadVideoLabel() {
  const t = LANGS[currentLang];
  const fmt = currentFormats[selectedResIndex];
  if (fmt) downloadVideoLabel.textContent = `${fmt.label} ${t.downloadVideo}`;
}

// ── Download ─────────────────────────────────────
downloadVideoBtn.addEventListener("click", async () => {
  const t = LANGS[currentLang];
  const fmt = currentFormats[selectedResIndex];
  if (!fmt || isResolvingHd) return;

  // Normal/SD ফরম্যাটে সরাসরি yt-dlp-এর দেওয়া url থাকে — সাথে সাথে নামবে
  if (!fmt.lazyHd) {
    triggerDownload(fmt.url, fmt.filename || "video.mp4");
    return;
  }

  // HD (No Watermark) — এখন RapidAPI কল করে আসল লিংক বের করা হচ্ছে
  isResolvingHd = true;
  const originalLabel = downloadVideoLabel.textContent;
  downloadVideoLabel.textContent = t.hdResolving;
  downloadVideoBtn.classList.add("resolving");
  downloadVideoBtn.disabled = true;

  try {
    const resp = await fetch(`${API_BASE}/api/tiktok/hd`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: currentUrl }),
    });
    const result = await resp.json().catch(() => ({}));

    if (!resp.ok || !result.success || !result.hd_url) {
      showError(result.error || t.hdFailed);
      return;
    }

    triggerDownload(result.hd_url, "tiktok_hd.mp4");

    // HD resolve-এ real audio track পাওয়া গেলে audio ট্যাবও আপডেট করে দাও
    if (result.audio_available && result.audio_url) {
      currentAudioUrl = result.audio_url;
      updateAudioAvailability(true);
    }
  } catch (err) {
    showError(t.hdFailed);
  } finally {
    isResolvingHd = false;
    downloadVideoBtn.classList.remove("resolving");
    downloadVideoBtn.disabled = false;
    downloadVideoLabel.textContent = originalLabel;
  }
});

downloadAudioBtn.addEventListener("click", () => {
  const t = LANGS[currentLang];
  if (!currentAudioUrl) {
    showError(t.audioUnavailable);
    return;
  }
  triggerDownload(currentAudioUrl, "audio.mp3");
});

document.querySelectorAll(".res-btn[data-audio]").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".res-btn[data-audio]").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    selectedAudioFmt = btn.dataset.audio;
  });
});

/**
 * TikTok-এর CDN (Akamai) এখন datacenter/proxy IP (Cloudflare Worker,
 * Render সার্ভার ইত্যাদি) থেকে আসা request 403 দিয়ে ব্লক করে দেয় — signed
 * URL আসল ব্যবহারকারীর (residential/mobile) IP থেকে না আসলে reject হয়।
 * তাই TikTok video/audio/photo CDN URL Worker দিয়ে proxy না করে সরাসরি
 * ব্যবহারকারীর ব্রাউজার থেকেই নতুন ট্যাবে খোলা হয় — তখন TikTok সেটাকে
 * সাধারণ ভিউয়িং ট্র্যাফিক হিসেবেই দেখে, ব্লক করে না।
 */
function isTikTokCdnUrl(url) {
  try {
    const h = new URL(url).hostname.toLowerCase();
    return h.includes("tiktokcdn") || h.includes("tiktokv.com") ||
           h.includes("muscdn.com") || h.includes(".tiktok.com");
  } catch {
    return false;
  }
}

/**
 * triggerDownload: বেশিরভাগ platform-এর জন্য Cloudflare Worker দিয়ে সরাসরি
 * download (নতুন ট্যাব খুলবে না, সরাসরি file নামবে)। TikTok CDN-এর জন্য
 * ব্যতিক্রম — সরাসরি নতুন ট্যাবে খোলা হয় (কারণ উপরে বলা IP-block সমস্যা)।
 */
function triggerDownload(cdnUrl, filename) {
  if (isTikTokCdnUrl(cdnUrl)) {
    window.open(cdnUrl, "_blank", "noopener");
    showToast(LANGS[currentLang].tiktokDirectOpenHint);
    return;
  }

  // Cloudflare Worker URL বানাও
  const workerUrl = `${CF_WORKER}?url=${encodeURIComponent(cdnUrl)}&filename=${encodeURIComponent(filename)}`;
  // Hidden anchor → click → download
  const a = document.createElement("a");
  a.href = workerUrl;
  a.download = filename;
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function showToast(msg) {
  if (!msg) return;
  let toast = document.getElementById("vlpToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "vlpToast";
    toast.className = "vlp-toast";
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add("show");
  clearTimeout(toast._hideTimer);
  toast._hideTimer = setTimeout(() => toast.classList.remove("show"), 6000);
}

// ── Tabs ─────────────────────────────────────────
tabVideo.addEventListener("click", () => switchTab("video"));
tabAudio.addEventListener("click", () => switchTab("audio"));

function switchTab(tab) {
  tabVideo.classList.toggle("active", tab === "video");
  tabAudio.classList.toggle("active", tab === "audio");
  panelVideo.classList.toggle("hidden", tab !== "video");
  panelAudio.classList.toggle("hidden", tab !== "audio");
}

// ── Helpers ──────────────────────────────────────
function formatDuration(secs) {
  if (!secs) return "";
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

// ── Init ─────────────────────────────────────────
applyLang("bn");
