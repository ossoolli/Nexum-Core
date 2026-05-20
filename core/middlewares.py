import time
from functools import wraps

# تخزين مؤقت لآخر ضغطة لكل مستخدم لتجنب السبام
LAST_ACTION_TIME = {}

# يمكن ربط هذا بقاعدة بيانات حقيقية
USER_ROLES = {
    # user_id: "OWNER" 
    # مثال: 123456789: "OWNER"
}

def rate_limit(cooldown: float = 1.0):
    """عزل الطلبات المتكررة بسرعة"""
    def decorator(func):
        @wraps(func)
        def wrapper(call_or_msg, *args, **kwargs):
            user_id = call_or_msg.from_user.id
            now = time.time()
            last_time = LAST_ACTION_TIME.get(user_id, 0)
            
            if now - last_time < cooldown:
                # إذا كان الطلب من نوع CallbackQuery، يمكن الرد عليه مباشرة بصمت
                if hasattr(call_or_msg, "id") and hasattr(call_or_msg, "data"):
                    # نحتاج استدعاء answer_callback_query من الـ bot لكن البوت ليس هنا. 
                    # لذا سنكتفي بتجاهل التنفيذ. في هندسة أكثر تقدماً نقوم بحقن البوت.
                    return None 
                return None
                
            LAST_ACTION_TIME[user_id] = now
            return func(call_or_msg, *args, **kwargs)
        return wrapper
    return decorator

def require_role(roles: list):
    """التحقق من صلاحيات المستخدم"""
    def decorator(func):
        @wraps(func)
        def wrapper(call_or_msg, *args, **kwargs):
            user_id = call_or_msg.from_user.id
            user_role = USER_ROLES.get(user_id, "VIEWER")
            
            if user_role not in roles:
                # إذا لم يكن لديه صلاحية
                return None
                
            return func(call_or_msg, *args, **kwargs)
        return wrapper
    return decorator
