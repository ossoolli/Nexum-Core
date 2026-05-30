# -*- coding: utf-8 -*-
# tests/test_sandbox_warden.py
"""
🧪 THE SOVEREIGN SANDBOX ARCHITECTURE TEST SUITE — حزمة اختبارات بيئة العزل وموديول الأمان
=====================================================================================
تتحقق هذه الاختبارات من تطبيق قرارات مجلس الحكماء:
1. التحقق من بوابة صلاحيات IAM الدقيقة للوكلاء.
2. التحقق من قدرة موديول Security Warden (SAST) على كشف وحظر الأكواد والوظائف والبرمجيات الخبيثة.
3. التحقق من كشف تسريب المفاتيح ورموز الوصول الحساسة (Secrets Detection) وقياس انتروبيا النصوص.
4. التحقق من تنفيذ الأكواد بأمان ودقة والتراجع لبيئة Subprocess الآمنة عند غياب محرك Docker.
"""

import os
import sys
import unittest

# إضافة مجلد المشروع إلى مسار الاستيراد
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.sandbox import SandboxRuntime, SecurityWarden, AGENT_ROLES


class TestSovereignSandboxArchitecture(unittest.TestCase):

    def setUp(self):
        # إنشاء بيئة تشغيل Sandbox للتحليل والاختبار
        self.sandbox = SandboxRuntime()
        self.warden = self.sandbox.warden

    def test_iam_permissions_enforcement(self):
        """1. التحقق من الإنفاذ الصارم لصلاحيات IAM الدقيقة لمنع تداخل الوكلاء"""
        # وكيل مخول بالكامل (Admin)
        allowed, msg = self.sandbox.check_iam_permission("admin", "nexum:sandbox:create")
        self.assertTrue(allowed)
        self.assertIn("✅", msg)

        # وكيل مطور أكواد مخول بإنشاء وحذف واستلام مخرجات Sandbox الخاصة به
        allowed_dev, msg_dev = self.sandbox.check_iam_permission("AI_CODE_DEVELOPER", "nexum:sandbox:create")
        self.assertTrue(allowed_dev)

        # وكيل مطور أكواد يحاول تنفيذ أمر غير مصرح به (مثلاً ربط مستودع تخزين عشوائي)
        allowed_dev_attach, msg_attach = self.sandbox.check_iam_permission("AI_CODE_DEVELOPER", "nexum:storage:ephemeral:attach")
        self.assertFalse(allowed_dev_attach)
        self.assertIn("🚫", msg_attach)

        # وكيل مجهول أو غير مخول يحاول إنشاء Sandbox
        allowed_hacker, msg_hacker = self.sandbox.check_iam_permission("malicious_agent_x", "nexum:sandbox:create")
        self.assertFalse(allowed_hacker)
        self.assertIn("🚫", msg_hacker)

    def test_sast_dangerous_imports_and_patterns(self):
        """2. التحقق من كشف موديول الأمان (Security Warden) للمستوردات والأنماط الخطيرة"""
        # كود آمن تماماً
        safe_code = """
def calculate_factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * calculate_factorial(n - 1)

print(calculate_factorial(5))
"""
        scan_res = self.warden.scan_code(safe_code)
        self.assertTrue(scan_res["safe"])
        self.assertEqual(len(scan_res["violations"]), 0)

        # كود غير آمن يحاول استدعاء os.system
        unsafe_code_os = """
import os
os.system("rm -rf /")
"""
        scan_res_os = self.warden.scan_code(unsafe_code_os)
        self.assertFalse(scan_res_os["safe"])
        # يجب كشف الانتهاك (سواء استيراد أو نمط)
        self.assertTrue(any("SAST_IMPORT_VIOLATION" in v or "SAST_PATTERN_VIOLATION" in v for v in scan_res_os["violations"]))

        # كود يحاول استخدام eval و subprocess
        unsafe_code_sub = """
import subprocess
result = eval("subprocess.run(['ls'])")
"""
        scan_res_sub = self.warden.scan_code(unsafe_code_sub)
        self.assertFalse(scan_res_sub["safe"])
        self.assertTrue(any("subprocess" in v or "eval" in v for v in scan_res_sub["violations"] + scan_res_sub["secrets"]))

    def test_sast_secrets_and_entropy_detection(self):
        """3. التحقق من كشف تسريب المفاتيح والرموز الحساسة ومستوى الانتروبيا للكود"""
        # كود يحمل مفتاح وصول OpenAI API Key صلباً
        code_with_secret = """
openai_key = "sk-proj-AbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUv"
print("Setting up client...")
"""
        scan_res_sec = self.warden.scan_code(code_with_secret)
        self.assertFalse(scan_res_sec["safe"])
        self.assertTrue(len(scan_res_sec["secrets"]) > 0)
        self.assertTrue(any("SAST_SECRET_DETECTED" in s or "SAST_HIGH_ENTROPY_SECRET" in s for s in scan_res_sec["secrets"]))

    def test_sandbox_execution_and_fallback(self):
        """4. التحقق من تنفيذ الأكواد بنجاح والتراجع الآمن لـ Subprocess عند غياب Docker"""
        # كود بايثون سليم للتنفيذ
        test_script = "print('HELLO FROM NEXUM SOVEREIGN SANDBOX')"
        
        # تنفيذ الكود تحت هوية وكيل مخول
        exec_res = self.sandbox.execute_in_sandbox("AI_CODE_DEVELOPER", test_script)
        
        self.assertIn(exec_res["status"], ["success", "failed"])
        self.assertIn("HELLO FROM NEXUM", exec_res["output"])
        self.assertIsNotNone(exec_res["mcp_meta"])
        
        # التحقق من تسجيل تفاصيل التنسيق وموقع الحوسبة في الميتا داتا
        self.assertIn("compute_node", exec_res["mcp_meta"])
        self.assertIn("storage_volume", exec_res["mcp_meta"])
        self.assertIn("isolation_level", exec_res["mcp_meta"])

    def test_sandbox_execution_blocked_by_warden(self):
        """5. التحقق من أن محاولة تنفيذ كود خبيث تُحجر فوراً وتوقف المعالجة والـ Sandbox كلياً"""
        malicious_script = """
import subprocess
subprocess.run(["echo", "exploit"])
"""
        exec_res = self.sandbox.execute_in_sandbox("AI_CODE_DEVELOPER", malicious_script)
        
        # يجب حظر العملية ووضع الكود في الحجر الأمني
        self.assertEqual(exec_res["status"], "security_blocked")
        self.assertIn("[Security Warden] تم اعتراض الكود وحجره فوراً", exec_res["output"])
        self.assertIsNotNone(exec_res["security_report"])
        self.assertEqual(exec_res["security_report"]["verdict"], "REJECTED_SECURITY")


if __name__ == "__main__":
    unittest.main()
