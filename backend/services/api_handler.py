"""
RapidAPI Handler — শুধু HD TikTok download-এ ব্যবহার হয়।
"""

import requests


RAPIDAPI_HOST = "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com"


def get_hd_info(url: str, api_key: str) -> dict:
    """RapidAPI দিয়ে TikTok HD video URL বের করো।"""
    headers = {
        "x-rapidapi-key":  api_key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    params = {"url": url, "hd": "1"}

    resp = requests.get(
        f"https://{RAPIDAPI_HOST}/index",
        headers=headers,
        params=params,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    video_url = (data.get("video") or [None])[0]
    audio_url = (data.get("music") or [None])[0]
    title     = data.get("title", "TikTok Video")
    cover     = data.get("cover", "")

    formats = []
    if video_url:
        formats.append({
            "label":      "HD",
            "height":     1080,
            "url":        video_url,
            "badge":      "HD",
            "badgeColor": "#3b82f6",
            "filename":   "tiktok_hd.mp4",
            "ext":        "mp4",
        })

    return {
        "title":     title,
        "thumbnail": cover,
        "duration":  None,
        "uploader":  "",
        "platform":  "tiktok",
        "formats":   formats,
        "audio_url": audio_url,
    }
