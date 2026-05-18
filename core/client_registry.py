"""
Client Registry – يدير جميع اتصالات WebSocket مع معلومات
المستخدم. يدعم اتصالات متعددة للمستخدم الواحد (عبر token الجلسة)
لدعم عدة فتحات تبويب أو أجهزة.
"""

import threading
import time
from typing import Dict, Any

class ClientRegistry:
    def __init__(self):
        # التركيبة: { user_id: { session_token: {"websocket": ws, "last_seen": timestamp, "role": role} } }
        self._clients: Dict[int, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def add(self, user_id: int, session_token: str, ws, role: str = "VIEWER"):
        with self._lock:
            if user_id not in self._clients:
                self._clients[user_id] = {}
            self._clients[user_id][session_token] = {
                "websocket": ws,
                "last_seen": time.time(),
                "role": role,
            }

    def remove(self, user_id: int, session_token: str):
        with self._lock:
            if user_id in self._clients:
                self._clients[user_id].pop(session_token, None)
                # تنظيف user_id إذا لم يعد لديه جلسات
                if not self._clients[user_id]:
                    del self._clients[user_id]

    def get_websockets(self, user_id: int) -> list:
        """إرجاع قائمة بجميع الـ websockets المفتوحة لهذا المستخدم"""
        with self._lock:
            if user_id in self._clients:
                return [session_data["websocket"] for session_data in self._clients[user_id].values()]
            return []
            
    def get_all_websockets(self) -> list:
        """إرجاع جميع الـ websockets النشطة لجميع المستخدمين"""
        with self._lock:
            all_ws = []
            for user_sessions in self._clients.values():
                all_ws.extend([session_data["websocket"] for session_data in user_sessions.values()])
            return all_ws

    def update_heartbeat(self, user_id: int, session_token: str):
        with self._lock:
            if user_id in self._clients and session_token in self._clients[user_id]:
                self._clients[user_id][session_token]["last_seen"] = time.time()

    def list_active(self):
        with self._lock:
            now = time.time()
            active_clients = {}
            for user_id, sessions in self._clients.items():
                active_sessions = {
                    token: info
                    for token, info in sessions.items()
                    if now - info["last_seen"] < 30
                }
                if active_sessions:
                    active_clients[user_id] = active_sessions
            return active_clients

# Singleton
client_registry = ClientRegistry()
