"""
Permission Manager – يتحكم في صلاحيات المستخدمين (ADMIN, OPERATOR, VIEWER)
ويُستَخدم كـ middleware في FastAPI وكمتحقق داخل الـ Orchestrator.
"""
import os
from typing import Set, Dict

# ---------------------------------------------------------------------------
# Role → permissions mapping (يمكن تعديلها عبر .env إذا لزم)
# ---------------------------------------------------------------------------
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "ADMIN": {"spawn_agent", "deploy", "restart", "view_logs", "orchestrate"},
    "OPERATOR": {"spawn_agent", "deploy", "view_logs", "orchestrate"},
    "VIEWER": {"view_logs"},
}

# ---------------------------------------------------------------------------
# تحميل تعيينات المستخدمين من متغيّر البيئة USER_ROLES
# الصيغة: "12345:ADMIN,67890:OPERATOR"
# ---------------------------------------------------------------------------
_raw = os.getenv("USER_ROLES", "")
USER_ROLES: Dict[int, str] = {}
for pair in _raw.split(","):
    if not pair:
        continue
    try:
        uid, role = pair.split(":")
        USER_ROLES[int(uid)] = role.upper()
    except Exception:
        # تجاهل أي تنسيق غير صالح
        continue


def get_role(user_id: int) -> str:
    """إرجاع الدور للمستخدم، أو VIEWER إذا غير معرف."""
    return USER_ROLES.get(user_id, "VIEWER")


def can(user_id: int, permission: str) -> bool:
    """تحقق ما إذا كان المستخدم يملك الصلاحية المطلوبة."""
    role = get_role(user_id)
    allowed = ROLE_PERMISSIONS.get(role, set())
    return permission in allowed

# ---------------------------------------------------------------------------
# FastAPI dependency – يُستَخدم في مسارات تحتاج صلاحية معينة
# ---------------------------------------------------------------------------
from fastapi import Depends, HTTPException, Request

def permission_dependency(permission: str):
    """Dependency factory لتضمينها في مسارات FastAPI.
    يُفترض أن الـ JWT تم التحقق منه مسبقاً وتخزين user_id في request.state.user_id.
    """
    async def _dep(request: Request):
        user_id = getattr(request.state, "user_id", None)
        if user_id is None or not can(user_id, permission):
            raise HTTPException(status_code=403, detail="Permission denied")
        return True
    return Depends(_dep)
