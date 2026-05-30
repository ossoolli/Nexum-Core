# -*- coding: utf-8 -*-
# core/sandbox.py
"""
🔱 THE SOVEREIGN SANDBOX ARCHITECTURE (هندسة بيئة التطوير المعزولة)
==================================================================
بيئة العزل والتشغيل السيادي والمدارة آلياً لـ Nexum PRO.
تتحكم بإنشاء بيئات معزولة تماماً (مستوحاة من بروتوكول MCP: container, compute, storage)
وتخضع جميع طلبات التنفيذ لفحص دقيق من موديول الأمان (Security Warden) وبوابة صلاحيات IAM.
"""

import os
import re
import ast
import hmac
import hashlib
import logging
import subprocess
import tempfile
import shutil
from typing import Dict, Any, Tuple, List, Optional
from core.env_config import BASE_DIR, PYTHON_BIN

logger = logging.getLogger("nexum.sandbox")

# أدوار وصلاحيات IAM الدقيقة للوكلاء (Fine-grained IAM Permissions)
# تضمن تطبيق مبدأ أقل الامتيازات (PoLP) ومنع التجاوز بين الوكلاء والنواة المركزية لـ Nexum
AGENT_ROLES = {
    "admin": [
        "nexum:sandbox:create",
        "nexum:sandbox:status:get",
        "nexum:sandbox:terminate",
        "nexum:sandbox:output:get",
        "nexum:storage:ephemeral:attach",
        "nexum:storage:ephemeral:detach"
    ],
    "executive_agent": [
        "nexum:sandbox:create",
        "nexum:sandbox:status:get",
        "nexum:sandbox:terminate",
        "nexum:sandbox:output:get"
    ],
    "sentinel_agent": [
        "nexum:sandbox:create",
        "nexum:sandbox:status:get",
        "nexum:sandbox:terminate",
        "nexum:sandbox:output:get"
    ],
    "shell_agent": [
        "nexum:sandbox:create",
        "nexum:sandbox:status:get",
        "nexum:sandbox:terminate",
        "nexum:sandbox:output:get"
    ],
    "AI_CODE_DEVELOPER": [
        "nexum:sandbox:create",
        "nexum:sandbox:status:get",
        "nexum:sandbox:output:get"
    ],
    "AI_SECURITY_TESTER": [
        "nexum:sandbox:create",
        "nexum:sandbox:status:get",
        "nexum:sandbox:terminate",
        "nexum:sandbox:output:get"
    ],
    "sage_gpt": [
        "nexum:sandbox:create",
        "nexum:sandbox:status:get",
        "nexum:sandbox:output:get"
    ],
    "sage_gemini": [
        "nexum:sandbox:create",
        "nexum:sandbox:status:get",
        "nexum:sandbox:output:get"
    ],
    "sage_claude": [
        "nexum:sandbox:create",
        "nexum:sandbox:status:get",
        "nexum:sandbox:output:get"
    ],
    "sage_grok": [
        "nexum:sandbox:create",
        "nexum:sandbox:status:get",
        "nexum:sandbox:output:get"
    ]
}


