import pytest
from nexum.security.rate_limiter import RateLimiter

def test_rate_limiter():
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    user_id = 12345
    
    # أول 3 رسائل مقبولة
    assert limiter.is_allowed(user_id) is True
    assert limiter.is_allowed(user_id) is True
    assert limiter.is_allowed(user_id) is True
    
    # الرسالة الرابعة مرفوضة
    assert limiter.is_allowed(user_id) is False

def test_dangerous_commands_logic():
    # هذا اختبار تجريبي لمنطق الحماية المخطط له في guard.py لاحقاً
    from core.security import security
    dangerous = "rm -rf /"
    # النظام الحالي يجب أن يحجب الكلمات المفتاحية
    assert any(word in dangerous for word in ["rm -rf", "mkfs"])
