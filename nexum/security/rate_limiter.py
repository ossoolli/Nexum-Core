import time
from collections import defaultdict

class RateLimiter:
    """
    يمنع إغراق البوت بالرسائل.
    الحد الافتراضي: 10 رسائل في 30 ثانية لكل مستخدم.
    """
    def __init__(self, max_requests: int = 10, window_seconds: int = 30):
        self.max_requests = max_requests
        self.window = window_seconds
        self._log = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        now = time.time()
        window_start = now - self.window
        # احتفظ فقط بالطلبات داخل النافذة الزمنية
        self._log[user_id] = [
            t for t in self._log[user_id] if t > window_start
        ]
        if len(self._log[user_id]) >= self.max_requests:
            return False
        self._log[user_id].append(now)
        return True

rate_limiter = RateLimiter()
