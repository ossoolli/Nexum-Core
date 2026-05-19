import os
import sys
import json
import asyncio
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.agent_registry import agent_registry
from core.event_bus import event_bus
from core.lifecycle import lifecycle
from core.runtime.message_bus import message_bus
from core.protocols.runtime_gateway import runtime_gateway
from core.runtime.async_orchestrator import async_orchestrator
from core.runtime.state_diff import state_diff

app = FastAPI(title="NEXUM Sovereign Runtime Gateway", version="3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_event():
    """Start runtime kernel workers and gateway message routers asynchronously"""
    from core.runtime.runtime_kernel import runtime_kernel
    asyncio.create_task(runtime_kernel.start())
    asyncio.create_task(_route_message_bus_to_gateway())
    print("🔱 [Gateway] Sovereign Runtime Gateway Initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    from core.runtime.runtime_kernel import runtime_kernel
    runtime_kernel.stop()

async def _route_message_bus_to_gateway():
    """قراءة الأحداث من الـ Message Bus وبثها عبر الـ Gateway بشكل تراكمي"""
    while True:
        event = await message_bus.event_stream.get()
        try:
            # Generate delta updates if applicable to reduce volume
            if event["type"] == "METRICS_UPDATE":
                delta = state_diff.compute_diff(event["data"], namespace="metrics")
                if delta:
                    await runtime_gateway.broadcast({"type": "metrics", "delta": delta}, channel="system")
            else:
                await runtime_gateway.broadcast(event, channel="events_live")
        finally:
            message_bus.event_stream.task_done()

# === RUNTIME SNAPSHOT ENDPOINTS ===

from core.runtime.swarm_manager import swarm_manager

@app.post("/agents/spawn")
async def spawn_new_agent(payload: dict):
    """
    Endpoint لتوليد وكيل جديد فعلياً في Runtime
    """
    role = payload.get("role", "Worker")
    capabilities = payload.get("capabilities", [])
    parent_id = payload.get("parent_id")
    
    agent = await swarm_manager.spawn_agent(role, capabilities, parent_id)
    return {"status": "success", "agent": agent}

@app.get("/runtime/state")
async def get_runtime_state():
    return {
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "active_graphs": len(async_orchestrator.active_graphs),
        "queued_tasks": message_bus.task_queue.qsize()
    }

@app.get("/runtime/agents")
async def get_runtime_agents(capability: str = None):
    if capability:
        agents = agent_registry.get_agents_by_capability(capability)
    else:
        agents = list(agent_registry.agents.values())
    for ag in agents:
        ag["lifecycle"] = lifecycle.get_state(ag["agent_id"])
    return agents

@app.get("/runtime/events")
async def get_runtime_events():
    return event_bus.get_history(limit=100)

@app.get("/runtime/protocols")
async def get_runtime_protocols():
    # Helper endpoint to fetch available yaml protocols
    return []

@app.post("/runtime/orchestrate")
async def trigger_orchestrator(payload: dict):
    goal = payload.get("goal", "")
    if not goal:
        return {"error": "No goal provided"}
    
    # We send this to the planner via regular event bus or create an async planner interface
    # For now, put it into the task queue or orchestrate directly
    await message_bus.route_task(None, {"action": "generate_graph", "goal": goal})
    return {"status": "Processing via Swarm"}

# === SOVEREIGN WEBSOCKET LAYER ===

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await runtime_gateway.connect(websocket)
    try:
        # إرسال Snapshot مبدئي
        init_state = {
            "type": "init",
            "agents": list(agent_registry.agents.values()),
        }
        await websocket.send_text(json.dumps(init_state))
        
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            # إدارة الاشتراكات ديناميكياً
            if msg.get("action") == "subscribe":
                await runtime_gateway.subscribe(websocket, msg.get("channel"))
            elif msg.get("action") == "unsubscribe":
                await runtime_gateway.unsubscribe(websocket, msg.get("channel"))
                
    except WebSocketDisconnect:
        runtime_gateway.disconnect(websocket)

# HTML UI
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    html_path = os.path.join(BASE_DIR, "webapp", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🔱 NEXUM Runtime OS active on port {port}")
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True)
