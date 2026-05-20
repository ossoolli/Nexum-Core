import time
from functools import wraps
from telebot import TeleBot

# قاموس لتتبع آخر استدعاء لكل مستخدم: {user_id: last_timestamp}
_user_logs = {}

def rate_limit(cooldown: float = 1.0):
    """
    Decorator لمنع إغراق البوت بالطلبات (Rate Limiting).
    يسمح بطلب واحد كل (cooldown) ثانية لكل مستخدم.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(message_or_call, *args, **kwargs):
            try:
                # التحقق إذا كان الحدث رسالة عادية أو Callback-Query
                user_id = message_or_call.from_user.id
            except AttributeError:
                # إذا لم نتمكن من تحديد المعرّف، نستمر في التنفيذ كخيار أمان
                return func(message_or_call, *args, **kwargs)

            now = time.time()
            last_time = _user_logs.get(user_id, 0)

            if now - last_time < cooldown:
                # إذا لم تنتهي فترة التبريد، يتم حجب الطلب والرد بتحذير صامت
                if hasattr(message_or_call, 'data'): # event is CallbackQuery
                    # البحث عن نسخة البوت في المعاملات لأجل answer_callback
                    for arg in args:
                        if hasattr(arg, 'answer_callback_query'):
                            arg.answer_callback_query(message_or_call.id, "⚠️ يرجى التمهل! عمليات سريعة جداً.", show_alert=True)
                            break
                return 

            _user_logs[user_id] = now
            return func(message_or_call, *args, **kwargs)
        return wrapper
    return decorator
