import os
import json
import subprocess
from typing import List, Dict

class BotFleet:
    """
    إدارة أسطول البوتات الفرعية (تشغيل، إيقاف، سرد، تحديث)
    """
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.bots_dir = os.path.join(os.path.dirname(storage_path), 'bots')
        os.makedirs(self.bots_dir, exist_ok=True)
        self._load_bots()

    def _load_bots(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.bots = json.load(f)
            except Exception:
                self.bots = {}
        else:
            self.bots = {}

    def _save_bots(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.bots, f, ensure_ascii=False, indent=4)

    def list_bots(self) -> List[Dict]:
        """سرد جميع البوتات المسجلة وحالتها"""
        self._load_bots()
        for bot_id, info in self.bots.items():
            if info.get('status') == 'RUNNING':
                pid = info.get('pid')
                if pid:
                    if not self._is_pid_running(pid):
                        self.bots[bot_id]['status'] = 'STOPPED'
                        self.bots[bot_id]['pid'] = None
        self._save_bots()
        return list(self.bots.values())

    def _is_pid_running(self, pid: int) -> bool:
        if os.name == 'nt':
            try:
                out = subprocess.check_output(f"tasklist /FI \"PID eq {pid}\"", shell=True).decode()
                return str(pid) in out
            except: return False
        else:
            try:
                os.kill(pid, 0)
                return True
            except OSError: return False

# تهيئة المسارات التلقائية
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bot_fleet = BotFleet(os.path.join(_base_dir, 'storage', 'bots.json'))
