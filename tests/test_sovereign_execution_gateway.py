# -*- coding: utf-8 -*-
"""
tests/test_sovereign_execution_gateway.py

الاختبارات الشاملة لبوابة التنفيذ السيادي لمجلس الحكماء (Sovereign Execution Gateway).
تتحقق من صحة عزل المسارات، تصفية حقن الأوامر، الموثوقية الرقمية للسجلات، وتأكيد الموافقات البشرية (HITL).
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import core.sovereign_execution_gateway

from core.sovereign_execution_gateway import (
    validate_path,
    validate_command,
    execute_command,
    read_file,
    write_file,
    modify_file,
    sign_log,
    verify_audit_log,
    AUDIT_LOG_PATH
)
from core.env_config import WORKSPACE_DIR


class TestSovereignExecutionGateway(unittest.TestCase):

    def setUp(self):
        # إنشاء بيئة عمل مؤقتة ومعزولة للاختبارات
        self.test_workspace = tempfile.mkdtemp()
        self.original_workspace = WORKSPACE_DIR
        
        # تغيير مسار WORKSPACE_DIR أمنياً للاختبارات
        import core.sovereign_execution_gateway
        core.sovereign_execution_gateway.WORKSPACE_DIR = self.test_workspace
        
        # إنشاء ملف سجل أمني مؤقت ومستقل للاختبار
        self.test_audit_log_dir = tempfile.mkdtemp()
        self.original_audit_log = AUDIT_LOG_PATH
        core.sovereign_execution_gateway.AUDIT_LOG_PATH = os.path.join(self.test_audit_log_dir, "nexum_audit.log")

    def tearDown(self):
        # تنظيف مجلدات الاختبار المؤقتة
        shutil.rmtree(self.test_workspace)
        shutil.rmtree(self.test_audit_log_dir)
        
        # استعادة المسارات الأصلية
        import core.sovereign_execution_gateway
        core.sovereign_execution_gateway.WORKSPACE_DIR = self.original_workspace
        core.sovereign_execution_gateway.AUDIT_LOG_PATH = self.original_audit_log

    def test_validate_path_allowed(self):
        """التحقق من السماح بالمسارات التي تقع بالكامل داخل مجلد العمل."""
        # مسار نسبي
        path_rel = "subfolder/file.txt"
        resolved = validate_path(path_rel, self.test_workspace)
        self.assertTrue(resolved.startswith(os.path.realpath(self.test_workspace)))
        
        # مسار مطلق داخل المجلد المعزول
        path_abs = os.path.join(self.test_workspace, "another_file.py")
        resolved_abs = validate_path(path_abs, self.test_workspace)
        self.assertEqual(resolved_abs, os.path.realpath(path_abs))

    def test_validate_path_traversal_denied(self):
        """التحقق من حظر محاولات تخطي المسار (Path Traversal) ورفع استثناء."""
        # محاولة تخطي بالمسار النسبي
        with self.assertRaises(PermissionError):
            validate_path("../outside.txt", self.test_workspace)
            
        # محاولة تخطي بالمسار المطلق خارج بيئة العمل
        with self.assertRaises(PermissionError):
            validate_path("/etc/passwd", self.test_workspace)

        # محاولة تخطي على نظام التشغيل ويندوز
        with self.assertRaises(PermissionError):
            validate_path("..\\..\\windows\\system32", self.test_workspace)

    def test_validate_command_whitelisted(self):
        """التحقق من قبول الأوامر المدرجة في القائمة البيضاء وتفكيكها بشكل سليم."""
        tokens = validate_command("python -c \"print('Hello')\"")
        self.assertEqual(tokens[0], "python")
        self.assertEqual(tokens[1], "-c")
        
        tokens_git = validate_command("git status")
        self.assertEqual(tokens_git, ["git", "status"])

    def test_validate_command_non_whitelisted_denied(self):
        """التحقق من حظر الأدوات والبرامج غير المصرح بها أمنياً."""
        non_whitelisted = [
            "rm -rf /",
            "curl https://google.com",
            "wget https://example.com",
            "sh malicious_script.sh",
            "powershell.exe Get-Process"
        ]
        for cmd in non_whitelisted:
            with self.assertRaises(PermissionError, msg=f"Should block: {cmd}"):
                validate_command(cmd)

    def test_validate_command_injection_denied(self):
        """التحقق من حظر محاولات حقن الأوامر باستخدام الرموز الخاصة."""
        injection_attempts = [
            "python -c 'print()' && rm -rf /",
            "ls; rm -rf /",
            "echo hello | python",
            "python -c 'import os; os.system(`ls`)'",
            "git $(rm -rf /)",
            "echo 'hello' > file.txt" # إعادة التوجيه محظورة
        ]
        for cmd in injection_attempts:
            with self.assertRaises(PermissionError, msg=f"Should detect injection in: {cmd}"):
                validate_command(cmd)

    def test_file_operations_success(self):
        """التحقق من عمليات الملفات الأساسية (كتابة، قراءة، وتعديل) داخل المجلد المعزول."""
        file_path = "sub/test_file.txt"
        content = "Line 1: Nexum Sovereign Core\nLine 2: Council of Sages"
        
        # 1. كتابة الملف
        write_file(file_path, content)
        
        # 2. قراءة الملف والتحقق من المطابقة
        read_content = read_file(file_path)
        self.assertEqual(read_content, content)
        
        # 3. تعديل الملف
        modify_file(file_path, "Council of Sages", "Council of Sovereign Sages")
        
        # 4. إعادة القراءة والتحقق من التعديل
        modified_content = read_file(file_path)
        self.assertIn("Council of Sovereign Sages", modified_content)
        self.assertNotIn("Council of Sages\n", modified_content)

    def test_file_operations_traversal_denied(self):
        """التحقق من حظر عمليات الملفات خارج بيئة العمل المعزولة."""
        with self.assertRaises(PermissionError):
            write_file("../malicious.txt", "content")
            
        with self.assertRaises(PermissionError):
            read_file("../malicious.txt")
            
        with self.assertRaises(PermissionError):
            modify_file("../malicious.txt", "target", "replacement")

    @patch("subprocess.run")
    def test_execute_command_success(self, mock_run):
        """التحقق من التنفيذ الناجح للأوامر المصرح بها وتوثيقها."""
        # محاكاة تشغيل ناجح للأمر
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Python 3.10.5"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = execute_command("python --version")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["stdout"], "Python 3.10.5")
        
        # التأكد من استدعاء subprocess بالمعايير الصحيحة
        mock_run.assert_called_once_with(
            ["python", "--version"],
            cwd=core.sovereign_execution_gateway.WORKSPACE_DIR,
            shell=False,
            capture_output=True,
            text=True,
            timeout=60,
            env=unittest.mock.ANY
        )

    def test_execute_command_sensitive_hitl_required(self):
        """التحقق من أن الأوامر الحساسة مثل pip تتطلب موافقة بشرية (HITL)."""
        # بدون دالة تأكيد -> يجب الرفض ورفع استثناء
        with self.assertRaises(PermissionError):
            execute_command("pip install requests")
            
        # مع دالة تأكيد ترجع False -> يجب الرفض ورفع استثناء
        confirm_callback = MagicMock(return_value=False)
        with self.assertRaises(PermissionError):
            execute_command("pip install requests", confirm_callback=confirm_callback)
        confirm_callback.assert_called_once_with("pip install requests")

    @patch("subprocess.run")
    def test_execute_command_sensitive_hitl_approved(self, mock_run):
        """التحقق من تنفيذ الأمر الحساس بعد الحصول على موافقة بشرية بنجاح."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Successfully installed"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        confirm_callback = MagicMock(return_value=True)
        result = execute_command("pip install requests", confirm_callback=confirm_callback)
        
        self.assertEqual(result["status"], "success")
        confirm_callback.assert_called_once_with("pip install requests")
        mock_run.assert_called_once()

    def test_tamper_evident_logging(self):
        """التحقق من أن سجل العمليات مشفر بـ HMAC وتكشف دالة التحقق أي تلاعب."""
        # 1. تنفيذ عمليات لتوليد سجلات
        write_file("audit_test.txt", "Some content")
        
        # السجلات يجب أن تكون سليمة حالياً
        self.assertTrue(verify_audit_log())
        
        # 2. قراءة ملف السجل الفعلي والتلاعب بمحتوياته
        path = core.sovereign_execution_gateway.AUDIT_LOG_PATH
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        self.assertTrue(len(lines) > 0)
        
        # التلاعب ببيانات السجل الأول بتغيير القيمة
        entry = json.loads(lines[0])
        entry["status"] = "hacked_status"  # تعديل الحالة لتجربة التلاعب
        
        # إعادة كتابة السجلات المعدلة دون إعادة حساب التوقيع الرقمي
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
        # التحقق يجب أن يكتشف التلاعب ويرجع False
        self.assertFalse(verify_audit_log())


if __name__ == "__main__":
    unittest.main()
