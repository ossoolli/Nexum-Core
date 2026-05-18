import uuid
import time
from threading import Lock

class SessionManager:
    """Manage short‑lived session tokens for Telegram ↔ Web reconnects.
    Tokens are valid for 10 minutes by default and map a Telegram user_id
    to a WebSocket reconnection request.
    """

    def __init__(self, ttl_seconds: int = 600):
        self._sessions = {}  # token -> (user_id, expires_at)
        self._ttl = ttl_seconds
        self._lock = Lock()

    def create_token(self, user_id: int) -> str:
        token = uuid.uuid4().hex
        expires = time.time() + self._ttl
        with self._lock:
            self._sessions[token] = (user_id, expires)
        return token

    def validate_token(self, token: str) -> int | None:
        with self._lock:
            data = self._sessions.get(token)
            if not data:
                return None
            user_id, expires = data
            if time.time() > expires:
                del self._sessions[token]
                return None
            # token is single‑use; remove after validation
            del self._sessions[token]
            return user_id

    def purge_expired(self):
        now = time.time()
        with self._lock:
            expired = [t for t, (_, exp) in self._sessions.items() if exp < now]
            for t in expired:
                del self._sessions[t]

# Singleton instance used across the project
session_manager = SessionManager()
