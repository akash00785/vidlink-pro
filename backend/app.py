"""
VidLink Pro — Flask Backend (Render)
=====================================
শুধু URL extraction করে। Video কখনো এই server দিয়ে যায় না।
Bandwidth খরচ: শুধু JSON response (~2KB per request)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from services.ytdlp_handler import get_video_info
from services.api_handler import get_hd_info

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
        "audio_available": bool
    }

    TikTok URL হলে, RAPIDAPI_KEY সেট করা থাকলে RapidAPI দিয়ে watermark-free
    HD ভিডিও + আসল আলাদা audio track আনার চেষ্টা করা হয় (বেশি reliable —
    yt-dlp-এর তুলনায় TikTok CDN 403 কম দেয়)। না থাকলে/fail করলে yt-dlp
    দিয়ে fallback করে।
    """
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "URL দাও"}), 400

    rapidapi_key = os.environ.get("RAPIDAPI_KEY", "") or None

    try:
        info = get_video_info(url, rapidapi_key=rapidapi_key)
        return jsonify(info)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Info error: {e}")
        return jsonify({"error": "ভিডিও তথ্য বের করতে পারিনি। লিংকটি সঠিক কিনা দেখো।"}), 500


# ── HD Download Info (RapidAPI) ───────────────────────
@app.route("/api/hd-info", methods=["POST"])
def hd_info():
    """
    RapidAPI দিয়ে HD quality URL বের করে।
    Body: { "url": "https://..." }
    """
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "URL দাও"}), 400

    rapidapi_key = os.environ.get("RAPIDAPI_KEY", "")
    if not rapidapi_key:
        return jsonify({"error": "HD service unavailable"}), 503

    try:
        info = get_hd_info(url, rapidapi_key)
        return jsonify(info)
    except Exception as e:
        app.logger.error(f"HD info error: {e}")
        return jsonify({"error": "HD info বের করা যায়নি।"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
