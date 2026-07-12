"""
VidLink Pro — Flask Backend (Render)
=====================================
শুধু URL extraction করে। Video কখনো এই server দিয়ে যায় না।
Bandwidth খরচ: শুধু JSON response (~2KB per request)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from services.ytdlp_handler import get_video_info
from services.api_handler import get_hd_info

app = Flask(__name__)

# ── CORS: শুধু তোমার domain থেকে request allow করো ──
ALLOWED_ORIGINS = [
    "https://vidlink.10001mb.com",
    "http://vidlink.10001mb.com",
    "https://vidlink-pro.renakashkhan0196581.workers.dev",
    "http://localhost",
    "http://127.0.0.1",
]
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=False)


# ── Health Check ──────────────────────────────────────
@app.route("/", methods=["GET"])
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
        "audio_url": str
    }
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
