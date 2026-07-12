"""
yt-dlp handler — শুধু URL extract করে, video download করে না।
"""

import yt_dlp
import re


# Quality label → badge mapping
QUALITY_BADGES = {
    "2160": ("ULTRA", "#a855f7"),
    "1440": ("2K",    "#8b5cf6"),
    "1080": ("HD",    "#3b82f6"),
    "720":  ("HD",    "#3b82f6"),
    "480":  ("",      ""),
    "360":  ("",      ""),
    "240":  ("",      ""),
    "144":  ("",      ""),
}

def detect_platform(url: str) -> str:
    url_lower = url.lower()
    if "tiktok.com"  in url_lower: return "tiktok"
    if "instagram.com" in url_lower: return "instagram"
    if "youtube.com" in url_lower or "youtu.be" in url_lower: return "youtube"
    if "facebook.com" in url_lower or "fb.watch" in url_lower: return "facebook"
    if "twitter.com" in url_lower or "x.com" in url_lower: return "twitter"
    return "unknown"


def get_video_info(url: str) -> dict:
    """
    Video info + CDN URLs বের করে।
    ফাইল download হয় না — শুধু JSON info।

    TikTok আলাদাভাবে হ্যান্ডল করা হয় (দেখুন _handle_tiktok) — Normal/SD
    সবসময় ফ্রি yt-dlp দিয়ে সাথে সাথে, HD RapidAPI দিয়ে lazy (ক্লিক করলে
    তখনই resolve হয়), আর ফটো/স্লাইডশো পোস্টের জন্য RapidAPI ছাড়া উপায় নেই।
    """
    platform = detect_platform(url)

    if platform == "tiktok":
        return _handle_tiktok(url)

    return _extract_with_ytdlp(url, platform)


def _looks_like_tiktok_photo(url: str) -> bool:
    """TikTok ফটো/স্লাইডশো পোস্টের URL-এ '/photo/' থাকে (ভিডিওতে '/video/')।
    শুধু vm/vt.tiktok.com শর্ট লিংকে এটা বলা যায় না — সেগুলো ভিডিও হিসেবেই
    try করা হয়, ব্যর্থ হলে ব্যবহারকারী পূর্ণ লিংক দিলে ধরা পড়বে।"""
    return "/photo/" in (url or "").lower()


def _handle_tiktok(url: str) -> dict:
    from .api_handler import has_rapidapi_key, resolve_tiktok_photo

    if _looks_like_tiktok_photo(url):
        if not has_rapidapi_key():
            raise ValueError(
                "এই ফটো/স্লাইডশো পোস্টের জন্য HD সার্ভিস কনফিগার করা নেই "
                "(RAPIDAPI_KEY লাগবে) — yt-dlp দিয়ে TikTok-এর ছবি পোস্ট বের করা যায় না।"
            )
        result = resolve_tiktok_photo(url)
        if not result.get("success"):
            raise ValueError(result.get("error") or "ছবিগুলো বের করা যায়নি।")
        return {
            "title":           result.get("title"),
            "thumbnail":       result.get("thumbnail"),
            "duration":        None,
            "uploader":        "",
            "platform":        "tiktok",
            "is_photo":        True,
            "images":          result.get("images", []),
            "formats":         [],
            "audio_url":       result.get("audio_url"),
            "audio_available": result.get("audio_available", False),
        }

    # সাধারণ TikTok ভিডিও পোস্ট: Normal/SD সবসময় yt-dlp দিয়ে সাথে সাথেই
    # ফেরত দেওয়া হয় (ফ্রি, কোনো API key লাগে না)। RAPIDAPI_KEY কনফিগার
    # করা থাকলে "hd_available: true" পাঠানো হয় — কিন্তু RapidAPI কল এখানে
    # হয় না, ব্যবহারকারী সত্যিই HD বাটনে ক্লিক করলে তখন /api/tiktok/hd
    # দিয়ে resolve হবে (কোটা বাঁচাতে)।
    info = _extract_with_ytdlp(url, "tiktok")
    info["is_photo"] = False
    info["images"] = []
    info["hd_available"] = has_rapidapi_key()
    return info


