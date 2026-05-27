# -*- coding: utf-8 -*-
"""
core/sovereign_execution_gateway.py

بوابة التنفيذ السيادي لمجلس الحكماء (Sovereign Execution Gateway).
توفر بيئة عزل صارمة لإدارة الملفات وتشغيل الأوامر بأمان تام مع دعم التواقيع الرقمية ضد التلاعب (Tamper-Evident).
"""

import os
import sys
import re
import shlex
import hmac
import hashlib
import json
import time
import subprocess
from typing import Callable, List, Dict, Any, Optional

# استيراد إعدادات المسارات
from core.env_config import WORKSPACE_DIR, LOGS_DIR

# مفتاح التوقيع الرقمي لسجل العمليات الأمنية (يمكن تهيئته عبر البيئة)
HMAC_KEY = os.getenv("SOVEREIGN_HMAC_KEY", "default_secret_key_for_tamper_proofing")
AUDIT_LOG_PATH = os.path.join(LOGS_DIR, "nexum_audit.log")

# الأوامر المصرح بها فقط
ALLOWED_COMMANDS = {"git", "python", "python3", "pip", "pip3", "ls", "echo", "cat"}

# الأوامر الحساسة التي تتطلب موافقة بشرية (Human-in-the-Loop)
SENSITIVE_COMMANDS = {"pip", "pip3"}

# كاشف حقن الأوامر (Command Injection Detector)
INJECTION_PATTERN = re.compile(r"[;|`><]|&|\$\(")


def sign_log(log_entry: Dict[str, Any]) -> str:
    """
    تقوم بتوليد توقيع رقمي فريد باستخدام HMAC-SHA256 لسجل العمليات لمنع التلاعب.
    Serializes a log entry deterministically and signs it using HMAC-SHA256.
    """
    serialized = json.dumps(log_entry, sort_keys=True)
    return hmac.new(HMAC_KEY.encode("utf-8"), serialized.encode("utf-8"), hashlib.sha256).hexdigest()


def secure_log(action: str, details: Dict[str, Any], status: str) -> Dict[str, Any]:
    """
    تقوم بكتابة سجل أمني مع توقيع رقمي في ملف nexum_audit.log.
    Appends a cryptographically signed security log entry to the audit log.
    """
    log_entry = {
        "timestamp": time.time(),
        "action": action,
        "details": details,
        "status": status
    }
    signature = sign_log(log_entry)
    log_entry["signature"] = signature

    # التأكد من وجود مجلد السجلات
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    return log_entry


def verify_audit_log() -> bool:
    """
    تتحقق من سلامة وصحة ملف سجل العمليات وكشف أي تلاعب بالملف.
    Verifies the integrity of the audit log file. Returns True if unmodified, False otherwise.
    """
    if not os.path.exists(AUDIT_LOG_PATH):
        return True

    try:
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                signature = entry.pop("signature", None)
                if not signature:
                    return False
                
                expected_signature = sign_log(entry)
                if not hmac.compare_digest(signature, expected_signature):
                    return False
        return True
    except Exception:
        return False


def validate_path(path: str, workspace_dir: str = WORKSPACE_DIR) -> str:
    """
    تتحقق من أن المسار المطلوب يقع بالكامل داخل مجلد العمل المعزول (WORKSPACE_DIR).
    يمنع ثغرات تخطي المسار (Path Traversal).
    """
    abs_workspace = os.path.realpath(os.path.abspath(workspace_dir))
    
    if not os.path.isabs(path):
        resolved_path = os.path.realpath(os.path.abspath(os.path.join(abs_workspace, path)))
    else:
        resolved_path = os.path.realpath(os.path.abspath(path))
        
    try:
        common = os.path.commonpath([abs_workspace, resolved_path])
    except ValueError as e:
        # تنشأ في نظام ويندوز في حال وجود محركات أقراص مختلفة
        raise PermissionError(f"🚫 محاولة وصول غير مصرح بها: المسار يقع في محرك أقراص مختلف: {path}") from e
        
    if common != abs_workspace:
        raise PermissionError(f"🚫 محاولة تخطي المسار المعزول (Path Traversal Detected): {path}")
        
    return resolved_path


