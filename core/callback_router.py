"""
Structured Callback Router — نظام توجيه الأزرار الهيكلي
بدل if/else المتضاربة، يستخدم namespace:action:param pattern
مثال: monitor:cpu, docker:restart:container_id, agent:spawn:frontend
"""
from typing import Callable, Dict, Optional


class CallbackRouter:
    """
    يسجل handlers لكل namespace ويوجه الطلبات تلقائياً.
    """

    def __init__(self):
        self._routes: Dict[str, Callable] = {}
        self._namespace_handlers: Dict[str, Callable] = {}

    def register(self, pattern: str, handler: Callable):
        """
        تسجيل handler لنمط محدد.
        pattern: "monitor:cpu" أو "docker:restart" أو "agent:spawn"
        """
        self._routes[pattern] = handler

    def register_namespace(self, namespace: str, handler: Callable):
        """
        تسجيل handler لكل الأوامر تحت namespace معين.
        مثال: register_namespace("monitor", handle_all_monitor)
        """
        self._namespace_handlers[namespace] = handler

    def dispatch(self, callback_data: str, context: dict = None) -> Optional[dict]:
        """
        يوجه callback_data للـ handler المناسب.
        يبحث أولاً عن تطابق كامل، ثم عن namespace.
        """
        context = context or {}

        # تطابق كامل أولاً
        if callback_data in self._routes:
            return self._routes[callback_data](callback_data, context)

        # تحليل الـ namespace
        parts = callback_data.split(":")
        namespace = parts[0]
        action = parts[1] if len(parts) > 1 else None
        param = parts[2] if len(parts) > 2 else None

        context["namespace"] = namespace
        context["action"] = action
        context["param"] = param

        # البحث عن namespace:action
        ns_action = f"{namespace}:{action}" if action else namespace
        if ns_action in self._routes:
            return self._routes[ns_action](callback_data, context)

        # البحث عن namespace handler عام
        if namespace in self._namespace_handlers:
            return self._namespace_handlers[namespace](callback_data, context)

        return {"error": f"No handler for: {callback_data}"}

    def list_routes(self) -> list:
        """عرض جميع المسارات المسجلة"""
        return list(self._routes.keys()) + [f"{ns}:*" for ns in self._namespace_handlers]


router = CallbackRouter()
