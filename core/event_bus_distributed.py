"""
Distributed Event Bus – يستخدم Redis Pub/Sub لجعل ناقل الأحداث موزعاً
بين أكثر من Node (مثلاً اكثر من Instance لتطبيق FastAPI).
إذا لم يتوفر Redis، يتراجع تلقائياً لاستخدام In-Memory.
"""
import os
import json
import time
import threading
from collections import deque
from datetime import datetime
from typing import Dict, List, Callable

try:
    import redis
except ImportError:
    redis = None

REDIS_URL = os.getenv("REDIS_URL", "")
NEXUM_CHANNEL = "nexum:events"

class DistributedEventBus:
    EVENT_TYPES = {
        "SYSTEM_ALERT": "system.alert",
        "AGENT_SPAWNED": "agent.spawned",
        "AGENT_STOPPED": "agent.stopped",
        "AGENT_FAILED": "agent.failed",
        "TASK_STARTED": "task.started",
        "TASK_COMPLETED": "task.completed",
        "TASK_FAILED": "task.failed",
        "BUILD_STARTED": "build.started",
        "BUILD_COMPLETED": "build.completed",
        "DEPLOY_STARTED": "deploy.started",
        "DEPLOY_COMPLETED": "deploy.completed",
        "DEPLOY_FAILED": "deploy.failed",
        "SANDBOX_SPAWNED": "sandbox.spawned",
        "SANDBOX_CRASHED": "sandbox.crashed",
        "PROTOCOL_COMPILED": "protocol.compiled",
    }

    def __init__(self, max_history=500):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history = deque(maxlen=max_history)
        self._lock = threading.Lock()
        
        self.redis_client = None
        self.pubsub = None
        
        if REDIS_URL and redis:
            try:
                self.redis_client = redis.from_url(REDIS_URL)
                self.pubsub = self.redis_client.pubsub()
                self.pubsub.subscribe(**{NEXUM_CHANNEL: self._redis_listener})
                
                # تشغيل Thread للاستماع لأحداث Redis
                self._listen_thread = threading.Thread(target=self._run_redis_listener, daemon=True)
                self._listen_thread.start()
                print("📡 Distributed Event Bus: Powered by Redis Streams")
            except Exception as e:
                print(f"⚠️ Redis Event Bus Connection Failed, falling back to Local: {e}")
                self.redis_client = None

    def _run_redis_listener(self):
        try:
            for message in self.pubsub.listen():
                pass
        except Exception as e:
            print(f"Redis Listener crashed: {e}")

    def _redis_listener(self, message):
        """مستمع للرسائل القادمة من Redis Pub/Sub وبثها داخلياً (Local)"""
        if message and message['type'] == 'message':
            try:
                data_str = message['data'].decode('utf-8')
                event = json.loads(data_str)
                # بث داخلي للمشتركين
                self._dispatch_internal(event, from_redis=True)
            except Exception as e:
                print(f"[EVENT_BUS] Redis Decode Error: {e}")

    def emit(self, event_type: str, data: dict = None):
        """بث حدث للشبكة والمشتركين المحليين"""
        if event_type not in self.EVENT_TYPES.values():
            pass
            
        event = {
            "id": f"evt_{int(time.time()*1000)}",
            "type": event_type,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
            "node": os.uname().nodename if hasattr(os, 'uname') else "local"
        }
        
        # بث للجميع عبر Redis إن وجد
        if self.redis_client:
            self.redis_client.publish(NEXUM_CHANNEL, json.dumps(event))
            
        # إضافة داخلياً وبث محلي
        self._dispatch_internal(event, from_redis=False)
        return event

    def _dispatch_internal(self, event: dict, from_redis: bool):
        """تسجيل وبث الحدث محلياً للمشتركين"""
        with self._lock:
            self._history.append(event)
            
        event_type = event["type"]
        
        for cb in self._subscribers.get(event_type, []):
            try:
                cb(event)
            except Exception as e:
                print(f"[EVENT_BUS] Subscriber error: {e}")
                
        for cb in self._subscribers.get("*", []):
            try:
                cb(event)
            except Exception as e:
                print(f"[EVENT_BUS] Wildcard error: {e}")
                
        # تسجيل في Runtime State
        try:
            from core.runtime_state import runtime_state
            runtime_state.push_event(event)
        except ImportError:
            pass

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def get_history(self, limit=50):
        with self._lock:
            return list(self._history)[-limit:]

    def stream_events(self):
        last_index = len(self._history)
        while True:
            with self._lock:
                current = list(self._history)
            if len(current) > last_index:
                for ev in current[last_index:]:
                    yield f"data: {json.dumps(ev)}\n\n"
                last_index = len(current)
            time.sleep(0.5)

# Singleton
event_bus = DistributedEventBus()
