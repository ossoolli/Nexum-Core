"""
core/env_config.py
مركز المسارات الحقيقية على السيرفر
"""
import os
import subprocess

# ─── المسار الجذري للمشروع ───
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = BASE_DIR

# ─── مجلدات العمل الحقيقية ───
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")   # مكان إنشاء الملفات الجديدة
REGISTRY_DIR  = os.path.join(BASE_DIR, "registry", "apps")  # تطبيقات sub-bots
STORAGE_DIR   = os.path.join(BASE_DIR, "storage")
LOGS_DIR      = os.path.join(BASE_DIR, "logs")
SANDBOX_DIR   = os.path.join(BASE_DIR, "sandbox_runs") # نتائج تشغيل الكود

# ─── إنشاء المجلدات إن لم تكون موجودة ───
for d in [WORKSPACE_DIR, REGISTRY_DIR, STORAGE_DIR, LOGS_DIR, SANDBOX_DIR]:
    os.makedirs(d, exist_ok=True)

# ─── بيئة Python الحالية ───
PYTHON_BIN = os.path.join(BASE_DIR, "venv", "bin", "python3")
if not os.path.exists(PYTHON_BIN):
    PYTHON_BIN = "python3"  # fallback للـ system python

# ─── Git config ───
GIT_AUTO_PUSH = os.getenv("GIT_AUTO_PUSH", "false").lower() == "true"
GIT_REMOTE    = os.getenv("GIT_REMOTE", "origin")
GIT_BRANCH    = os.getenv("GIT_BRANCH", "main")

# ─── دالة تحقق صحة البيئة ───
def verify_environment() -> dict:
    """تتحقق من أن كل المسارات الحقيقية موجودة وصالحة"""
    result = {
        "project_root": os.path.exists(PROJECT_ROOT),
        "workspace":    os.path.exists(WORKSPACE_DIR),
        "python_bin":   os.path.exists(PYTHON_BIN),
        "git_available": False,
        "docker_available": False
    }
    try:
        subprocess.run(["git", "--version"], capture_output=True, timeout=3)
        result["git_available"] = True
    except Exception:
        pass
    try:
        subprocess.run(["docker", "--version"], capture_output=True, timeout=3)
        result["docker_available"] = True
    except Exception:
        pass
    return result
