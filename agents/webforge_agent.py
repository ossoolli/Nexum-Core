"""
🌐 WebForge Agent — محرك إنشاء المواقع والتطبيقات
===================================================
يبني HTML/CSS/JS, Dashboard, FastAPI بأمر نصي واحد.
يرث من BaseAgent.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.base_agent import BaseAgent

APPS_DIR = os.path.join(BASE_DIR, "registry", "apps")
TEMPLATES_DIR = os.path.join(BASE_DIR, "storage", "templates")
os.makedirs(APPS_DIR, exist_ok=True)


class WebForgeAgent(BaseAgent):
    """مهندس ويب — ينشئ مواقع وتطبيقات كاملة"""

    def __init__(self):
        super().__init__(
            name="webforge",
            description="ينشئ مواقع وتطبيقات ويب من وصف نصي",
            version="1.0"
        )

    def run(self, input_data: dict) -> dict:
        build_type = input_data.get("type", "landing")
        if build_type == "landing":
            return self.build_landing_page(
                input_data.get("project_name", "my_app"),
                input_data.get("description", ""),
                input_data.get("color_scheme", "blue"),
                input_data.get("sections"),
            )
        elif build_type == "dashboard":
            return self.build_dashboard(
                input_data.get("project_name", "my_dashboard"),
                input_data.get("data_schema", {}),
                input_data.get("widgets", ["cards", "table"]),
            )
        elif build_type == "api":
            return self.build_fastapi_app(
                input_data.get("project_name", "my_api"),
                input_data.get("endpoints", []),
            )
        return {"status": "error", "error": f"Unknown type: {build_type}"}

    # ═══════════════════════════════════════
    # بناء صفحة هبوط
    # ═══════════════════════════════════════

    def build_landing_page(
        self,
        project_name: str,
        description: str,
        color_scheme: str = "blue",
        sections: list = None
    ) -> dict:
        """ينشئ صفحة هبوط HTML كاملة"""
        try:
            sections = sections or ["hero", "features", "contact"]
            safe_name = project_name.replace(" ", "_").lower()
            proj_dir = os.path.join(APPS_DIR, safe_name)
            os.makedirs(proj_dir, exist_ok=True)

            # محاولة استخدام LLM
            html = self._generate_with_llm(safe_name, description, color_scheme, sections)
            if not html:
                html = self._generate_from_template(safe_name, description, color_scheme, sections)

            path = os.path.join(proj_dir, "index.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)

            self.log(f"Landing page built: {safe_name}")
            self.record_metric("sites_built", self.metrics.get("sites_built", 0) + 1)

            # تشغيل المعاينة
            preview_url = ""
            try:
                from core.preview_server import preview_server
                preview_url = preview_server.start(safe_name, proj_dir)
            except Exception:
                pass

            return {
                "status": "success",
                "project": safe_name,
                "path": path,
                "size_bytes": os.path.getsize(path),
                "preview_url": preview_url,
            }
        except Exception as e:
            self.log(f"Build failed: {e}", level="ERROR")
            return {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════
    # بناء لوحة تحكم
    # ═══════════════════════════════════════

    def build_dashboard(
        self,
        project_name: str,
        data_schema: dict = None,
        widgets: list = None
    ) -> dict:
        """ينشئ لوحة تحكم HTML"""
        try:
            safe_name = project_name.replace(" ", "_").lower()
            proj_dir = os.path.join(APPS_DIR, safe_name)
            os.makedirs(proj_dir, exist_ok=True)

            widgets = widgets or ["cards", "table"]
            html = self._build_dashboard_html(safe_name, data_schema or {}, widgets)

            path = os.path.join(proj_dir, "index.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)

            self.log(f"Dashboard built: {safe_name}")
            return {"status": "success", "project": safe_name, "path": path}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════
    # بناء FastAPI
    # ═══════════════════════════════════════

    def build_fastapi_app(
        self,
        app_name: str,
        endpoints_schema: list = None
    ) -> dict:
        """ينشئ تطبيق FastAPI كامل"""
        try:
            safe_name = app_name.replace(" ", "_").lower()
            proj_dir = os.path.join(APPS_DIR, safe_name)
            os.makedirs(proj_dir, exist_ok=True)

            endpoints = endpoints_schema or [
                {"method": "GET", "path": "/", "description": "الصفحة الرئيسية"},
                {"method": "GET", "path": "/health", "description": "فحص صحة"},
            ]

            # main.py
            main_code = self._build_fastapi_code(safe_name, endpoints)
            with open(os.path.join(proj_dir, "main.py"), "w", encoding="utf-8") as f:
                f.write(main_code)

            # requirements.txt
            with open(os.path.join(proj_dir, "requirements.txt"), "w") as f:
                f.write("fastapi>=0.100.0\nuvicorn[standard]\npydantic>=2.0\n")

            # Dockerfile
            with open(os.path.join(proj_dir, "Dockerfile"), "w") as f:
                f.write(f"FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\n"
                        f"RUN pip install -r requirements.txt\n"
                        f"CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n")

            self.log(f"FastAPI app built: {safe_name}")
            return {"status": "success", "project": safe_name, "path": proj_dir}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════
    # المشاريع والمعاينة
    # ═══════════════════════════════════════

    def serve_local(self, project_name: str, port: int = None) -> str:
        """تشغيل معاينة محلية"""
        try:
            from core.preview_server import preview_server
            proj_dir = os.path.join(APPS_DIR, project_name)
            return preview_server.start(project_name, proj_dir)
        except Exception as e:
            return f"❌ فشل تشغيل المعاينة: {e}"

    def list_projects(self) -> list:
        """جميع المشاريع"""
        try:
            projects = []
            for name in os.listdir(APPS_DIR):
                proj_dir = os.path.join(APPS_DIR, name)
                if os.path.isdir(proj_dir):
                    files = os.listdir(proj_dir)
                    projects.append({
                        "name": name,
                        "files": len(files),
                        "has_html": "index.html" in files,
                        "has_api": "main.py" in files,
                    })
            return projects
        except Exception:
            return []

    # ═══════════════════════════════════════
    # مولّدات داخلية
    # ═══════════════════════════════════════

    def _generate_with_llm(self, name, desc, colors, sections):
        """محاولة استخدام Gemini لتوليد HTML"""
        try:
            from services.gemini_service import GeminiService
            svc = GeminiService(os.getenv("GOOGLE_API_KEY"))
            prompt = (
                f"أنشئ صفحة HTML5 كاملة ومكتفية بذاتها لمشروع '{name}'.\n"
                f"الوصف: {desc}\n"
                f"نظام الألوان: {colors}\n"
                f"الأقسام: {', '.join(sections)}\n\n"
                "المتطلبات: HTML كامل في ملف واحد مع CSS مدمج. "
                "تصميم احترافي Responsive. لا مكتبات خارجية. "
                "أعد الكود فقط بدون شرح — ابدأ بـ <!DOCTYPE html>"
            )
            res, _ = svc.ask(prompt)
            if res and "<!DOCTYPE" in res.upper() or "<html" in res.lower():
                # تنظيف markdown fences
                import re
                res = re.sub(r'^```(?:html)?\s*', '', res.strip())
                res = re.sub(r'\s*```$', '', res.strip())
                return res
        except Exception as e:
            self.log(f"LLM generation failed, using template: {e}", level="WARNING")
        return None

    def _generate_from_template(self, name, desc, colors, sections):
        """توليد HTML من قالب ثابت"""
        color_map = {
            "blue": ("#1a73e8", "#f8f9fa"), "green": ("#0d9488", "#f0fdf4"),
            "dark": ("#6366f1", "#0f172a"), "red": ("#dc2626", "#fef2f2"),
            "gold": ("#d97706", "#fffbeb"),
        }
        primary, bg = color_map.get(colors, color_map["blue"])
        text_color = "#ffffff" if colors == "dark" else "#1f2937"

        sects = ""
        if "hero" in sections:
            sects += f'''<section style="padding:80px 20px;text-align:center;background:linear-gradient(135deg,{primary},#667eea);color:#fff">
<h1 style="font-size:3em;margin:0">{name.replace('_',' ').title()}</h1>
<p style="font-size:1.3em;margin:20px 0;opacity:0.9">{desc or "مشروع متميز"}</p>
<a href="#features" style="background:#fff;color:{primary};padding:14px 36px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;margin-top:10px">اكتشف المزيد</a>
</section>\n'''
        if "features" in sections:
            sects += f'''<section id="features" style="padding:60px 20px;background:{bg};text-align:center">
<h2 style="color:{primary};margin-bottom:40px">المميزات</h2>
<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:30px;max-width:1000px;margin:auto">
<div style="background:#fff;padding:30px;border-radius:16px;width:280px;box-shadow:0 4px 20px rgba(0,0,0,0.08)">
<div style="font-size:2.5em">⚡</div><h3>سرعة فائقة</h3><p>أداء عالٍ وتجربة سلسة</p></div>
<div style="background:#fff;padding:30px;border-radius:16px;width:280px;box-shadow:0 4px 20px rgba(0,0,0,0.08)">
<div style="font-size:2.5em">🛡️</div><h3>أمان متقدم</h3><p>حماية بيانات بمعايير عالمية</p></div>
<div style="background:#fff;padding:30px;border-radius:16px;width:280px;box-shadow:0 4px 20px rgba(0,0,0,0.08)">
<div style="font-size:2.5em">🌐</div><h3>دعم شامل</h3><p>متاح على جميع الأجهزة</p></div>
</div></section>\n'''
        if "contact" in sections:
            sects += f'''<section style="padding:60px 20px;background:{primary};text-align:center;color:#fff">
<h2>تواصل معنا</h2><p style="margin:10px">نسعد بسماعك</p>
<a href="mailto:info@example.com" style="background:#fff;color:{primary};padding:12px 30px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;margin-top:15px">📧 راسلنا</a>
</section>\n'''

        return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{name.replace('_',' ').title()}</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Segoe UI',Tahoma,sans-serif;color:{text_color};line-height:1.7}}</style>
</head><body>{sects}
<footer style="padding:20px;text-align:center;background:#1f2937;color:#9ca3af;font-size:0.9em">
🔱 Built by NEXUM WebForge | © 2026</footer></body></html>'''

    def _build_dashboard_html(self, name, schema, widgets):
        """توليد لوحة تحكم HTML"""
        cards = ""
        if "cards" in widgets:
            cards = '''<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:30px">
<div class="card"><h3>📊</h3><p>إجمالي</p><span>1,234</span></div>
<div class="card"><h3>📈</h3><p>نشط</p><span>856</span></div>
<div class="card"><h3>⏳</h3><p>معلّق</p><span>78</span></div>
<div class="card"><h3>✅</h3><p>مكتمل</p><span>300</span></div></div>'''

        table = ""
        if "table" in widgets:
            table = '''<table style="width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 15px rgba(0,0,0,0.05)">
<thead><tr style="background:#667eea;color:#fff"><th style="padding:12px">المعرّف</th><th>الاسم</th><th>الحالة</th><th>التاريخ</th></tr></thead>
<tbody><tr><td style="padding:10px;border-bottom:1px solid #eee">#001</td><td>عنصر أول</td><td>🟢 نشط</td><td>2026-01-01</td></tr>
<tr><td style="padding:10px;border-bottom:1px solid #eee">#002</td><td>عنصر ثاني</td><td>🟡 معلّق</td><td>2026-01-05</td></tr></tbody></table>'''

        return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{name} Dashboard</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Segoe UI',sans-serif;background:#f1f5f9;color:#1f2937}}
.sidebar{{width:240px;background:#1e293b;color:#fff;height:100vh;position:fixed;padding:20px}}
.sidebar h2{{margin-bottom:30px;color:#818cf8}}.sidebar a{{display:block;color:#94a3b8;padding:10px;text-decoration:none;border-radius:8px;margin:4px 0}}
.sidebar a:hover{{background:#334155;color:#fff}}.main{{margin-right:260px;padding:30px}}
.card{{background:#fff;padding:24px;border-radius:16px;text-align:center;box-shadow:0 2px 15px rgba(0,0,0,0.05)}}
.card span{{font-size:2em;font-weight:bold;color:#667eea;display:block;margin-top:8px}}</style>
</head><body>
<div class="sidebar"><h2>🔱 {name}</h2>
<a href="#">📊 لوحة التحكم</a><a href="#">👥 المستخدمون</a><a href="#">⚙️ الإعدادات</a></div>
<div class="main"><h1 style="margin-bottom:25px">📊 لوحة تحكم {name}</h1>
{cards}{table}</div></body></html>'''

    def _build_fastapi_code(self, name, endpoints):
        """توليد كود FastAPI"""
        routes = ""
        for ep in endpoints:
            method = ep.get("method", "GET").lower()
            path = ep.get("path", "/")
            desc = ep.get("description", "")
            routes += f'''
@app.{method}("{path}")
async def {path.strip('/').replace('/','_') or 'root'}():
    """{desc}"""
    return {{"status": "ok", "endpoint": "{path}"}}\n'''

        return f'''"""
🚀 {name} — Generated by NEXUM WebForge
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{name}", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
{routes}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''


# Singleton
webforge = WebForgeAgent()
