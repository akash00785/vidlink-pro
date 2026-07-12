"""
RapidAPI Handler — TikTok HD (watermark-free) ভিডিও, আসল আলাদা audio/music
track, এবং ফটো/স্লাইডশো পোস্টের ছবিগুলো আনার জন্য ব্যবহার হয়।

Normal/SD ভিডিও কোয়ালিটি এর উপর নির্ভর করে না — সেটা সবসময় yt-dlp দিয়ে হয়
(দেখুন ytdlp_handler.py), যাতে RAPIDAPI_KEY না থাকলে বা exhausted হয়ে
গেলেও Normal Download কাজ করে।
"""
import os
import logging

import requests

from services.key_manager import KeyManager
from services import rapidapi_cache

RAPIDAPI_HOST = "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com"
TIMEOUT = 15

# RAPIDAPI_KEY-তে কমা দিয়ে একাধিক key দেওয়া যায় (দেখুন key_manager.py)
key_manager = KeyManager(os.environ.get("RAPIDAPI_KEY", ""))


def has_rapidapi_key() -> bool:
    return key_manager.has_keys()


def _call_rapidapi(url: str) -> dict:
    """
    RapidAPI-কে raw কল করে। একটা key rate-limit (429) দিলে অটো পরের
    key-তে সুইচ করে, সব key ব্যর্থ না হওয়া পর্যন্ত চেষ্টা করে।
    """
    if not key_manager.has_keys():
        raise RuntimeError("RAPIDAPI_KEY সেট করা নেই।")

    last_error = None
    tried = set()

    for _ in range(len(key_manager.keys)):
        api_key = key_manager.get_active_key()
        if not api_key or api_key in tried:
            break
        tried.add(api_key)

        headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": RAPIDAPI_HOST}
        params = {"url": url, "hd": "1"}

        try:
            resp = requests.get(
                f"https://{RAPIDAPI_HOST}/index",
                headers=headers,
                params=params,
                timeout=TIMEOUT,
            )
        except requests.RequestException as e:
            logging.warning(f"RapidAPI request error, trying next key if any: {e}")
            last_error = e
            continue

        if resp.status_code == 429:
            logging.warning("RapidAPI key rate-limited (429) — rotating to next key.")
            key_manager.mark_rate_limited(api_key)
            continue

        if resp.status_code != 200:
            logging.error(f"RapidAPI returned status {resp.status_code}")
            last_error = RuntimeError(f"RapidAPI status {resp.status_code}")
            continue

        try:
            return resp.json()
        except ValueError:
            logging.error("RapidAPI returned non-JSON response.")
            last_error = RuntimeError("RapidAPI non-JSON response")
            continue

    raise last_error or RuntimeError("সব RapidAPI key ব্যর্থ/exhausted।")


def _extract_images(data: dict) -> list:
    """ভিন্ন ভিন্ন RapidAPI provider ছবি/স্লাইডশো ভিন্ন key-নামে দেয়,
    তাই common সবগুলো নাম try করা হচ্ছে।"""
    for key in ("images", "image_urls", "imagesList", "slideshow_images", "photo_urls"):
        val = data.get(key)
        if val:
            return list(val)
    return []


def resolve_tiktok_hd(url: str) -> dict:
    """
    ব্যবহারকারী "HD (No Watermark)" ডাউনলোড বাটনে ক্লিক করলে তখনই ডাকা
    হয় (lazy) — শুধু প্রিভিউ দেখা visitor-দের জন্য RapidAPI কোটা খরচ হয়
    না। একই লিংকের বারবার আসা রিকোয়েস্টে ক্যাশ থেকে উত্তর দেওয়া হয়।

    Returns: {'success': True, 'hd_url', 'audio_url', 'audio_available', ...}
             বা {'success': False, 'error': str}
    """
    cached = rapidapi_cache.get_cached(f"hd:{url}")
    if cached is not None:
        return cached

    try:
        data = _call_rapidapi(url)
    except Exception as e:
        logging.error(f"resolve_tiktok_hd failed: {e}")
        return {"success": False, "error": "HD লিংক বের করা যায়নি। একটু পর আবার চেষ্টা করো।"}

    video_url = (data.get("video") or [None])[0]
    audio_url = (data.get("music") or [None])[0]  # TikTok-এর আসল আলাদা audio/music track

    if not video_url:
        return {"success": False, "error": "এই ভিডিওর জন্য HD লিংক পাওয়া যায়নি।"}

    result = {
        "success":         True,
        "hd_url":          video_url,
        "audio_url":       audio_url,
        "audio_available": audio_url is not None,
        "title":           data.get("title") or "TikTok Video",
        "thumbnail":       data.get("cover", ""),
    }
    rapidapi_cache.set_cached(f"hd:{url}", result)
    return result


def resolve_tiktok_photo(url: str) -> dict:
    """
    TikTok ফটো/স্লাইডশো পোস্টের জন্য — yt-dlp এগুলোর ছবি বের করতে পারে
    না, তাই RapidAPI ছাড়া উপায় নেই। প্রিভিউ দেখানোর জন্যই ছবিগুলো লাগে,
    তাই এটা lazy করা সম্ভব না (resolve_tiktok_hd-এর মতো ক্লিকের অপেক্ষা
    করা যায় না) — তবে একই ভিডিও/পোস্ট লিংকের জন্য ক্যাশ থেকে উত্তর হয়।
    """
    cached = rapidapi_cache.get_cached(f"photo:{url}")
    if cached is not None:
        return cached

    try:
        data = _call_rapidapi(url)
    except Exception as e:
        logging.error(f"resolve_tiktok_photo failed: {e}")
        return {"success": False, "error": "ছবিগুলো বের করা যায়নি। একটু পর আবার চেষ্টা করো।"}

    images = _extract_images(data)
    if not images:
        return {"success": False, "error": "এই পোস্টে কোনো ছবি পাওয়া যায়নি।"}

    audio_url = (data.get("music") or [None])[0]

    result = {
        "success":         True,
        "is_photo":        True,
        "images":          images,
        "audio_url":       audio_url,
        "audio_available": audio_url is not None,
        "title":           data.get("title") or "TikTok Photos",
        "thumbnail":       data.get("cover") or images[0],
    }
    rapidapi_cache.set_cached(f"photo:{url}", result)
    return result
