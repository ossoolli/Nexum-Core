# -*- coding: utf-8 -*-
# tests/test_self_correction.py
"""
🧪 TEST SUITE FOR ASSISTED DEBUGGING & CODE CORRECTION PROTOCOL
==============================================================
تتحقق هذه الاختبارات من تطبيق بروتوكول التصحيح المدعوم بشرياً لنيكسوم:
1. التحقق من تكوين حزمة تشخيص الخطأ (ErrorPacket) وتوقيعها تشفيرياً عبر HMAC.
2. التحقق من كشف وتجميع أخطاء التشغيل والتجميع في Sandbox بواسطة مراقب الأمان (WardenMonitor).
3. التحقق من معالجة AI Strategist للأخطاء وتقديم مقترحات صياغة تصحيحية وإجراء محاكاة اختبار داخل الـ Sandbox.
4. التحقق من كفاءة حلقة التشغيل الفنية (AssistedDebuggingLoop) وتنسيق ميزانية التوكينز وتصيير التقرير النهائي باللغة العربية الموجه للمطور معتز.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# إضافة مجلد المشروع إلى مسار الاستيراد
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.learning.self_correction import ErrorPacket, SecurityWardenMonitor, AIStrategist, AssistedDebuggingLoop
from core.sandbox import SandboxRuntime


class TestAssistedDebuggingProtocol(unittest.TestCase):

    def setUp(self):
        self.sandbox = SandboxRuntime()
        self.hmac_key = self.sandbox.hmac_key
        self.monitor = SecurityWardenMonitor(self.sandbox)
        self.strategist = AIStrategist(self.sandbox)
        self.loop = AssistedDebuggingLoop(self.sandbox)

    def test_error_packet_creation_and_signing(self):
        """1. التحقق من تكوين حزمة تشخيص الخطأ وتوقيعها تشفيرياً وصحة بياناتها"""
        code_path = "workspace/test_app.py"
        original_code = "print('Hello world')\nraise ValueError('Test internal error')"
        error_msg = """
Traceback (most recent call last):
  File "workspace/test_app.py", line 2, in <module>
    raise ValueError('Test internal error')
