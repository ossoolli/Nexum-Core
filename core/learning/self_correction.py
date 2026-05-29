import logging
import traceback
import subprocess

logger = logging.getLogger("nexum.self_correction")

def execute_with_reflection(code_path, run_command="python3"):
    """
    حلقة تصحيح ذاتي: تنفيذ، التقاط خطأ، إصلاح، إعادة تنفيذ.
    """
    max_attempts = 3
    for attempt in range(max_attempts):
        result = subprocess.run([run_command, code_path], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Executed successfully on attempt {attempt + 1}")
            return True, result.stdout
        
        error_msg = result.stderr
        logger.warning(f"⚠️ Attempt {attempt + 1} failed. Analyzing error...")
        # هنا سنربط مع الـ Evolution Engine للـ Reflection
        # ... (سيتم الربط مع Gemini لإصلاح الكود)
    return False, "Failed after max attempts"