def _extract_with_ytdlp(url: str, platform: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,          # ← কোনো download নেই
        "extract_flat": False,
        # YouTube bot-block bypass: android/tv client দিয়ে আগে try করো —
        # এগুলো সাধারণত "Sign in to confirm you're not a bot" চাওয়ার
        # আগেই সফল হয়। "web" শেষে রাখা হয়েছে শুধু fallback হিসেবে, কারণ
        # web client ব্যর্থ হলেই এই cookie-চাওয়া error দেখায়।
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "tv", "web"],
                "skip": ["dash", "translated_subs"],
            }
        },
        "http_headers": {
            "User-Agent": "com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip",
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            raise ValueError(f"yt-dlp error: {e}")

    if not info:
        raise ValueError("ভিডিও তথ্য পাওয়া যায়নি।")

    title = info.get("title", "Video")
    thumbnail = info.get("thumbnail") or _pick_thumbnail(info)
    duration = info.get("duration")
    uploader = info.get("uploader") or info.get("channel") or ""

    # Format list বানাও
    formats = _build_formats(info, platform)
    audio_url = _get_audio_url(info)

    return {
        "title":          title,
        "thumbnail":      thumbnail,
        "duration":       int(duration) if duration else None,
        "uploader":       uploader,
        "platform":       platform,
        "formats":        formats,
        "audio_url":      audio_url,
        # সত্যিকারের আলাদা audio-only stream পাওয়া গেলে তবেই True —
        # নাহলে audio বাটনে চাপলে আসলে পুরো ভিডিও নেমে যেত (আগের বাগ)।
        "audio_available": audio_url is not None,
    }


def _pick_thumbnail(info: dict) -> str | None:
    thumbs = info.get("thumbnails") or []
    if thumbs:
        return thumbs[-1].get("url")
    return None


def _build_formats(info: dict, platform: str) -> list:
    """Available video formats বের করো, highest quality আগে।

    দুইটা জিনিস দিয়ে duplicate বাদ দেওয়া হয়: height AND url।
    শুধু height দিয়ে dedup করলে TikTok/Facebook-এর মতো platform-এ
    কখনো কখনো ভিন্ন height লেবেল হওয়া সত্ত্বেও আসলে একই underlying
    CDN url থেকে যায় — ফলে "HD" আর normal বাটনে চাপলে একই ভিডিও নামে।
    এখন একই url দ্বিতীয়বার দেখা গেলে সেটা বাদ দেওয়া হয়, তাই স্ক্রিনে
    যে কয়টা বাটন দেখা যাবে, প্রতিটা সত্যিই আলাদা resolution/ফাইল হবে।
    """
    raw_formats = info.get("formats") or []
    seen_heights = set()
    seen_urls = set()
    result = []

    # Height অনুযায়ী sort (descending)
    video_fmts = [
        f for f in raw_formats
        if f.get("vcodec") not in (None, "none")
        and f.get("height")
    ]
    video_fmts.sort(key=lambda f: f.get("height", 0), reverse=True)

    for f in video_fmts:
        h = f.get("height")
        url = f.get("url")
        if not h or not url:
            continue
        if h in seen_heights or url in seen_urls:
            continue
        seen_heights.add(h)
        seen_urls.add(url)

        h_str = str(h)
        label = f"{h}p"
        badge, badge_color = QUALITY_BADGES.get(h_str, ("", ""))

        ext = f.get("ext") or "mp4"
        safe_title = re.sub(r'[^\w\-]', '_', info.get("title", "video"))[:40]
        filename = f"{safe_title}_{label}.{ext}"

        result.append({
            "label":      label,
            "height":     h,
            "url":        url,
            "badge":      badge,
            "badgeColor": badge_color,
            "filename":   filename,
            "ext":        ext,
        })

        if len(result) >= 6:
            break

    # Fallback: যদি কোনো format না পাওয়া যায়
    if not result:
        best = info.get("url")
        if best:
            result.append({
                "label": "Best",
                "height": 0,
                "url": best,
                "badge": "",
                "badgeColor": "",
                "filename": "video.mp4",
                "ext": "mp4",
            })

    return result


def _get_audio_url(info: dict) -> str | None:
    """সত্যিকারের audio-only URL বের করো (যদি থাকে)।

    আগে এখানে কোনো আলাদা audio-only stream না পেলে পুরো video URL-ই
    fallback হিসেবে ফেরত দেওয়া হতো — তার ফলে "MP3 নামাও" বাটনে চাপলে
    আসলে পুরো ভিডিও ফাইল নেমে যেত (নাম শুধু audio.mp3)। TikTok/Facebook-এর
    মতো platform-এ সাধারণত video+audio একসাথে মেশানো থাকে, আলাদা
    audio track থাকে না — তাই এখন সেক্ষেত্রে honestly None রিটার্ন করা হয়
    এবং frontend audio ডাউনলোড বাটন বন্ধ রাখে/স্পষ্ট মেসেজ দেখায়।
    """
    raw_formats = info.get("formats") or []
    audio_fmts = [
        f for f in raw_formats
        if f.get("acodec") not in (None, "none")
        and f.get("vcodec") in (None, "none")
        and f.get("url")
    ]
    if audio_fmts:
        # Best audio (highest abr)
        audio_fmts.sort(key=lambda f: f.get("abr") or 0, reverse=True)
        return audio_fmts[0].get("url")

    return None
