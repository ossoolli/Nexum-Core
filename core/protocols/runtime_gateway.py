from typing import Dict, List, Set, Any
from fastapi import WebSocket
import asyncio
import json

class RuntimeGateway:
    """
    Sovereign Runtime Gateway
    مدير قنوات الـ WebSocket، يدعم الاشتراكات، الغرف، وبث التحديثات التراكمية (Delta Updates).
    يستبدل بث الحالة الكاملة (Full-State Refreshes) لتجنب العبء على الشبكة.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # تعقب اشتراكات الجلسات: websocket -> set of channel names
        self.subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set(["system", "events_live"]) # قنوات افتراضية

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]

    async def subscribe(self, websocket: WebSocket, channel: str):
        if websocket in self.subscriptions:
            self.subscriptions[websocket].add(channel)

    async def unsubscribe(self, websocket: WebSocket, channel: str):
        if websocket in self.subscriptions and channel in self.subscriptions[websocket]:
            self.subscriptions[websocket].remove(channel)

    async def broadcast(self, message: dict, channel: str = "system"):
        """بث البيانات للمشتركين في القناة المحددة فقط"""
        payload = json.dumps({"channel": channel, "data": message})
        inactive_sockets = []
        
        for ws in self.active_connections:
            if channel in self.subscriptions.get(ws, set()):
                try:
                    await ws.send_text(payload)
                except Exception:
                    inactive_sockets.append(ws)
                    
        for ws in inactive_sockets:
            self.disconnect(ws)

runtime_gateway = RuntimeGateway()
