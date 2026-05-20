from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import psutil

app = FastAPI(title="Nexum Mini App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

@app.get("/mini-app")
async def mini_app_view():
    """ تقديم واجهة الـ Mini App لتيليجرام """
    html_path = os.path.join(TEMPLATES_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

@app.websocket("/ws/live")
async def websocket_live_stats(websocket: WebSocket):
    """ إرسال بيانات السيرفر الحية بشكل دوري (RAM / CPU) """
    await websocket.accept()
    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            
            payload = {
                "cpu": cpu,
                "ram": ram,
                "agents_online": 3 # رقم افتراضي حالياً
            }
            await websocket.send_json(payload)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WS Error: {e}")
