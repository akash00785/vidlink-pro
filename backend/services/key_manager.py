"""
একাধিক RapidAPI key নিয়ে কাজ করার জন্য — একটা key rate-limit (429) খেলে
বাকিগুলো এখনো কাজ করতে পারলে অটো পরের key-তে সুইচ করে। ব্যর্থ key কিছুক্ষণ
(cooldown) "বিরতিতে" থাকে, তারপর আবার নিজে থেকেই সক্রিয় হয় (RapidAPI free
plan প্রায়ই দৈনিক/মাসিক রিসেট হয়)।

RAPIDAPI_KEY এনভায়রনমেন্ট ভ্যারিয়েবলে কমা (,) দিয়ে একাধিক key দেওয়া যায়:
  RAPIDAPI_KEY=keyA,keyB,keyC
একটামাত্র key দিলেও স্বাভাবিকভাবে কাজ করবে (rotation ছাড়াই)।
"""
import time
import threading


class KeyManager:
    def __init__(self, keys_str, cooldown_seconds=6 * 60 * 60):
        self.keys = [
            {"val": k.strip(), "active": True, "failed_at": 0}
            for k in (keys_str or "").split(",")
            if k.strip()
        ]
        self.cooldown = cooldown_seconds
        self._lock = threading.Lock()

    def has_keys(self) -> bool:
        return bool(self.keys)

    def get_active_key(self):
        """একটা সক্রিয় key ফেরত দেয়, cooldown শেষ হলে ব্যর্থ key আবার সক্রিয় করে।"""
        with self._lock:
            now = time.time()
            for k in self.keys:
                if not k["active"] and (now - k["failed_at"] > self.cooldown):
                    k["active"] = True
            for k in self.keys:
                if k["active"]:
                    return k["val"]
            return None

    def mark_rate_limited(self, key_val):
        with self._lock:
            for k in self.keys:
                if k["val"] == key_val:
                    k["active"] = False
                    k["failed_at"] = time.time()