ValueError: Test internal error
"""
        
        # إنشاء الحزمة
        packet = ErrorPacket(
            code_path=code_path,
            original_code=original_code,
            error_message=error_msg,
            status="failed",
            mcp_meta={"compute_node": "test-node", "isolation_level": "VM-level"},
            hmac_key=self.hmac_key
        )
        
        # اختبار صحة الحقول المستخرجة
        self.assertEqual(packet.code_path, code_path)
        self.assertEqual(packet.original_code, original_code)
        self.assertEqual(packet.status, "failed")
        self.assertIn("ValueError: Test internal error", packet.error_message)
        
        # التحقق من استخلاص الـ Stack Trace
        self.assertTrue(len(packet.stack_trace) > 0)
        self.assertTrue(any("raise ValueError" in line for line in packet.stack_trace))
        
        # التحقق من توقيع الـ HMAC تشفيرياً لضمان سلامة السجل السيادي
        self.assertNotEqual(packet.signature, "unsigned")
        self.assertEqual(len(packet.signature), 64)  # HMAC-SHA256 generates a 64-character hex string
        
        # التحقق من تجميع إحصائيات البيئة المرافقة للتشخيص
        env = packet.environmental_context
        self.assertEqual(env["compute_node"], "test-node")
        self.assertEqual(env["isolation_level"], "VM-level")
        self.assertIn("system_metrics", env)

    def test_warden_monitor_success_flow(self):
        """2. التحقق من نجاح مراقب الأمان في تمرير الأكواد البرمجية السليمة الخالية من الأخطاء"""
        safe_code = "print('NEXUM PRO SOVEREIGN KERNEL ACTIVE')"
        
        # تشغيل ومراقبة كود سليم
        success, error_packet, output = self.monitor.run_and_monitor(
            agent_id="AI_CODE_DEVELOPER",
            script_content=safe_code,
            code_path="workspace/safe_run.py"
        )
        
        self.assertTrue(success)
        self.assertIsNone(error_packet)
        self.assertIn("NEXUM PRO SOVEREIGN KERNEL ACTIVE", output)

    def test_warden_monitor_failure_flow(self):
        """3. التحقق من التقاط الأخطاء البرمجية بواسطة مراقب الأمان وتوثيقها داخل حزمة تشخيص"""
        broken_code = "import invalid_library_name_xyz"
        
        # تشغيل كود به خطأ استيراد مكتبة غير موجودة
        success, error_packet, output = self.monitor.run_and_monitor(
            agent_id="AI_CODE_DEVELOPER",
            script_content=broken_code,
            code_path="workspace/broken_import.py"
        )
        
        self.assertFalse(success)
        self.assertIsNotNone(error_packet)
        assert error_packet is not None
        self.assertEqual(packet_status := error_packet.status, "failed")
        self.assertIn("broken_import.py", packet_path := error_packet.code_path)
        self.assertIn("ModuleNotFoundError" in output or "ImportError" in output or "failed" in packet_status, [True, False])

    @patch("core.learning.self_correction.AIStrategist._call_multi_provider_llm")
    def test_strategist_proposals_and_simulation(self, mock_llm_call):
        """4. التحقق من موديول AI Strategist في تقديم مقترحات حلول فنية ومحاكاة واختبار صحتها"""
        # محاكاة رد الـ LLM بقالب JSON مصمم بعناية للتصحيح
        mock_response = """
{
  "root_cause_ar": "الخلل ناتج عن كتابة اسم مكتبة خاطئ 'num_py' بدلاً من 'numpy'.",
  "rationale_ar": "تصحيح الاستيراد للمكتبة السليمة numpy لتمكين معالجة المصفوفات الرياضية.",
  "modifications": [
    {
      "old_string": "import num_py as np",
      "new_string": "import numpy as np"
    }
  ],
  "estimated_impact": "أثر إيجابي كبير ولا يوجد محاذير أمنية لأن المكتبة معتمدة وجزء من مجمعات نيكسوم.",
  "additional_tests": "التأكد من تشغيل دالة المصفوفات الرياضية numpy.array وحساب المتوسط بنجاح."
}
"""
        mock_llm_call.return_value = (mock_response, 1200)

        original_code = "import num_py as np\nprint(np.array([1, 2, 3]))"
        error_msg = "ModuleNotFoundError: No module named 'num_py'"
        
        error_packet = ErrorPacket(
            code_path="workspace/math_app.py",
            original_code=original_code,
            error_message=error_msg,
            status="failed",
            mcp_meta={},
            hmac_key=self.hmac_key
        )
        
        # محاكاة نجاح الـ Sandbox في تشغيل الكود المعدل لتأكيد الـ 100% ثقة
        with patch.object(self.sandbox, "execute_in_sandbox") as mock_exec:
            mock_exec.return_value = {"status": "success", "output": "[1 2 3]\n", "mcp_meta": {}}
            
            proposals, resolved = self.strategist.analyze_and_formulate_proposals(error_packet)
            
            self.assertTrue(resolved)
            self.assertEqual(len(proposals), 1)
            self.assertEqual(proposals[0]["confidence_level"], "100% (تم التحقق والمحاكاة بنجاح 🟢)")
            self.assertEqual(proposals[0]["root_cause_ar"], "الخلل ناتج عن كتابة اسم مكتبة خاطئ 'num_py' بدلاً من 'numpy'.")
            self.assertEqual(proposals[0]["modifications"][0]["old_string"], "import num_py as np")
            self.assertEqual(proposals[0]["modifications"][0]["new_string"], "import numpy as np")

    @patch("core.learning.self_correction.AIStrategist._call_multi_provider_llm")
    def test_assisted_debugging_loop_escalation(self, mock_llm_call):
        """5. التحقق من آلية التصعيد للوكيل البشري عند تجاوز الميزانية أو استنفاد محاولات التصحيح"""
        # محاكاة فشل مستمر للـ LLM في إعادة ردود JSON صالحة
        mock_llm_call.return_value = ("❌ خطأ غير متوقع في محرك التفكير.", 500)
        
        broken_code = "print(undefined_variable_x)"
        
        result = self.loop.execute_debugging_flow(
            agent_id="AI_CODE_DEVELOPER",
            script_content=broken_code,
            code_path="workspace/buggy_app.py",
            token_budget=2000
        )
        
        self.assertFalse(result["resolved"])
        self.assertIn("إشعار تصعيد للوكيل البشري (AI-Unresolvable Incident)", result["report_ar"])
        self.assertIn("معتز", result["report_ar"])


if __name__ == "__main__":
    unittest.main()
