"""
🖥️ PreviewServer — خادم HTTP خفيف لمعاينة التطبيقات
=====================================================
يدير البورتات تلقائياً (8100-8200).
يعمل كـ thread مستقل بدون تعطيل البوت.
"""
import os
import socket
import threading
import http.server
import functools
from typing import Dict, Optional


class PreviewServer:
    """خادم معاينة محلي — يشغّل مجلدات HTML على HTTP"""

    PORT_RANGE = (8100, 8200)

    def __init__(self):
        self._servers: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def start(self, project_name: str, path: str) -> str:
        """
        تشغيل خادم معاينة لمشروع:
        1. يجد بورتاً حراً
        2. يشغّل HTTP server على المجلد
        3. يعيد رابط المعاينة
        """
        with self._lock:
            # إيقاف الخادم القديم إذا وجد
            if project_name in self._servers:
                self._stop_internal(project_name)

            port = self._find_free_port()
            if port is None:
                return "❌ لا توجد بورتات متاحة"

            if not os.path.isdir(path):
                return f"❌ المجلد غير موجود: {path}"

            handler = functools.partial(
                http.server.SimpleHTTPRequestHandler,
                directory=path
            )
            try:
                server = http.server.HTTPServer(("0.0.0.0", port), handler)
            except OSError as e:
                return f"❌ فشل تشغيل الخادم: {e}"

            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()

            self._servers[project_name] = {
                "port": port,
                "thread": t,
                "server": server,
                "path": path,
            }

            url = f"http://localhost:{port}"
            print(f"[Preview] {project_name} → {url}")
            return url

    def stop(self, project_name: str) -> bool:
        """إيقاف خادم معاينة"""
        with self._lock:
            return self._stop_internal(project_name)

    def _stop_internal(self, project_name: str) -> bool:
        info = self._servers.pop(project_name, None)
        if info and info.get("server"):
            try:
                info["server"].shutdown()
            except Exception:
                pass
            return True
        return False

    def list_running(self) -> list:
        """جميع الخوادم النشطة"""
        result = []
        for name, info in self._servers.items():
            result.append({
                "name": name,
                "port": info["port"],
                "path": info["path"],
                "url": f"http://localhost:{info['port']}",
            })
        return result

    def _find_free_port(self) -> Optional[int]:
        """إيجاد بورت حر في النطاق"""
        for port in range(self.PORT_RANGE[0], self.PORT_RANGE[1]):
            # تجاوز البورتات المستخدمة بالفعل
            used = {info["port"] for info in self._servers.values()}
            if port in used:
                continue
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("0.0.0.0", port))
                    return port
            except OSError:
                continue
        return None


# Singleton
preview_server = PreviewServer()