def validate_command(command_str: str) -> List[str]:
    """
    تتحقق من خلو الأمر من محاولات حقن الأوامر (Command Injection) وأن الأداة مستدعاة من القائمة البيضاء.
    """
    if not command_str or not isinstance(command_str, str):
        raise ValueError("🚫 يجب أن يكون الأمر نصاً غير فارغ.")

    # 1. التحقق من وجود رموز حقن الأوامر في النص الخام
    if INJECTION_PATTERN.search(command_str):
        raise PermissionError(f"🚫 تم كشف محاولة حقن أوامر (Command Injection Detected): {command_str}")

    # 2. تفكيك الأمر إلى عناصر منفصلة (Tokenization)
    try:
        tokens = shlex.split(command_str)
    except Exception as e:
        raise ValueError(f"🚫 فشل تحليل عناصر الأمر: {e}") from e

    if not tokens:
        raise ValueError("🚫 الأمر فارغ بعد التحليل.")

    # 3. التحقق من اسم الأداة الأساسية (Binary)
    binary = tokens[0]
    binary_base = os.path.basename(binary).lower()
    if binary_base.endswith(".exe"):
        binary_base = binary_base[:-4]

    if binary_base not in ALLOWED_COMMANDS:
        raise PermissionError(f"🚫 الأداة المرفقة غير مصرح بها في القائمة البيضاء: {binary_base}")

    # 4. تحقق إضافي على كل عنصر لتأكيد خلوه من رموز الحقن
    for token in tokens:
        if any(char in token for char in (";", "|", "`", ">", "<", "&")) or "$(" in token:
            raise PermissionError(f"🚫 تم كشف محاولة حقن أوامر داخل عناصر الأمر: {token}")

    return tokens


def execute_command(command_str: str, confirm_callback: Optional[Callable[[str], bool]] = None) -> Dict[str, Any]:
    """
    تنفذ أمراً مصرحاً به في بيئة معزولة داخل WORKSPACE_DIR.
    تطلب موافقة يدوية (Human-in-the-Loop) للأوامر الحساسة مثل pip.
    """
    try:
        # التحقق من سلامة الأمر وأنه مصرح به
        tokens = validate_command(command_str)
        binary = os.path.basename(tokens[0]).lower()
        if binary.endswith(".exe"):
            binary = binary[:-4]

        # التعامل مع الأوامر الحساسة (HITL)
        if binary in SENSITIVE_COMMANDS:
            if confirm_callback is None:
                raise PermissionError(
                    f"🚫 الأمر الحساس '{command_str}' يتطلب تأكيداً يدوياً (HITL)، ولكن لم يتم توفير دالة تأكيد."
                )
            
            authorized = confirm_callback(command_str)
            if not authorized:
                secure_log("execute_command", {"command": command_str, "reason": "تم رفض الموافقة البشرية (HITL)"}, "denied")
                raise PermissionError(f"🚫 تم رفض تنفيذ الأمر الحساس بواسطة المستخدم: {command_str}")

        # التأكد من وجود مجلد العمل المعزول
        os.makedirs(WORKSPACE_DIR, exist_ok=True)

        # التنفيذ الفعلي بأمان باستخدام shell=False لمنع التمرير غير المباشر
        result = subprocess.run(
            tokens,
            cwd=WORKSPACE_DIR,
            shell=False,
            capture_output=True,
            text=True,
            timeout=60,
            env=os.environ.copy()
        )

        status = "success" if result.returncode == 0 else "failed"
        details = {
            "command": command_str,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        secure_log("execute_command", details, status)

        return {
            "status": status,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        secure_log("execute_command", {"command": command_str, "error": str(e)}, "failed")
        raise e


def read_file(path: str) -> str:
    """
    تقرأ ملفاً بأمان تام من داخل مسار العمل المعزول فقط.
    """
    resolved_path = validate_path(path, WORKSPACE_DIR)
    
    try:
        with open(resolved_path, "r", encoding="utf-8") as f:
            content = f.read()
        secure_log("read_file", {"path": path, "resolved_path": resolved_path}, "success")
        return content
    except Exception as e:
        secure_log("read_file", {"path": path, "resolved_path": resolved_path, "error": str(e)}, "failed")
        raise e


def write_file(path: str, content: str) -> None:
    """
    تكتب ملفاً بأمان تام داخل مسار العمل المعزول فقط مع إنشاء المجلدات الفرعية تلقائياً.
    """
    resolved_path = validate_path(path, WORKSPACE_DIR)
    
    try:
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
        with open(resolved_path, "w", encoding="utf-8") as f:
            f.write(content)
        secure_log("write_file", {"path": path, "resolved_path": resolved_path}, "success")
    except Exception as e:
        secure_log("write_file", {"path": path, "resolved_path": resolved_path, "error": str(e)}, "failed")
        raise e


def modify_file(path: str, target: str, replacement: str) -> None:
    """
    تعدل ملفاً داخل مسار العمل المعزول باستبدال جزء نصي محدد بجزء آخر بديل.
    """
    resolved_path = validate_path(path, WORKSPACE_DIR)
    
    try:
        with open(resolved_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if target not in content:
            raise ValueError(f"🚫 النص المطلوب استبداله غير موجود في الملف: {path}")
            
        new_content = content.replace(target, replacement)
        
        with open(resolved_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        secure_log("modify_file", {"path": path, "resolved_path": resolved_path}, "success")
    except Exception as e:
        secure_log("modify_file", {"path": path, "resolved_path": resolved_path, "error": str(e)}, "failed")
        raise e
