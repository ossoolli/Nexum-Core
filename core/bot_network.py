"""
📡 BotNetwork — شبكة التواصل بين البوتات
==========================================
Redis Pub/Sub مع fallback لـ dict محلي.
"""
import json
import uuid
import time
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

# محاولة تحميل Redis (اختياري)
try:
    import redis
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False


class BotNetwork:
    """شبكة تواصل بين البوتات عبر Redis أو قاموس محلي"""

    def __init__(self, redis_url: str = None):
        self._bots: Dict[str, dict] = {}
        self._message_queue: Dict[str, list] = {}       # fallback محلي
        self._task_results: Dict[str, dict] = {}
        self._callbacks: Dict[str, Callable] = {}
        self._redis = None

        if redis_url and _REDIS_AVAILABLE:
            try:
                self._redis = redis.Redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                print("[BotNetwork] Redis connected.")
            except Exception as e:
                print(f"[BotNetwork] Redis failed, using local: {e}")
                self._redis = None
        else:
            print("[BotNetwork] Running in local mode (no Redis).")

    # ═══════════════════════════════════════
    # التسجيل
    # ═══════════════════════════════════════

    def register_bot(self, name: str, token: str = "", callback_url: str = None) -> bool:
        """تسجيل بوت في الشبكة"""
        try:
            self._bots[name] = {
                "name": name,
                "token_hash": hash(token) if token else 0,
                "callback_url": callback_url,
                "registered_at": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat(),
            }
            if name not in self._message_queue:
                self._message_queue[name] = []
            return True
        except Exception:
            return False

    def unregister_bot(self, name: str) -> bool:
        """إلغاء تسجيل بوت"""
        self._bots.pop(name, None)
        self._message_queue.pop(name, None)
        return True

    # ═══════════════════════════════════════
    # المراسلة
    # ═══════════════════════════════════════

    def send_message(
        self,
        from_bot: str,
        to_bot: str,
        message: str,
        message_type: str = "text"
    ) -> bool:
        """إرسال رسالة من بوت لآخر"""
        try:
            payload = {
                "from": from_bot,
                "to": to_bot,
                "type": message_type,
                "content": message,
                "timestamp": datetime.utcnow().isoformat(),
                "id": uuid.uuid4().hex[:8],
            }

            if self._redis:
                channel = f"nexum.bot.{to_bot}"
                self._redis.publish(channel, json.dumps(payload, ensure_ascii=False))
            else:
                if to_bot not in self._message_queue:
                    self._message_queue[to_bot] = []
                self._message_queue[to_bot].append(payload)

            return True
        except Exception as e:
            print(f"[BotNetwork] Send error: {e}")
            return False

    def broadcast_all(self, from_bot: str, message: str) -> int:
        """بث رسالة لجميع البوتات المسجلة"""
        count = 0
        for name in self._bots:
            if name != from_bot:
                if self.send_message(from_bot, name, message, "broadcast"):
                    count += 1
        return count

    def get_messages(self, bot_name: str) -> list:
        """جلب الرسائل المعلّقة لبوت (local fallback)"""
        msgs = self._message_queue.get(bot_name, [])
        self._message_queue[bot_name] = []
        return msgs

    # ═══════════════════════════════════════
    # تفويض المهام
    # ═══════════════════════════════════════

    def delegate_task(
        self,
        from_bot: str,
        to_bot: str,
        task: dict,
        callback: Callable = None
    ) -> str:
        """تكليف بوت بمهمة وانتظار النتيجة"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task_payload = {
            "task_id": task_id,
            "from": from_bot,
            "task": task,
            "status": "PENDING",
            "created_at": datetime.utcnow().isoformat(),
        }

        if callback:
            self._callbacks[task_id] = callback

        self.send_message(from_bot, to_bot, json.dumps(task_payload), "task")
        self._task_results[task_id] = {"status": "PENDING"}
        return task_id

    def report_task_result(self, task_id: str, result: dict):
        """تسجيل نتيجة مهمة"""
        self._task_results[task_id] = {
            "status": "COMPLETED",
            "result": result,
            "completed_at": datetime.utcnow().isoformat(),
        }
        cb = self._callbacks.pop(task_id, None)
        if cb:
            try:
                cb(result)
            except Exception:
                pass

    def get_task_status(self, task_id: str) -> dict:
        """حالة مهمة"""
        return self._task_results.get(task_id, {"status": "NOT_FOUND"})

    # ═══════════════════════════════════════
    # الحالة
    # ═══════════════════════════════════════

    def get_network_status(self) -> dict:
        """خريطة كاملة للشبكة"""
        return {
            "total_bots": len(self._bots),
            "redis_connected": self._redis is not None,
            "bots": list(self._bots.keys()),
            "pending_messages": {
                name: len(msgs) for name, msgs in self._message_queue.items()
            },
            "active_tasks": sum(
                1 for t in self._task_results.values() if t["status"] == "PENDING"
            ),
        }


# Singleton
bot_network = BotNetwork()
