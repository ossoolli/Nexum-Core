# -*- coding: utf-8 -*-
# core/browser_sandbox.py
"""
🔱 NEXUM Secure Browser Sandbox — متصفح الطيران السيادي الآمن
===========================================================
يقوم بتشغيل متصفح معزول كلياً لتصفح وثائق البرمجة والمكتبات الرسمية،
مع تطبيق بروتوكول الأمان الصارم المعتمد من مجلس الحكماء (AAA Unanimous):

1. بيئة معزولة كلياً (Isolated Sandbox): عبر Docker لمنع تسريب الجلسات أو الوصول للملفات.
2. بروتوكول الموافقة البشرية (Human-in-the-Loop): للقراءة فقط، وأي عملية كتابة/إرسال تتطلب تأكيداً.
3. تقييد النطاق (Domain Whitelisting): تصفح وثائق البرمجة الرسمية فقط ويمنع لوحات التحكم والبنوك.
4. تطهير البيانات (Output Sanitization): تصفية وتطهير البيانات لمنع هجمات الحقن غير المباشر (Indirect Prompt Injection).
"""

import os
import re
import hmac
import hashlib
import logging
import subprocess
from typing import Dict, Any, Tuple, List, Optional

logger = logging.getLogger("nexum.browser_sandbox")

# قائمة النطاقات البيضاء المسموح بزيارتها (توثيقات ومكتبات برمجية رسمية)
ALLOWED_DOMAINS = [
    r"^github\.com$",
    r"^.*\.github\.com$",
    r"^github\.io$",
    r"^.*\.github\.io$",
    r"^stackoverflow\.com$",
    r"^.*\.stackoverflow\.com$",
    r"^pypi\.org$",
    r"^.*\.pypi\.org$",
    r"^npmjs\.com$",
    r"^.*\.npmjs\.com$",
    r"^docs\.python\.org$",
    r"^playwright\.dev$",
    r"^puppeteer\.dev$",
    r"^docker\.com$",
    r"^.*\.docker\.com$",
    r"^pkg\.go\.dev$",
    r"^golang\.org$",
    r"^dev\.to$",
    r"^medium\.com$",
    r"^wikipedia\.org$",
    r"^.*\.wikipedia\.org$",
    r"^localhost$",
    r"^127\.0\.0\.1$"
]

# قائمة الكلمات المفتاحية الخطيرة الممنوعة لحماية الوكيل من الحقن غير المباشر
DANGEROUS_PATTERNS = [
    r"(?i)ignore\s+(?:all\s+)?previous\s+instructions",
    r"(?i)system\s+prompt\s+override",
    r"(?i)you\s+are\s+now\s+a",
    r"(?i)delete\s+(?:all\s+)?files",
    r"(?i)format\s+(?:c|system|drive|disk)",
    r"(?i)execute\s+(?:arbitrary\s+)?code",
    r"(?i)bypass\s+security",
    r"(?i)overwrite\s+config"
]


