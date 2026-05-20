"""
🔱 NEXUM Runtime API — FastAPI Gateway v5.0
=============================================
يوفر REST API + WebSocket للتحكم بجميع وكلاء النظام.
جميع الاستيرادات اختيارية — لن ينهار إذا نقص ملف.
"""
import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# ─── استيرادات آمنة (لا تنهار إذا نقص ملف) ───
from core.agent_registry import agent_registry
from core.event_bus import event_bus

try:
    from core.lifecycle import lifecycle
except ImportError:
    lifecycle = None

try:
    from core.runtime.message_bus import message_bus
    from core.protocols.runtime_gateway import runtime_gateway
    from core.runtime.async_orchestrator import async_orchestrator
    from core.runtime.state_diff import state_diff
    from core.runtime.swarm_manager import swarm_manager
    _RUNTIME_AVAILABLE = True
except ImportError:
    _RUNTIME_AVAILABLE = False
    message_bus = None
    runtime_gateway = None

# ─── استيراد الوكلاء الجدد ───
try:
    from agents.webforge_agent import webforge
except ImportError:
    webforge = None

try:
    from agents.agent_smith import agent_smith
except ImportError:
    agent_smith = None

try:
    from core.bot_fleet import bot_fleet
except ImportError:
    bot_fleet = None

try:
    from agents.channel_manager import channel_manager
except ImportError:
    channel_manager = None

try:
    from agents.monitor import monitor_agent
except ImportError:
    monitor_agent = None


# ═══════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════

class BuildRequest(BaseModel):
    project_name: str
    description: str = ""
    type: str = "landing"
    color_scheme: str = "blue"
    sections: list = []

class AgentBuildRequest(BaseModel):
    name: str
    purpose: str
    tools_needed: list = []
    triggers: list = []
    auto_start: bool = False

class BotSpawnRequest(BaseModel):
    name: str
    token: str
    personality: str
    capabilities: list = ["chat"]
    admin_id: int = 0

class ChannelRequest(BaseModel):
    channel_id: str
    name: str
    bot_token: str
    tags: list = []

class PostRequest(BaseModel):
    content: str
    channel_ids: list
    scheduled_time: str = "now"


# ═══════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════

app = FastAPI(title="NEXUM Sovereign Runtime Gateway", version="5.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def startup_event():
    if _RUNTIME_AVAILABLE:
        try:
            from core.runtime.runtime_kernel import runtime_kernel
            asyncio.create_task(runtime_kernel.start())
        except Exception:
            pass
    print("🔱 [Gateway] NEXUM API v5.0 — Online.")


# ═══════════════════════════════════════
# System Endpoints
# ═══════════════════════════════════════

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "version": "5.0",
        "timestamp": datetime.utcnow().isoformat(),
        "modules": {
            "webforge": webforge is not None,
            "agent_smith": agent_smith is not None,
            "bot_fleet": bot_fleet is not None,
            "channel_manager": channel_manager is not None,
            "runtime": _RUNTIME_AVAILABLE,
        }
    }

@app.get("/api/status")
async def system_status():
    report = {}
    if monitor_agent:
        try:
            report = monitor_agent.get_system_info()
        except Exception:
            report = {"status": "monitor unavailable"}
    return report

@app.get("/runtime/agents")
async def get_runtime_agents(capability: str = None):
    if capability:
        agents = agent_registry.get_agents_by_capability(capability)
    else:
        agents = list(agent_registry.agents.values())
    return agents

@app.get("/runtime/events")
async def get_runtime_events():
    try:
        return event_bus.get_history(limit=100)
    except Exception:
        return []


# ═══════════════════════════════════════
# WebForge Endpoints
# ═══════════════════════════════════════

@app.post("/api/webforge/build")
async def build_project(request: BuildRequest):
    if not webforge:
        return {"status": "error", "error": "WebForge not available"}
    result = webforge.start({
        "type": request.type,
        "project_name": request.project_name,
        "description": request.description,
        "color_scheme": request.color_scheme,
        "sections": request.sections
    })
    return result

@app.get("/api/webforge/apps")
async def list_apps():
    if not webforge:
        return []
    return webforge.list_projects()

@app.get("/api/webforge/preview/{name}")
async def get_preview_url(name: str):
    if not webforge:
        return {"error": "WebForge not available"}
    url = webforge.serve_local(name)
    return {"preview_url": url}


