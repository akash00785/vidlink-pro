"""
VidLink Pro — Flask Backend (Render)
=====================================
শুধু URL extraction করে। Video কখনো এই server দিয়ে যায় না।
Bandwidth খরচ: শুধু JSON response (~2KB per request)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from services.ytdlp_handler import get_video_info, detect_platform
from services.api_handler import resolve_tiktok_hd

# ── Frontend এখন এই একই Render service থেকে সার্ভ হয় ──
# আগে InfinityFree-তে আলাদাভাবে হোস্ট করতে হতো; এখন আর দরকার নেই।
# backend/app.py-এর পাশের frontend/ ফোল্ডারটাই সরাসরি সার্ভ করা হচ্ছে।
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(
    __name__,
    static_folder=os.path.join(FRONTEND_DIR, "assets"),
    static_url_path="/assets",
)

# ── CORS: এটা শুধু একটা read-only video-info API (কোনো cookie/session লাগে
# না), তাই origin খোলা রাখা হয়েছে — future-এ custom domain বসালেও নতুন করে
# CORS ঠিক করতে হবে না। ──
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)


# ── Frontend পরিবেশন করো ──────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# ── Health Check (Render health check + uptime pings) ──
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "VidLink Pro API"})


# ── Main API: Video Info ──────────────────────────────
@app.route("/api/info", methods=["POST"])
def video_info():
    """
    Body: { "url": "https://..." }
    Returns: {
        "title": str,
        "thumbnail": str,
        "duration": int (seconds),
        "uploader": str,
        "platform": str,
        "formats": [
            { "label": "1080p", "url": str, "badge": "HD", "badgeColor": "#3b82f6", "filename": str }
        ],
        "audio_url": str,
        "audio_available": bool,
        # TikTok ভিডিও পোস্টের জন্য অতিরিক্ত:
        "hd_available": bool,   # true হলে ফ্রন্টএন্ড /api/tiktok/hd কল করে HD resolve করতে পারবে
        # TikTok ফটো/স্লাইডশো পোস্টের জন্য অতিরিক্ত:
        "is_photo": bool,
        "images": [str, ...],
    }

    TikTok ভিডিও পোস্ট: Normal/SD সবসময় ফ্রি yt-dlp দিয়ে সাথে সাথেই আসে।
    RAPIDAPI_KEY কনফিগার করা থাকলে "hd_available": true পাঠানো হয়, কিন্তু
    RapidAPI এখানে কল হয় না — ব্যবহারকারী HD বাটনে ক্লিক করলে /api/tiktok/hd
    দিয়ে lazy resolve হয় (কোটা বাঁচাতে)।
    TikTok ফটো/স্লাইডশো পোস্ট (URL-এ '/photo/'): yt-dlp এগুলো বের করতে
    পারে না, তাই সরাসরি RapidAPI দিয়ে "images" লিস্ট ফেরত দেওয়া হয়।
    """
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "URL দাও"}), 400

    try:
        info = get_video_info(url)
        return jsonify(info)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Info error: {e}")
        return jsonify({"error": "ভিডিও তথ্য বের করতে পারিনি। লিংকটি সঠিক কিনা দেখো।"}), 500


# ── TikTok HD Resolve (RapidAPI, lazy) ────────────────
@app.route("/api/tiktok/hd", methods=["POST"])
def tiktok_hd_resolve():
    """
    ব্যবহারকারী "HD (No Watermark)" ডাউনলোড বাটনে ক্লিক করলে তখনই ডাকা হয়।
    /api/info-এ RapidAPI কল হয় না (শুধু প্রিভিউ দেখা visitor-দের কোটা
    খরচ না করাতে) — আসল RapidAPI কল এখানেই হয়, key rotation + ক্যাশ-সহ।
    Body: { "url": "https://..." }
    """
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url or detect_platform(url) != "tiktok":
        return jsonify({"success": False, "error": "সঠিক TikTok URL দাও।"}), 400

    result = resolve_tiktok_hd(url)
    status = 200 if result.get("success") else 400
    return jsonify(result), status


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