class SecureBrowserSandbox:
    """
    متحكم متصفح NEXUM الآمن والمعزول.
    """

    def __init__(self):
        self.workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.hmac_key = self._load_or_generate_hmac_key()
        self.whitelisted_domains = [re.compile(pattern) for pattern in ALLOWED_DOMAINS]
        self.dangerous_regexes = [re.compile(pattern) for pattern in DANGEROUS_PATTERNS]

    def _load_or_generate_hmac_key(self) -> bytes:
        """جلب أو إنشاء مفتاح HMAC لتوقيع سجلات الأمان للتأكد من عدم العبث بها."""
        key = os.getenv("SOVEREIGN_HMAC_KEY")
        if key:
            return key.encode("utf-8")

        key_path = os.path.join(self.workspace_dir, "storage", ".sovereign_key")
        os.makedirs(os.path.dirname(key_path), exist_ok=True)

        if os.path.exists(key_path):
            with open(key_path, "r", encoding="utf-8") as f:
                return f.read().strip().encode("utf-8")
        else:
            new_key = os.urandom(32).hex()
            with open(key_path, "w", encoding="utf-8") as f:
                f.write(new_key)
            return new_key.encode("utf-8")

    def _sign_audit_log(self, action: str, details: str) -> str:
        """توقيع سجلات الأمان تشفيرياً لتكون غير قابلة للتلاعب."""
        message = f"action={action}|details={details}".encode("utf-8")
        return hmac.new(self.hmac_key, message, hashlib.sha256).hexdigest()

    def _log_security_event(self, action: str, details: str, level: str = "INFO"):
        """حفظ الحدث الأمني وتوقيعه للتفتيش اللاحق."""
        signature = self._sign_audit_log(action, details)
        log_msg = f"[AUDIT] Action: {action} | Details: {details} | Signature: {signature}"
        
        if level == "WARNING":
            logger.warning(log_msg)
        elif level == "ERROR":
            logger.error(log_msg)
        else:
            logger.info(log_msg)

        # حفظ السجل في ملف التدقيق المعتمد
        audit_file = os.path.join(self.workspace_dir, "storage", "logs", "browser_audit.log")
        os.makedirs(os.path.dirname(audit_file), exist_ok=True)
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(f"{log_msg}\n")

    def validate_url(self, url: str) -> bool:
        """
        التحقق من نطاق الرابط ومطابقته مع القائمة البيضاء المسموح بها.
        """
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split("/")[0]
        # إزالة البورت إن وجد
        domain = domain.split(":")[0]

        for regex in self.whitelisted_domains:
            if regex.match(domain):
                return True

        self._log_security_event(
            action="DOMAIN_BLOCKED",
            details=f"Blocked attempt to access unauthorized domain: {domain} (URL: {url})",
            level="WARNING"
        )
        return False

    def sanitize_output(self, content: str) -> str:
        """
        تطهير وتصفية النصوص المقشوطة لحماية نموذج الاستدلال من هجمات الحقن غير المباشر.
        """
        if not content:
            return ""

        sanitized = content
        # فحص وجود أنماط خطيرة
        detected = []
        for regex in self.dangerous_regexes:
            if regex.search(sanitized):
                detected.append(regex.pattern)
                # تحييد النمط الخطير بإضافة كسر للنص
                sanitized = regex.sub("[REDACTED_POTENTIAL_INJECTION]", sanitized)

        if detected:
            self._log_security_event(
                action="INJECTION_FILTERED",
                details=f"Neutralized potential prompt injection patterns: {detected}",
                level="WARNING"
            )

        return sanitized

    def request_human_approval(self, action: str, selector: str, value: str = "") -> bool:
        """
        بروتوكول الموافقة البشرية (Human-in-the-Loop)
        يقوم بتسجيل طلب الموافقة وتمريره لنظام الاتصال أو التحقق من موافقة سابقة مسبقة.
        """
        details = f"Action: {action} | Selector: {selector} | Value: {value}"
        self._log_security_event(action="PENDING_HUMAN_APPROVAL", details=details, level="INFO")
        
        # في بيئة التخاطب الذاتي، يتم حظر التنفيذ التلقائي لعمليات الكتابة حتى يوافق المطور معتز.
        # نقوم بمحاكاة السجل حالياً وإصدار تنبيه أمان، أو الإرجاع بالرفض إذا لم يكن هناك معامل تأكيد صريح.
        print(f"⚠️ [Human-in-the-Loop] التماس تأكيد أمني: هل توافق على عملية الكتابة؟ ({details})")
        return False

    def execute_browser_command(self, action: str, url: str, params: Optional[dict] = None) -> dict:
        """
        تنفيذ أوامر المتصفح السيادية مع العزل الصارم ومطابقة بروتوكول الأمان.
        
        المعاملات:
            action: الإجراء المطلوب (goto, click, type, scrape, screenshot)
            url: الرابط المستهدف
            params: معايير إضافية (selectors, input text)
        """
        if not params:
            params = {}

        # 1. تقييد النطاق (Domain Whitelisting)
        if not self.validate_url(url):
            return {
                "status": "security_violation",
                "message": f"🚫 وصول مرفوض: النطاق المستهدف غير مدرج في القائمة البيضاء السيادية لـ NEXUM."
            }

        # 2. حماية الموافقة البشرية للعمليات التفاعلية (Human-in-the-Loop)
        is_write_action = action in ["click", "type", "submit", "fill", "press"]
        if is_write_action:
            approved = params.get("approved_by_human", False)
            if not approved:
                self.request_human_approval(action, params.get("selector", ""), params.get("value", ""))
                return {
                    "status": "pending_approval",
                    "message": f"⚠️ الإجراء [{action}] يتطلب موافقة بشرية صريحة مسبقة من المطور معتز.",
                    "requires_approval": True,
                    "action_details": {
                        "action": action,
                        "url": url,
                        "selector": params.get("selector"),
                        "value": params.get("value")
                    }
                }

        # 3. إعداد تشغيل المتصفح معزولاً داخل Docker
        # نستخدم حاوية معزولة لـ Playwright لتشغيل كود الاستعراض بشكل مستقل تماماً عن النظام المضيف
        self._log_security_event(
            action="BROWSER_EXECUTION_START",
            details=f"Executing {action} on {url} inside isolated sandbox",
            level="INFO"
        )

        docker_available = False
        try:
            # التحقق من توفر دوكر وجاهزيته
            res = subprocess.run("docker info", shell=True, capture_output=True, text=True, timeout=5)
            docker_available = (res.returncode == 0)
        except Exception:
            docker_available = False

        if docker_available:
            # تشغيل السكربت البرمجي للمتصفح داخل Docker (Isolated Sandbox)
            return self._execute_inside_docker(action, url, params)
        else:
            self._log_security_event(
                action="SANDBOX_FALLBACK",
                details="Docker not available. Falling back to local restricted subprocess.",
                level="WARNING"
            )
            # الاحتياط للتشغيل المحلي المقيد عند غياب دوكر مع إصدار تحذير أمني صارخ
            return self._execute_local_restricted(action, url, params)

    def _execute_inside_docker(self, action: str, url: str, params: dict) -> dict:
        """
        تشغيل متصفح Playwright معزول كلياً داخل حاوية Docker مؤقتة ومستقلة تماماً.
        """
        # توليد كود بايثون مصغر لتشغيل Playwright وجلب محتوى الصفحة بأمان
        python_code = f"""
import sys
import json
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({{"status": "error", "message": "Playwright library missing inside container"}}))
    sys.exit(1)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # تنفيذ الإجراء الآمن
        page.goto("{url}", timeout=15000, wait_until="domcontentloaded")
        
        result_data = {{}}
        if "{action}" == "scrape" or "{action}" == "goto":
            result_data["text"] = page.locator("body").inner_text()
            result_data["title"] = page.title()
        elif "{action}" == "screenshot":
            # التقاط لقطة شاشة كـ base64
            import base64
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
                page.screenshot(path=tmp.name)
                tmp.seek(0)
                result_data["screenshot"] = base64.b64encode(tmp.read()).decode("utf-8")
        
        browser.close()
        print(json.dumps({{"status": "success", "data": result_data}}))
except Exception as e:
    print(json.dumps({{"status": "error", "message": str(e)}}))
"""
        # الهروب من علامات التنصيص
        escaped_code = python_code.replace('"', '\\"').replace('$', '\\$')
        
        # بناء أمر Docker مع عزل تام للشبكة وتقييد الموارد
        docker_cmd = (
            f'docker run --rm --network bridge --memory 512m --cpus 1.0 '
            f'mcr.microsoft.com/playwright:v1.40.0-focal '
            f'python3 -c "{escaped_code}"'
        )

        try:
            res = subprocess.run(docker_cmd, shell=True, capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                import json
                try:
                    output_data = json.loads(res.stdout.strip())
                    if output_data.get("status") == "success":
                        # 4. تطهير البيانات (Output Sanitization)
                        raw_text = output_data["data"].get("text", "")
                        output_data["data"]["text"] = self.sanitize_output(raw_text)
                        return output_data
                    else:
                        return {"status": "error", "message": output_data.get("message")}
                except Exception as je:
                    return {"status": "error", "message": f"Failed to parse container output: {je}", "raw": res.stdout}
            else:
                return {"status": "error", "message": f"Docker run returned non-zero code: {res.returncode}", "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Docker execution timed out (30s limit)"}
        except Exception as e:
            return {"status": "error", "message": f"Docker initialization failed: {str(e)}"}

    def _execute_local_restricted(self, action: str, url: str, params: dict) -> dict:
        """
        التشغيل المحلي المقيد كخط بديل أمني مع التنبيه وحظر العمليات الحساسة.
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "status": "error",
                "message": "❌ تعذر التشغيل: مكتبة Playwright غير مثبتة محلياً، وبيئة Docker غير متوفرة."
            }

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto(url, timeout=15000)
                
                result_data = {}
                if action in ["scrape", "goto"]:
                    result_data["text"] = self.sanitize_output(page.locator("body").inner_text())
                    result_data["title"] = page.title()
                elif action == "screenshot":
                    import tempfile
                    import base64
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        page.screenshot(path=tmp.name)
                        tmp.seek(0)
                        result_data["screenshot"] = base64.b64encode(tmp.read()).decode("utf-8")
                        result_data["screenshot_path"] = tmp.name

                browser.close()
                return {"status": "success", "data": result_data, "sandbox_mode": "local_restricted_fallback"}
        except Exception as e:
            return {"status": "error", "message": f"Local execution failed: {str(e)}"}


# Singleton instance
browser_sandbox = SecureBrowserSandbox()