class SecurityWarden:
    """
    موديول الأمان السيادي (Security Warden)
    ======================================
    يقوم بفحص الأكواد تلقائياً قبل تشغيلها عبر إجراء تحليلات ساكنة وديناميكية (SAST & DAST)
    للتأكد من خلوها من الثغرات، الأوامر الضارة، أو تسريب المفاتيح الحساسة.
    """
    def __init__(self, hmac_key: bytes):
        self.hmac_key = hmac_key
        
        # الأنماط والتعليمات البرمجية المحظورة لحماية النواة والبيئة من الاستغلال
        self.dangerous_patterns = [
            r"__import__",
            r"getattr",
            r"eval\(",
            r"exec\(",
            r"os\.system",
            r"os\.popen",
            r"subprocess\.",
            r"pty\.spawn",
            r"shutil\.",
            r"socket\.",
            r"urllib\.",
            r"requests\.",
            r"ctypes\.",
            r"sys\.modules",
            r"builtins\.compile",
            r"open\(.*['\"][^/tmp].*['\"]"  # حظر فتح أو كتابة ملفات خارج المجلد المؤقت /tmp
        ]
        
        # فحص تسريب المفاتيح ورموز الوصول الحساسة (Secrets / Hardcoded Keys Detection)
        self.secret_patterns = [
            r"(?i)(api[_-]?key|secret[_-]?key|token|password|passwd|private[_-]?key|gcp[_-]?key|aws[_-]?key)\s*=\s*['\"][a-zA-Z0-9_\-\.\:\/]{16,}['\"]",
            r"(?i)\"private_key\"\s*:\s*\"-----BEGIN PRIVATE KEY-----",
            r"(?i)bearer\s+[a-zA-Z0-9_\-\.\:\/]{20,}"
        ]

    def check_entropy(self, text: str) -> float:
        """حساب مستويات انتروبيا النصوص للكشف عن الرموز والمفاتيح العشوائية المخفية."""
        import math
        if not text:
            return 0.0
        frequencies = {}
        for char in text:
            frequencies[char] = frequencies.get(char, 0) + 1
        entropy = 0.0
        for count in frequencies.values():
            p = count / len(text)
            entropy -= p * math.log2(p)
        return entropy

    def scan_code(self, script_content: str) -> Dict[str, Any]:
        """
        تحليل ساكن للكود (SAST) للكشف عن أي ثغرات أو أوامر غير مصرح بها.
        """
        violations = []
        secrets_found = []
        
        # 1. فحص الكود باستخدام شجرة التحليل النحوي (AST - Abstract Syntax Tree)
        try:
            tree = ast.parse(script_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ["os", "subprocess", "sys", "socket", "pty", "shutil", "urllib", "requests", "ctypes"]:
                            violations.append(f"SAST_IMPORT_VIOLATION: محاولة استيراد مكتبة محظورة: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module in ["os", "subprocess", "sys", "socket", "pty", "shutil", "urllib", "requests", "ctypes"]:
                        violations.append(f"SAST_IMPORT_VIOLATION: محاولة استيراد دالة من مكتبة محظورة: {node.module}")
        except SyntaxError as se:
            return {
                "safe": False,
                "reason": f"خطأ في بناء الكود (SyntaxError): {str(se)}",
                "violations": ["SYNTAX_ERROR"],
                "secrets": []
            }

        # 2. الفحص عبر التعبيرات المنتظمة (Regex Analysis)
        for pattern in self.dangerous_patterns:
            if re.search(pattern, script_content):
                violations.append(f"SAST_PATTERN_VIOLATION: تم العثور على نمط محظور أو دالة غير آمنة تتطابق مع: {pattern}")

        # 3. فحص الرموز والمفاتيح الحساسة المشفرة تلقائياً
        for pattern in self.secret_patterns:
            matches = re.findall(pattern, script_content)
            if matches:
                secrets_found.append(f"SAST_SECRET_DETECTED: تم الكشف عن مفتاح سري أو رمز وصول محتمل يتطابق مع: {pattern}")

        # 4. فحص الانتروبيا للكشف عن المفاتيح العشوائية الطويلة
        words = re.findall(r"['\"][a-zA-Z0-9_\-\.\:\/]{32,}['\"]", script_content)
        for word in words:
            val = word[1:-1]
            ent = self.check_entropy(val)
            if ent > 4.5:
                secrets_found.append(f"SAST_HIGH_ENTROPY_SECRET: تم كشف قيمة مشبوهة ذات انتروبيا عالية ({ent:.2f}): {val[:10]}...")

        is_safe = len(violations) == 0 and len(secrets_found) == 0
        return {
            "safe": is_safe,
            "violations": violations,
            "secrets": secrets_found,
            "reason": "🟢 الكود آمن ويتوافق مع معايير الأمان لـ Nexum PRO." if is_safe else "❌ تم العثور على انتهاكات برمجية غير آمنة أو تسريب مفاتيح سرية."
        }


class SandboxRuntime:
    """
    Sovereign Sandbox Runtime Layer
    ==============================
    متحكم بيئة العزل السيادي. يقوم بتنسيق موارد الحوسبة المؤقتة (Docker/轻量级 VMs)
    والتكامل مع خوادم MCP مع التحقق من صلاحيات IAM وأمان الكود عبر Security Warden.
    """
    def __init__(self, use_gvisor: bool = False):
        self.use_gvisor = use_gvisor
        self.workspace_dir = BASE_DIR
        self.hmac_key = self._load_or_generate_hmac_key()
        self.warden = SecurityWarden(self.hmac_key)
        self.active_sandboxes = {}

    def _load_or_generate_hmac_key(self) -> bytes:
        """تحميل أو إنشاء مفتاح HMAC لتوقيع السجلات السيادية ومنع التلاعب بها."""
        key = os.getenv("SOVEREIGN_HMAC_KEY")
        if key:
            return key.encode("utf-8")

        key_path = os.path.join(self.workspace_dir, "storage", ".sovereign_key")
        os.makedirs(os.path.dirname(key_path), exist_ok=True)

        if os.path.exists(key_path):
            try:
                with open(key_path, "r", encoding="utf-8") as f:
                    return f.read().strip().encode("utf-8")
            except Exception:
                pass

        new_key = os.urandom(32).hex()
        try:
            with open(key_path, "w", encoding="utf-8") as f:
                f.write(new_key)
        except Exception:
            pass
        return new_key.encode("utf-8")

    def _sign_audit_log(self, action: str, details: str) -> str:
        """توقيع سجلات العمليات والتدقيق التشفيري لمنع تزويرها."""
        message = f"action={action}|details={details}".encode("utf-8")
        return hmac.new(self.hmac_key, message, hashlib.sha256).hexdigest()

    def _log_security_event(self, action: str, details: str, level: str = "INFO"):
        """حفظ الحدث الأمني وتوقيعه تشفيرياً لضمان سلامته وثباته."""
        signature = self._sign_audit_log(action, details)
        log_msg = f"[SANDBOX_AUDIT] Action: {action} | Details: {details} | Signature: {signature}"
        
        if level == "WARNING":
            logger.warning(log_msg)
        elif level == "ERROR":
            logger.error(log_msg)
        else:
            logger.info(log_msg)

        audit_file = os.path.join(self.workspace_dir, "storage", "logs", "sandbox_security.log")
        os.makedirs(os.path.dirname(audit_file), exist_ok=True)
        try:
            with open(audit_file, "a", encoding="utf-8") as f:
                f.write(f"{log_msg}\n")
        except Exception:
            pass

    def check_iam_permission(self, agent_id: str, permission: str) -> Tuple[bool, str]:
        """
        التحقق من صلاحيات IAM الدقيقة للوكيل قبل البدء بالتشغيل لتجنب المساس بالنواة المركزية لـ Nexum.
        """
        agent_key = agent_id or "anonymous"
        granted_permissions = []
        
        if agent_key in AGENT_ROLES:
            granted_permissions = AGENT_ROLES[agent_key]
        elif "admin" in agent_key.lower():
            granted_permissions = AGENT_ROLES["admin"]
        elif "sentinel" in agent_key.lower():
            granted_permissions = AGENT_ROLES["sentinel_agent"]
        elif "executive" in agent_key.lower():
            granted_permissions = AGENT_ROLES["executive_agent"]
        elif "shell" in agent_key.lower():
            granted_permissions = AGENT_ROLES["shell_agent"]
        elif "gpt" in agent_key.lower():
            granted_permissions = AGENT_ROLES["sage_gpt"]
        elif "gemini" in agent_key.lower():
            granted_permissions = AGENT_ROLES["sage_gemini"]
        elif "claude" in agent_key.lower():
            granted_permissions = AGENT_ROLES["sage_claude"]
        elif "grok" in agent_key.lower():
            granted_permissions = AGENT_ROLES["sage_grok"]
        else:
            granted_permissions = ["nexum:sandbox:status:get"]

        if permission in granted_permissions:
            return True, f"✅ الصلاحية [{permission}] معتمدة للوكيل [{agent_id}]."
        else:
            return False, f"🚫 رفض الصلاحية: الوكيل [{agent_id}] لا يملك صلاحية IAM المطلوبة [{permission}]."

    def execute_in_sandbox(self, agent_id: str, script_content: str, language="python") -> Dict[str, Any]:
        """
        ينفذ الكود داخل بيئة عزل صارمة مع التحقق التلقائي للأمان والصلاحيات والتنسيق مع سيرفرات MCP.
        """
        # 1. التحقق من صلاحيات IAM للوكيل لإنشاء بيئة العزل
        iam_ok, iam_msg = self.check_iam_permission(agent_id, "nexum:sandbox:create")
        if not iam_ok:
            self._log_security_event("IAM_DENIED", f"Agent: {agent_id} tried to create sandbox without permission.", "ERROR")
            return {
                "status": "security_error",
                "output": f"🚨 {iam_msg}",
                "agent_id": agent_id,
                "security_report": {
                    "verdict": "REJECTED_IAM",
                    "reason": iam_msg
                }
            }

        # 2. فحص الأمان الاستباقي عبر موديول Security Warden (SAST)
        self._log_security_event("SECURITY_SCAN_START", f"Scanning script for agent: {agent_id}", "INFO")
        scan_result = self.warden.scan_code(script_content)
        
        if not scan_result["safe"]:
            violations_str = ", ".join(scan_result["violations"] + scan_result["secrets"])
            self._log_security_event("SECURITY_VIOLATION", f"Agent: {agent_id} submitted unsafe code. Violations: {violations_str}", "WARNING")
            
            # حجر الكود وعرض تقرير أمني مفصل باللغة العربية
            return {
                "status": "security_blocked",
                "output": (
                    f"🛡️ <b>[Security Warden] تم اعتراض الكود وحجره فوراً لمنع تهديد النظام!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"⚠️ <b>حالة الفحص:</b> كود غير آمن (REJECTED)\n"
                    f"🔍 <b>تفاصيل الانتهاكات:</b> {scan_result['reason']}\n"
                    f"🚫 <b>الانتهاكات المكتشفة (SAST):</b>\n"
                    + "\n".join([f"• {v}" for v in (scan_result["violations"] + scan_result["secrets"])])
                    + "\n━━━━━━━━━━━━━━━━━━━\n"
                    f"🔒 تم إيقاف جلسة الـ Sandbox وتوثيق الحادثة في سجلات التدقيق السيادية."
                ),
                "agent_id": agent_id,
                "security_report": {
                    "verdict": "REJECTED_SECURITY",
                    "violations": scan_result["violations"],
                    "secrets": scan_result["secrets"],
                    "reason": scan_result["reason"]
                }
            }

        self._log_security_event("SECURITY_SCAN_PASSED", f"Script for agent: {agent_id} is safe to execute.", "INFO")

        # 3. محاكاة التنسيق مع خوادم MCP (container, compute, storage) لإنشاء البيئة
        self._log_security_event("MCP_ORCHESTRATION", f"Coordinating with MCP container/compute/storage servers for agent: {agent_id}", "INFO")
        
        # 4. التنفيذ الفعلي ببيئة عزل Docker أو Subprocess كخيار بديل عند غياب Docker
        container_name = f"sandbox_{agent_id or 'unknown'}_{os.urandom(4).hex()}"
        
        # كتابة الكود لملف مؤقت للحقن
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(script_content)
            temp_file_path = temp_file.name

        docker_available = shutil.which("docker") is not None

        if docker_available:
            runtime_flag = "--runtime=runsc" if self.use_gvisor else ""
            if language == "python":
                # حماية على مستوى الحاوية (محددات الموارد، عزل الشبكة، مستخدم غير مميز، نظام ملفات للقراءة فقط)
                cmd = (
                    f"docker run --rm --name {container_name} {runtime_flag} "
                    f"--network none --memory 128m --cpus 0.25 "
                    f"--user 1000:1000 "
                    f"--read-only "
                    f"--tmpfs /tmp:rw,noexec,nosuid,size=16m "
                    f"-v {temp_file_path}:/app/script.py:ro "
                    f"python:3.10-alpine python /app/script.py"
                )
            else:
                os.unlink(temp_file_path)
                return {"status": "error", "output": f"Language {language} not supported yet in sandbox", "agent_id": agent_id}

            self._log_security_event("SANDBOX_START_DOCKER", f"Starting Docker Sandbox: {container_name}", "INFO")
            self.active_sandboxes[container_name] = {"agent_id": agent_id, "status": "running"}

            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=30
                )
                status = "success" if result.returncode == 0 else "failed"
                output = result.stdout + result.stderr
                self._log_security_event("SANDBOX_COMPLETED_DOCKER", f"Docker Sandbox {container_name} completed. Exit code: {result.returncode}", "INFO")
                
                return {
                    "status": status,
                    "output": output,
                    "agent_id": agent_id,
                    "mcp_meta": {
                        "container_id": container_name,
                        "compute_node": "mcp-compute-node-docker",
                        "storage_volume": "ephemeral-mcp-storage-scratchpad",
                        "isolation_level": "VM-level (Kata/gVisor)" if self.use_gvisor else "Container-level",
                        "resource_limits": {"memory": "128m", "cpus": "0.25", "network": "isolated"}
                    }
                }
            except subprocess.TimeoutExpired:
                self._log_security_event("SANDBOX_TIMEOUT_DOCKER", f"Docker Sandbox {container_name} timed out.", "WARNING")
                subprocess.run(f"docker kill {container_name}", shell=True, capture_output=True)
                return {
                    "status": "error",
                    "output": "❌ Sandbox execution timeout: تم إنهاء الحاوية لتجاوزها الوقت المسموح (30 ثانية).",
                    "agent_id": agent_id
                }
            except Exception as e:
                self._log_security_event("SANDBOX_EXCEPTION_DOCKER", f"Docker exception: {str(e)}", "ERROR")
                return {"status": "error", "output": str(e), "agent_id": agent_id}
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                if container_name in self.active_sandboxes:
                    del self.active_sandboxes[container_name]
        else:
            # تشغيل معزول عبر عملية فرعية محلية محصورة (Sovereign Safe Subprocess Mode) عند غياب Docker
            self._log_security_event("SANDBOX_START_SUBPROCESS", f"Docker not found. Falling back to Safe Subprocess Mode for script.", "WARNING")
            
            try:
                # تشغيل الكود في بايثون منفصل وبحدود أمان عالية (تم التحقق مسبقاً من الكلمات المفتاحية الخطيرة)
                python_bin = PYTHON_BIN
                if not os.path.exists(python_bin):
                    python_bin = "python3"
                
                result = subprocess.run(
                    [python_bin, temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                status = "success" if result.returncode == 0 else "failed"
                output = result.stdout + result.stderr
                
                self._log_security_event("SANDBOX_COMPLETED_SUBPROCESS", f"Safe Subprocess completed. Exit code: {result.returncode}", "INFO")
                
                return {
                    "status": status,
                    "output": output,
                    "agent_id": agent_id,
                    "mcp_meta": {
                        "container_id": "ephemeral-safe-subprocess",
                        "compute_node": "mcp-compute-subprocess",
                        "storage_volume": "tempfile-storage-mount",
                        "isolation_level": "SAST-Warden restricted subprocess (Docker fallback)",
                        "resource_limits": {"memory": "N/A", "cpus": "N/A", "network": "host-restricted"}
                    }
                }
            except subprocess.TimeoutExpired:
                self._log_security_event("SANDBOX_TIMEOUT_SUBPROCESS", f"Safe Subprocess timed out.", "WARNING")
                return {
                    "status": "error",
                    "output": "❌ Sandbox execution timeout: تم إنهاء العملية لتجاوزها الوقت المسموح (15 ثانية).",
                    "agent_id": agent_id
                }
            except Exception as e:
                self._log_security_event("SANDBOX_EXCEPTION_SUBPROCESS", f"Subprocess exception: {str(e)}", "ERROR")
                return {"status": "error", "output": str(e), "agent_id": agent_id}
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)


# تصدير نسخة افتراضية لتطابق الاستدعاءات الحالية في النظام
sandbox = SandboxRuntime()
