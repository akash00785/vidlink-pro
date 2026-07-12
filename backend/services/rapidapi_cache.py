"""
একই TikTok ভিডিও/পোস্ট লিংক বারবার এলে প্রতিবার RapidAPI-কে না ডেকে অল্প
সময়ের জন্য ফলাফল মেমরিতে ক্যাশ করে রাখা হয় — ভাইরাল ভিডিওতে অনেক ভিজিটর
একই লিংক পাঠালে RapidAPI কোটা বাঁচে।

এটা ইচ্ছাকৃতভাবে in-memory (এই process-এর মধ্যেই) রাখা হয়েছে, Tik2BD-Pro-এর
মতো Upstash Redis ব্যবহার করা হয়নি — কারণ সেটার জন্য আলাদা account বানিয়ে
নতুন secret (UPSTASH_REDIS_REST_URL/TOKEN) যোগ করতে হতো। ট্রেড-অফ:
- Render redeploy/restart হলে ক্যাশ খালি হয়ে যায় — সমস্যা না, নতুন করে
  ভরে যাবে।
- একাধিক gunicorn worker চললে প্রতিটার নিজস্ব আলাদা ক্যাশ থাকে (পুরোপুরি
  shared না), তবু একই worker-এ বারবার আসা রিকোয়েস্টের কোটা বাঁচায়।
  ভবিষ্যতে সত্যিকারের cross-worker ক্যাশ চাইলে Upstash Redis
  (hd_limiter-এর প্যাটার্নে) যোগ করা যাবে।
"""
import time
import threading

CACHE_TTL_SECONDS = 45 * 60
MAX_ENTRIES = 500

_lock = threading.Lock()
_store = {}  # url -> (expires_at, result)


def get_cached(url):
    with _lock:
        entry = _store.get(url)
        if not entry:
            return None
        expires_at, result = entry
        if time.time() > expires_at:
            _store.pop(url, None)
            return None
        return result


def set_cached(url, result):
    """সফল রেজাল্টই ক্যাশ করা হয় — ব্যর্থ রেজাল্ট ক্যাশ করলে সাময়িক সমস্যাও
    ৪৫ মিনিট ধরে সবার জন্য দেখাতে থাকবে।"""
    if not result or not result.get("success"):
        return
    with _lock:
        _store[url] = (time.time() + CACHE_TTL_SECONDS, result)
        if len(_store) > MAX_ENTRIES:
            oldest_key = min(_store, key=lambda k: _store[k][0])
            _store.pop(oldest_key, None)
