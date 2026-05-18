import os
import psutil
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
import time

# استيراد محركات النواة السيادية
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.agent_registry import agent_registry
from core.orchestrator import orchestrator

app = Flask(__name__)
CORS(app)  # السماح للـ WebApp بالاتصال بسلاسة

@app.route('/')
def index():
    """تقديم الواجهة الرسومية (Sovereign Control Panel)"""
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>Error: index.html not found!</h3>", 404

@app.route('/api/system/stream')
def system_stream():
    """Event Gateway (SSE): بث حي لبيانات استهلاك السيرفر والذاكرة"""
    def generate():
        while True:
            # جمع البيانات الحية من النظام (Live Monitoring)
            data = {
                "cpu": psutil.cpu_percent(interval=None),
                "ram": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(2)  # تحديث كل ثانيتين
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """جلب سجل الوكلاء النشطين وصلاحياتهم وعرضها في البطاقات"""
    return jsonify(list(agent_registry.agents.values()))

@app.route('/api/orchestrate', methods=['POST'])
def trigger_orchestrator():
    """نقطة اتصال لتلقي الأوامر من الـ Command Palette داخل التلجرام"""
    data = request.json
    goal = data.get('goal', '')
    
    if not goal:
        return jsonify({"error": "No goal provided"}), 400
        
    try:
        # إعطاء الهدف للمايسترو للبدء بالتنفيذ الحقيقي
        result = orchestrator.execute_goal(goal)
        return jsonify({
            "status": "success",
            "protocol_id": result.get("protocol", {}).get("protocol_id"),
            "results": result.get("results")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # لتشغيل السيرفر محلياً
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
