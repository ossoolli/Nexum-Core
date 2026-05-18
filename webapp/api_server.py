import os
import sys
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from agents.monitor import monitor_agent
from core.executor import executor

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Endpoint for the Mini App dashboard to fetch realtime stats"""
    data = monitor_agent.get_system_data()
    return jsonify(data)

@app.route('/api/execute', methods=['POST'])
def execute_cmd():
    """Endpoint to run commands from the Mini App securely"""
    data = request.json
    cmd = data.get('command')
    if not cmd:
        return jsonify({"status": "error", "output": "No command provided."})
    
    # Needs a real auth mechanism in production, e.g. checking Telegram initData hash.
    # For now, this is a local endpoint MVP.
    result = executor.execute(cmd)
    return jsonify(result)

if __name__ == '__main__':
    print("🌐 NEXUM WebApp API Server running on port 5000...")
    app.run(host='0.0.0.0', port=5000)
