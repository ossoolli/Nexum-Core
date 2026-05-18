"""
NEXUM Runtime Server — FastAPI + WebSocket + SSE
الخادم الحقيقي لمنصة التحكم السيادية (Sovereign Control Plane)
"""
import os
import sys
import json
import asyncio
import psutil
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# إعداد المسار
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.agent_registry import agent_registry
from core.event_bus import event_bus
from core.lifecycle import lifecycle
from core.orchestrator import orchestrator

app = FastAPI(title="NEXUM PRIME Runtime", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# === WebSocket Connections ===
connected_clients: list[WebSocket] = []


async def broadcast(data: dict):
    """بث البيانات لجميع العملاء المتصلين عبر WebSocket"""
    message = json.dumps(data)
    for ws in connected_clients[:]:
        try:
            await ws.send_text(message)
        except Exception:
            connected_clients.remove(ws)


# === Routes ===

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """تقديم واجهة النظام التشغيلي المرئي"""
    html_path = os.path.join(BASE_DIR, "webapp", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/agents")
async def get_agents():
    """جلب سجل الوكلاء مع حالات دورة الحياة"""
    agents = list(agent_registry.agents.values())
    for ag in agents:
        state_info = lifecycle.get_state(ag["agent_id"])
        ag["lifecycle"] = state_info
    return agents


@app.get("/api/events")
async def get_events():
    """جلب آخر الأحداث المسجلة في النظام"""
    return event_bus.get_history(limit=50)


@app.get("/api/system/stream")
async def system_stream():
    """بث SSE حي لاستهلاك الموارد"""
    async def generate():
        while True:
            data = {
                "cpu": psutil.cpu_percent(interval=None),
                "ram": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent,
                "timestamp": datetime.now().isoformat(),
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(2)
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/orchestrate")
async def trigger_orchestrator(payload: dict):
    """تلقي أوامر من الـ Command Palette وتشغيل الأوركستريتور"""
    goal = payload.get("goal", "")
    if not goal:
        return {"error": "No goal provided"}

    event_bus.emit(event_bus.TASK_STARTED, {"goal": goal})
    try:
        result = orchestrator.execute_goal(goal)
        event_bus.emit(event_bus.TASK_COMPLETED, {
            "goal": goal,
            "protocol_id": result.get("protocol", {}).get("protocol_id"),
        })
        return {"status": "success", "result": result}
    except Exception as e:
        event_bus.emit(event_bus.TASK_FAILED, {"goal": goal, "error": str(e)})
        return {"status": "error", "message": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """نقطة WebSocket للبث الحي للأحداث وحالة النظام"""
    await ws.accept()
    connected_clients.append(ws)
    try:
        # إرسال الحالة الأولية
        await ws.send_text(json.dumps({
            "type": "init",
            "agents": list(agent_registry.agents.values()),
            "events": event_bus.get_history(20),
        }))
        while True:
            # انتظار أوامر من العميل
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("action") == "orchestrate":
                result = orchestrator.execute_goal(msg.get("goal", ""))
                await ws.send_text(json.dumps({"type": "orchestrate_result", "data": result}))
    except WebSocketDisconnect:
        connected_clients.remove(ws)


# ربط الـ Event Bus بالـ WebSocket للبث التلقائي
def _on_any_event(event):
    """عند حدوث أي حدث، أرسله لكل العملاء المتصلين"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(broadcast({"type": "event", "event": event}))
    except RuntimeError:
        pass

event_bus.subscribe("*", _on_any_event)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🔱 NEXUM Runtime Server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
