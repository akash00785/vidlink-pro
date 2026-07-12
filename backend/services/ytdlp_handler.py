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
    yt-dlp দিয়ে video info + CDN URLs বের করে।
    ফাইল download হয় না — শুধু JSON info।
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,          # ← কোনো download নেই
        "extract_flat": False,
        # YouTube bot-block bypass: Android client ব্যবহার করো
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
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

    platform = detect_platform(url)
    title = info.get("title", "Video")
    thumbnail = info.get("thumbnail") or _pick_thumbnail(info)
    duration = info.get("duration")
    uploader = info.get("uploader") or info.get("channel") or ""

    # Format list বানাও
    formats = _build_formats(info, platform)
    audio_url = _get_audio_url(info)

    return {
        "title":     title,
        "thumbnail": thumbnail,
        "duration":  int(duration) if duration else None,
        "uploader":  uploader,
        "platform":  platform,
        "formats":   formats,
        "audio_url": audio_url,
    }


def _pick_thumbnail(info: dict) -> str | None:
    thumbs = info.get("thumbnails") or []
    if thumbs:
        return thumbs[-1].get("url")
    return None


def _build_formats(info: dict, platform: str) -> list:
    """Available video formats বের করো, highest quality আগে।"""
    raw_formats = info.get("formats") or []
    seen_heights = set()
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
        if not h or h in seen_heights:
            continue
        seen_heights.add(h)

        url = f.get("url")
        if not url:
            continue

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
    """Audio-only URL বের করো।"""
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

    # Fallback: video format থেকে audio নাও
    if info.get("url"):
        return info["url"]

    return None