# ═══════════════════════════════════════
# Agent Builder Endpoints
# ═══════════════════════════════════════

@app.post("/api/agents/build")
async def build_agent(request: AgentBuildRequest):
    if not agent_smith:
        return {"status": "error", "error": "AgentSmith not available"}
    spec = agent_smith.design_agent(request.name, request.purpose, request.tools_needed, request.triggers)
    if spec.get("status") == "success":
        path = agent_smith.build_agent(request.name)
        return {"status": "success", "path": path, "spec": spec.get("spec")}
    return spec

@app.get("/api/agents/list")
async def list_agents():
    if not agent_smith:
        return []
    return agent_smith.list_agents()

@app.post("/api/agents/export/{name}")
async def export_agent(name: str):
    if not agent_smith:
        return {"error": "AgentSmith not available"}
    path = agent_smith.export_agent(name)
    return {"path": path}

@app.delete("/api/agents/{name}")
async def delete_agent(name: str):
    return {"status": "not_implemented", "message": "Agent deletion coming soon"}


# ═══════════════════════════════════════
# Bot Fleet Endpoints
# ═══════════════════════════════════════

@app.post("/api/bots/spawn")
async def spawn_bot(request: BotSpawnRequest):
    if not bot_fleet:
        return {"status": "error", "error": "BotFleet not available"}
    return bot_fleet.spawn_bot(
        request.name, request.token, request.personality,
        request.capabilities, request.admin_id
    )

@app.get("/api/bots/list")
async def list_bots():
    if not bot_fleet:
        return []
    return bot_fleet.list_bots()

@app.post("/api/bots/{name}/restart")
async def restart_bot(name: str):
    if not bot_fleet:
        return {"error": "BotFleet not available"}
    return {"result": bot_fleet.restart_bot(name)}

@app.delete("/api/bots/{name}")
async def delete_bot(name: str):
    if not bot_fleet:
        return {"error": "BotFleet not available"}
    return {"result": bot_fleet.kill_bot(name)}

@app.get("/api/bots/{name}/stats")
async def bot_stats(name: str):
    if not bot_fleet:
        return {"error": "BotFleet not available"}
    return bot_fleet.get_bot_stats(name)


# ═══════════════════════════════════════
# Channel Manager Endpoints
# ═══════════════════════════════════════

@app.post("/api/channels/register")
async def register_channel(request: ChannelRequest):
    if not channel_manager:
        return {"status": "error", "error": "ChannelManager not available"}
    ok = channel_manager.register_channel(
        request.channel_id, request.name, request.bot_token, request.tags
    )
    return {"status": "success" if ok else "error"}

@app.get("/api/channels/list")
async def list_channels():
    if not channel_manager:
        return []
    return channel_manager.list_channels()

@app.post("/api/channels/crosspost")
async def cross_post(request: PostRequest):
    if not channel_manager:
        return {"error": "ChannelManager not available"}
    return channel_manager.cross_post(request.content, request.channel_ids)

@app.post("/api/channels/schedule")
async def schedule_post(request: PostRequest):
    if not channel_manager:
        return {"error": "ChannelManager not available"}
    job_id = channel_manager.schedule_post(
        request.content, request.channel_ids, request.scheduled_time
    )
    return {"job_id": job_id}


# ═══════════════════════════════════════
# WebSocket (اختياري — يعتمد على runtime)
# ═══════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if not _RUNTIME_AVAILABLE or not runtime_gateway:
        await websocket.close(code=1001)
        return
    await runtime_gateway.connect(websocket)
    try:
        init_state = {
            "type": "init",
            "agents": list(agent_registry.agents.values()),
        }
        await websocket.send_text(json.dumps(init_state))
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("action") == "subscribe":
                await runtime_gateway.subscribe(websocket, msg.get("channel"))
            elif msg.get("action") == "unsubscribe":
                await runtime_gateway.unsubscribe(websocket, msg.get("channel"))
    except WebSocketDisconnect:
        runtime_gateway.disconnect(websocket)


# ═══════════════════════════════════════
# HTML Dashboard
# ═══════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    html_path = os.path.join(BASE_DIR, "webapp", "index.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>🔱 NEXUM API v5.0 — Online</h1><p>Dashboard not found.</p>"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🔱 NEXUM Runtime API v5.0 on port {port}")
    uvicorn.run("api_server:app", host="0.0.0.0", port=port)
