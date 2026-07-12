/**
 * VidLink Pro — Cloudflare Worker
 * ================================
 * কাজ: CDN URL থেকে video/audio pipe করে browser-এ পাঠায়।
 * Video এখানে জমা হয় না — সরাসরি stream হয়।
 * Bandwidth: Cloudflare-এর (ফ্রি, unlimited)
 *
 * Deploy: https://dash.cloudflare.com → Workers → Create Worker
 * এই পুরো file paste করো, তারপর Deploy করো।
 */

// এই Worker শুধু CDN থেকে ফাইল pipe করে ব্রাউজারে পাঠায় — কোনো cookie/session
// ব্যবহার হয় না, তাই origin খোলা রাখা হয়েছে (Render-এ custom domain বসালেও
// এখানে কিছু বদলাতে হবে না)।
const ALLOWED_ORIGIN = "*";

export default {
  async fetch(request) {
    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: corsHeaders(),
      });
    }

    if (request.method !== "GET") {
      return new Response("Only GET allowed", { status: 405, headers: corsHeaders() });
    }

    const url = new URL(request.url);
    const targetUrl = url.searchParams.get("url");
    const filename  = url.searchParams.get("filename") || "video.mp4";

    if (!targetUrl) {
      return new Response("Missing ?url= parameter", { status: 400, headers: corsHeaders() });
    }

    // URL validation
    let parsed;
    try {
      parsed = new URL(targetUrl);
    } catch {
      return new Response("Invalid URL", { status: 400, headers: corsHeaders() });
    }

    // শুধু known CDN domains allow করো (security)
    // TikTok অনেক আলাদা আলাদা CDN hostname ব্যবহার করে (v16/v19/v77/vXX-webapp,
    // p16-sign-*, muscdn.com ইত্যাদি) — আগে শুধু ৩টা নির্দিষ্ট hostname ছিল
    // বলে বাকি TikTok CDN host গুলো "Unrecognized" হয়ে যেত। এখন generic
    // "tiktok"/"tiktokcdn"/"muscdn" প্যাটার্নে match করা হচ্ছে।
    const allowedHosts = [
      "tiktokcdn",
      "tiktokv.com",
      "muscdn.com",
      ".tiktok.com",
      "scontent.cdninstagram.com",
      "cdninstagram.com",
      "scontent-",
      "googlevideo.com",
      "youtube.com",
      "ytimg.com",
      "fbcdn.net",
      "video.twimg.com",
      "pbs.twimg.com",
    ];

    const hostOk = allowedHosts.some(h => parsed.hostname.includes(h));
    if (!hostOk) {
      // Log করো কিন্তু block করো না — অন্য CDN হতে পারে
      console.warn("Unrecognized CDN host:", parsed.hostname);
    }

    try {
      // CDN থেকে fetch করো — প্রতিটা platform তার নিজের Referer আশা করে।
      // আগে সবসময় TikTok-এর Referer পাঠানো হতো, তাই অন্য platform-এর
      // (Facebook/Instagram/YouTube) CDN মাঝে মাঝে ভুল Referer দেখে
      // request প্রত্যাখ্যান করতে পারত।
      const fetchHeaders = {
        // Browser-এর মতো দেখাও CDN-কে
        "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept":          "*/*",
        "Accept-Encoding": "identity",
        "Range":           request.headers.get("Range") || "bytes=0-",
      };
      const referer = refererFor(parsed.hostname);
      if (referer) fetchHeaders["Referer"] = referer;

      const cdnResp = await fetch(targetUrl, {
        headers: fetchHeaders,
        redirect: "follow",
      });

      if (!cdnResp.ok && cdnResp.status !== 206) {
        return new Response(`CDN error: ${cdnResp.status}`, {
          status: cdnResp.status,
          headers: corsHeaders(),
        });
      }

      // Content type বের করো
      const contentType = cdnResp.headers.get("content-type") || guessContentType(filename);
      const contentLength = cdnResp.headers.get("content-length");

      // Response headers বানাও
      const headers = {
        ...corsHeaders(),
        "Content-Type":        contentType,
        "Content-Disposition": `attachment; filename="${encodeURIComponent(filename)}"`,
        "Cache-Control":       "no-store",
        "X-Content-Type-Options": "nosniff",
      };

      if (contentLength) headers["Content-Length"] = contentLength;

      // Range response handle করো
      const status = cdnResp.status === 206 ? 206 : 200;
      if (cdnResp.status === 206) {
        headers["Content-Range"] = cdnResp.headers.get("content-range") || "";
        headers["Accept-Ranges"] = "bytes";
      }

      // Stream করো — জমা হয় না
      return new Response(cdnResp.body, { status, headers });

    } catch (err) {
      console.error("Worker fetch error:", err);
      return new Response("Fetch failed: " + err.message, {
        status: 502,
        headers: corsHeaders(),
      });
    }
  },
};

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin":  ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Range",
    "Access-Control-Expose-Headers": "Content-Length, Content-Range",
  };
}

// Target CDN hostname দেখে সঠিক Referer বেছে নাও — অনেক CDN (বিশেষ করে
// TikTok) Referer না মিললে বা ভুল হলে 403 দেয়।
function refererFor(hostname) {
  const h = hostname.toLowerCase();
  if (h.includes("tiktok"))                          return "https://www.tiktok.com/";
  if (h.includes("instagram") || h.includes("cdninstagram")) return "https://www.instagram.com/";
  if (h.includes("fbcdn") || h.includes("facebook"))  return "https://www.facebook.com/";
  if (h.includes("googlevideo") || h.includes("youtube") || h.includes("ytimg")) return "https://www.youtube.com/";
  if (h.includes("twimg") || h.includes("twitter") || h.includes("x.com"))       return "https://twitter.com/";
  return undefined;
}

function guessContentType(filename) {
  const ext = filename.split(".").pop().toLowerCase();
  const map = {
    mp4: "video/mp4",
    webm: "video/webm",
    mkv: "video/x-matroska",
    mp3: "audio/mpeg",
    m4a: "audio/mp4",
    ogg: "audio/ogg",
  };
  return map[ext] || "application/octet-stream";
}
