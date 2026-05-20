"""
📢 ChannelManager — مدير القنوات والبث المتزامن
================================================
يدير قنوات Telegram متعددة مع جدولة وبث متزامن.
يرث من BaseAgent.
"""
import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.base_agent import BaseAgent

CHANNELS_PATH = os.path.join(BASE_DIR, "storage", "channels_registry.json")
os.makedirs(os.path.dirname(CHANNELS_PATH), exist_ok=True)


class ChannelManager(BaseAgent):
    """مدير القنوات — ينشر في قنوات Telegram متعددة"""

    def __init__(self):
        super().__init__(
            name="channel_manager",
            description="يدير قنوات Telegram ويبث المحتوى فيها",
            version="1.0"
        )
        self._channels = self._load_channels()
        self._scheduled_jobs: List[dict] = []
        self._job_counter = 0

    def run(self, input_data: dict) -> dict:
        action = input_data.get("action", "list")
        if action == "cross_post":
            return self.cross_post(
                input_data.get("content", ""),
                input_data.get("channel_ids", [])
            )
        elif action == "list":
            return {"channels": self.list_channels()}
        return {"status": "error", "error": f"Unknown action: {action}"}

    # ═══════════════════════════════════════
    # التسجيل
    # ═══════════════════════════════════════

    def register_channel(
        self,
        channel_id: str,
        name: str,
        bot_token: str,
        tags: list = None
    ) -> bool:
        """تسجيل قناة جديدة"""
        try:
            self._channels[channel_id] = {
                "channel_id": channel_id,
                "name": name,
                "bot_token_hash": bot_token[:10] + "***",
                "bot_token": bot_token,
                "tags": tags or [],
                "registered_at": datetime.utcnow().isoformat(),
                "posts_count": 0,
                "last_post": None,
            }
            self._save_channels()
            self.log(f"Channel registered: {name} ({channel_id})")
            return True
        except Exception as e:
            self.log(f"Register failed: {e}", level="ERROR")
            return False

    def unregister_channel(self, channel_id: str) -> bool:
        """إلغاء تسجيل قناة"""
        if channel_id in self._channels:
            del self._channels[channel_id]
            self._save_channels()
            return True
        return False

    # ═══════════════════════════════════════
    # النشر
    # ═══════════════════════════════════════

    def cross_post(self, content: str, channel_ids: list = None) -> dict:
        """نشر الآن في قنوات محددة"""
        if not content:
            return {"status": "error", "error": "المحتوى فارغ"}

        targets = channel_ids or list(self._channels.keys())
        results = {}

        for cid in targets:
            ch = self._channels.get(cid)
            if not ch:
                results[cid] = "❌ قناة غير مسجلة"
                continue

            try:
                import telebot
                bot = telebot.TeleBot(ch["bot_token"])
                bot.send_message(cid, content, parse_mode="Markdown")
                results[cid] = "✅ تم"
                ch["posts_count"] = ch.get("posts_count", 0) + 1
                ch["last_post"] = datetime.utcnow().isoformat()
            except Exception as e:
                results[cid] = f"❌ {str(e)[:50]}"

        self._save_channels()
        self.log(f"Cross-posted to {len(targets)} channels")
        return {"status": "success", "results": results}

    def auto_post(self, content: str, tags: list = None) -> int:
        """نشر في كل القنوات ذات الـ tags المحددة"""
        target_ids = []
        for cid, info in self._channels.items():
            if not tags:
                target_ids.append(cid)
            elif any(t in info.get("tags", []) for t in tags):
                target_ids.append(cid)

        result = self.cross_post(content, target_ids)
        return len(target_ids)

    def schedule_post(
        self,
        content: str,
        channel_ids: list,
        scheduled_time: str = "now",
        media_path: str = None
    ) -> str:
        """جدولة منشور"""
        self._job_counter += 1
        job_id = f"job_{self._job_counter}"

        job = {
            "job_id": job_id,
            "content": content,
            "channel_ids": channel_ids,
            "scheduled_time": scheduled_time,
            "media_path": media_path,
            "status": "PENDING",
            "created_at": datetime.utcnow().isoformat(),
        }

        if scheduled_time == "now":
            self.cross_post(content, channel_ids)
            job["status"] = "COMPLETED"
        else:
            self._scheduled_jobs.append(job)
            # تشغيل مجدول بسيط
            threading.Thread(
                target=self._execute_scheduled, args=(job,), daemon=True
            ).start()

        self.log(f"Post scheduled: {job_id}")
        return job_id

    # ═══════════════════════════════════════
    # التحليلات
    # ═══════════════════════════════════════

    def get_channel_analytics(self, channel_id: str) -> dict:
        """تحليلات قناة محددة"""
        ch = self._channels.get(channel_id)
        if not ch:
            return {"status": "error", "error": "قناة غير موجودة"}
        return {
            "name": ch.get("name"),
            "posts_count": ch.get("posts_count", 0),
            "last_post": ch.get("last_post"),
            "tags": ch.get("tags", []),
            "registered_at": ch.get("registered_at"),
        }

    def list_channels(self) -> list:
        """جميع القنوات المسجلة"""
        result = []
        for cid, info in self._channels.items():
            result.append({
                "channel_id": cid,
                "name": info.get("name", ""),
                "tags": info.get("tags", []),
                "posts_count": info.get("posts_count", 0),
                "last_post": info.get("last_post"),
            })
        return result

    # ═══════════════════════════════════════
    # دوال داخلية
    # ═══════════════════════════════════════

    def _execute_scheduled(self, job: dict):
        """تنفيذ منشور مجدول"""
        try:
            target_time = datetime.fromisoformat(job["scheduled_time"])
            wait = (target_time - datetime.utcnow()).total_seconds()
            if wait > 0:
                time.sleep(wait)
            self.cross_post(job["content"], job["channel_ids"])
            job["status"] = "COMPLETED"
        except Exception as e:
            job["status"] = "FAILED"
            self.log(f"Scheduled post failed: {e}", level="ERROR")

    def _load_channels(self) -> dict:
        try:
            if os.path.exists(CHANNELS_PATH):
                with open(CHANNELS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return {}

    def _save_channels(self):
        try:
            # لا نحفظ الـ token الكامل
            safe = {}
            for cid, info in self._channels.items():
                safe[cid] = info
            with open(CHANNELS_PATH, "w", encoding="utf-8") as f:
                json.dump(safe, f, ensure_ascii=False, indent=2)
        except IOError as e:
            self.log(f"Save channels error: {e}", level="ERROR")


# Singleton
channel_manager = ChannelManager()
