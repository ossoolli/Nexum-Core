import json
import redis
import os
from typing import Dict, Any

class DistributedMemory:
    """
    Distributed Memory Layer
    يعتمد على Redis كطبقة Pub/Sub وكذاكرة سريعة (Fast Memory).
    مهيأ لاستقبال Vector DB (مثل pgvector) للذاكرة طويلة المدى لاحقاً.
    """
    def __init__(self):
        # Using default localhost for now, can be configured via ENV
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        
        try:
            self.r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.r.ping()
            self.connected = True
            print("🚀 [Persistence] Distributed Memory connected to Redis.")
        except redis.ConnectionError:
            self.connected = False
            print("⚠️ [Persistence] Redis not available. Running in memory degradation mode.")
            self._fallback_memory = {}

    def set_agent_state(self, agent_id: str, state: Dict[str, Any]):
        """حفظ حالة الوكيل في الذاكرة الموزعة"""
        if self.connected:
            self.r.set(f"agent:state:{agent_id}", json.dumps(state))
        else:
            self._fallback_memory[f"agent:state:{agent_id}"] = json.dumps(state)

    def get_agent_state(self, agent_id: str) -> Dict[str, Any]:
        """استرجاع حالة الوكيل"""
        if self.connected:
            data = self.r.get(f"agent:state:{agent_id}")
        else:
            data = self._fallback_memory.get(f"agent:state:{agent_id}")
            
        return json.loads(data) if data else {}

    def publish_event(self, channel: str, message: Dict[str, Any]):
        """بث حدث حي لجميع المكتتبين (WebSockets/Orchestrator)"""
        if self.connected:
            self.r.publish(channel, json.dumps(message))
        # Note: In fallback mode, local EventBus acts as the pub/sub engine.

distributed_memory = DistributedMemory()
