# -*- coding: utf-8 -*-
# core/learning/self_correction.py
"""
🔱 ASSISTED DEBUGGING & CODE CORRECTION PROTOCOL (بروتوكول التصحيح البرمجي المدعوم بشرياً)
======================================================================================
المواصفات والمعايير البرمجية المعتمدة من مجلس الحكماء (The Council of Sages):
1. التقاط كامل الـ Stack Trace وسجلات البيئة (Warden Monitoring & Data Capture) عند حدوث خطأ.
2. استخدام محرك AI Strategist لتحليل السبب الجذري وصياغة مقترحات إصلاح باللغة العربية (Assisted Correction).
3. إجراء محاكاة داخلية (Internal Simulation Loop) لاختبار كفاءة التعديلات المقترحة في الـ Sandbox قبل عرضها.
4. فرض قيود صارمة على عدد المحاولات (Max Retries) وميزانية التوكينز (Token Budget) لمنع الحلقات المفرغة.
5. منع التطبيق التلقائي للكود في مستودع العمل، وطلب اعتماد وموافقة المطور البشري (Mutaz) كبوابة أمان إجبارية.
"""

import os
import re
import hmac
import hashlib
import logging
import traceback
import json
from typing import Dict, Any, List, Tuple, Optional

# استيراد موديولات نيكسوم الأساسية
from core.sandbox import SandboxRuntime
from core.llm_factory import llm
from core.llm_engine import llm_engine, openai_engine

logger = logging.getLogger("nexum.self_correction")


class ErrorPacket:
    """
    حزمة تشخيص الخطأ (Error Packet)
    ===============================
    نموذج بيانات يحمل التفاصيل الكاملة للخطأ البرمجي، وسجلات البيئة لتوفير سياق تشخيصي آمن.
    """
    def __init__(self, 
                 code_path: str, 
                 original_code: str, 
                 error_message: str, 
                 status: str, 
                 mcp_meta: Optional[Dict[str, Any]] = None,
                 hmac_key: bytes = b""):
        self.code_path = code_path
        self.original_code = original_code
        self.error_message = error_message
        self.status = status
        self.mcp_meta = mcp_meta or {}
        
        # استخلاص وتجميع سجلات البيئة والـ Stack Trace
        self.stack_trace = self._extract_stack_trace(error_message)
        self.environmental_context = self._gather_env_context()
        self.token_spent = 0
        self.token_budget = 30000  # الحد الأقصى للميزانية الافتراضية
        
        # توقيع الحزمة تشفيرياً لضمان سلامتها ضد التلاعب
        self.signature = self._generate_signature(hmac_key)

    def _extract_stack_trace(self, raw_error: str) -> List[str]:
        """استخلاص أسطر Stack Trace ذات الصلة من الرسالة الخام."""
        lines = raw_error.splitlines()
        trace = []
        in_traceback = False
        for line in lines:
            if "Traceback" in line or "File \"" in line:
                in_traceback = True
            if in_traceback:
                trace.append(line)
        return trace if trace else lines[-10:] if lines else ["Unknown error context"]

    def _gather_env_context(self) -> Dict[str, Any]:
        """جمع الإحصائيات الفنية من بيئة النظام الحالية لوضعها في سياق التشخيص."""
        try:
            import psutil
            cpu_pct = psutil.cpu_percent()
            ram_pct = psutil.virtual_memory().percent
        except ImportError:
            cpu_pct = "N/A"
            ram_pct = "N/A"
            
        return {
            "compute_node": self.mcp_meta.get("compute_node", "mcp-compute-subprocess"),
            "isolation_level": self.mcp_meta.get("isolation_level", "SAST-Warden restricted subprocess"),
            "system_metrics": {
                "cpu_percent": cpu_pct,
                "ram_percent": ram_pct
            }
        }

    def _generate_signature(self, hmac_key: bytes) -> str:
        """توقيع البيانات تشفيرياً لتوثيق سلامتها."""
        if not hmac_key:
            return "unsigned"
        data_to_sign = f"{self.code_path}|{self.status}|{len(self.original_code)}".encode("utf-8")
        return hmac.new(hmac_key, data_to_sign, hashlib.sha256).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """تحويل الكائن إلى قاموس بيانات."""
        return {
            "code_path": self.code_path,
            "original_code": self.original_code,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "status": self.status,
            "environmental_context": self.environmental_context,
            "token_spent": self.token_spent,
            "token_budget": self.token_budget,
            "signature": self.signature
        }


class SecurityWardenMonitor:
    """
    مراقب المأمور الأمني والـ Sandbox (Security Warden Monitor)
    ==========================================================
    يراقب تنفيذ الأكواد البرمجية داخل الـ Sandbox، وعند الكشف عن أخطاء تجميع أو تشغيل،
    يقوم بجمع الأدلة الفنية وبناء حزمة تشخيص الخطأ.
    """
    def __init__(self, sandbox: Optional[SandboxRuntime] = None):
        self.sandbox = sandbox or SandboxRuntime()

    def run_and_monitor(self, agent_id: str, script_content: str, code_path: str) -> Tuple[bool, Optional[ErrorPacket], str]:
        """
        تشغيل الكود داخل الـ Sandbox ومراقبته.
        يعيد: (نجاح العملية: bool، حزمة التشخيص: ErrorPacket في حال الفشل، مخرجات التشغيل: str)
        """
        logger.info(f"🔍 WardenMonitor: Running script for agent [{agent_id}] in sandbox...")
        
        # تنفيذ الكود في البيئة المعزولة
        result = self.sandbox.execute_in_sandbox(agent_id, script_content)
        status = result.get("status")
        output = result.get("output", "")
        mcp_meta = result.get("mcp_meta", {})

        if status == "success":
            logger.info("✅ WardenMonitor: Script executed successfully without errors.")
            return True, None, output

        # في حال حدوث خطأ أو اعتراض أمني أو رفض صلاحيات
        logger.warning(f"⚠️ WardenMonitor: Script execution failed with status: {status}")
        
        # إنشاء حزمة تشخيص الخطأ وتمرير مفتاح HMAC الخاص بالـ Sandbox للتوقيع
        error_packet = ErrorPacket(
            code_path=code_path,
            original_code=script_content,
            error_message=output,
            status=status or "unknown",
            mcp_meta=mcp_meta,
            hmac_key=self.sandbox.hmac_key
        )
        
        return False, error_packet, output


class AIStrategist:
    """
    المخطط والمنظر الذكي لـ نيكسوم (AI Strategist)
    ==============================================
    يقوم بتحليل أسباب الخطأ الجذرية، وإجراء صياغة برمجية تصحيحية (Iterative Self-Correction)،
    وإجراء محاكاة داخلية لاختبار الكود المصحح في الـ Sandbox لضمان سلامته قبل عرضه على المطور البشري.
    """
    def __init__(self, sandbox: Optional[SandboxRuntime] = None):
        self.sandbox = sandbox or SandboxRuntime()
        self.max_proposal_attempts = 3

    def _estimate_tokens(self, text: str) -> int:
        """تقدير استهلاك التوكينز بناءً على طول النص (الاعتماد المحافظ: 1 توكين = 4 محارف)."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def _call_multi_provider_llm(self, prompt: str) -> Tuple[str, int]:
        """
        استدعاء النماذج الذكية مع تطبيق آلية التراجع المتعدد للمزودين (Multi-Provider Fallback)
        لضمان مرونة واستمرارية النظام ومقاومة انقطاع الـ APIs.
        """
        estimated_tokens = self._estimate_tokens(prompt)
        
        # 1. المحاولة الأولى: استخدام Gemini الإقليمي الافتراضي (gemini-2.5-flash)
        logger.info("🤖 AI Strategist: Consulting primary model (Gemini)...")
        try:
            # استخدام ask_gemini من llm_factory
            response = llm.ask_gemini("AI_STRATEGIST", prompt)
            if response and "⚠️ خطأ" not in response and "⚠️ Gemini SDK" not in response:
                total_tokens = estimated_tokens + self._estimate_tokens(response)
                return response, total_tokens
            logger.warning(f"⚠️ Gemini failed or returned warning, trying fallback providers. Response: {response[:100]}...")
        except Exception as e:
            logger.warning(f"⚠️ Primary Gemini provider failed: {e}")

        # 2. المحاولة الثانية: التراجع لـ OpenRouter (Claude-3.5-Sonnet)
        logger.info("🤖 AI Strategist: Falling back to OpenRouter (Claude)...")
        try:
            response, _ = llm_engine.ask(prompt, model="anthropic/claude-sonnet-4")
            if response and "❌ خطأ" not in response:
                total_tokens = estimated_tokens + self._estimate_tokens(response)
                return response, total_tokens
            logger.warning(f"⚠️ OpenRouter failed: {response[:100]}...")
        except Exception as e:
            logger.warning(f"⚠️ Fallback OpenRouter provider failed: {e}")

        # 3. المحاولة الثالثة: التراجع لـ OpenAI (GPT-4o-mini / GPT-4o)
        logger.info("🤖 AI Strategist: Falling back to OpenAI (GPT)...")
        try:
            response, _ = openai_engine.ask(prompt, model="gpt-4o-mini")
            if response and "❌ خطأ" not in response:
                total_tokens = estimated_tokens + self._estimate_tokens(response)
                return response, total_tokens
        except Exception as e:
            logger.error(f"❌ All fallback LLM providers exhausted: {e}")

        return "❌ فشل النظام في الاتصال بجميع مزودي الـ AI المعتمدين.", estimated_tokens

    def _apply_modifications_to_code(self, original_code: str, modifications: List[Dict[str, str]]) -> str:
        """تطبيق التعديلات البرمجية (استبدال النصوص القديمة بالجديدة) في الذاكرة."""
        modified_code = original_code
        for mod in modifications:
            old_str = mod.get("old_string", "")
            new_str = mod.get("new_string", "")
            if old_str and old_str in modified_code:
                modified_code = modified_code.replace(old_str, new_str)
            else:
                logger.warning(f"⚠️ AI Strategist: Old string not found in code during simulation: {old_str[:50]}...")
        return modified_code

    def analyze_and_formulate_proposals(self, error_packet: ErrorPacket) -> Tuple[List[Dict[str, Any]], bool]:
        """
        تحليل حزمة الخطأ، وصياغة مقترحات الحلول الفنية وإجراء محاكاة داخلية لاختبارها.
        يعيد: (قائمة مقترحات الحلول: list، تم الحل بالكامل في المحاكاة: bool)
        """
        logger.info("🧠 AI Strategist: Initiating root cause analysis and proposal formulation...")
        
        proposals = []
        all_resolved = False
        current_code = error_packet.original_code
        current_error = error_packet.error_message
        
        # بدء حلقة المحاكاة والتصحيح الداخلي الذكي (Internal Simulation Loop)
        for attempt in range(self.max_proposal_attempts):
            logger.info(f"🔄 AI Strategist: Simulation Attempt {attempt + 1}/{self.max_proposal_attempts}")
            
            # صياغة محفز تشخيصي دقيق للـ AI باللغة العربية
            prompt = f"""
أنت الـ AI Strategist في نظام التشغيل السيادي NEXUM PRO. مهمتك هي تحليل الخطأ البرمجي الوارد من الـ Sandbox وصياغة مقترح حل دقيق جداً للمطور البشري "معتز".

سياق الملف البرمجي: {error_packet.code_path}
مستوى العزل الحالي: {error_packet.environmental_context['isolation_level']}

مخرجات الخطأ الحالية (Stack Trace & Logs):
{current_error}

الكود البرمجي الحالي الجاري تحليله وتصحيحه:
```python
{current_code}
```

يجب أن تقوم بـ:
1. تحليل السبب الجذري للخطأ البرمجي وشرحه بوضوح تام باللغة العربية.
2. تحديد التعديلات البرمجية المطلوبة بدقة (نص الكود القديم والمستبدل الجديد).
3. تقديم مبررات الحل التقنية ومحاذير الأمان والأداء باللغة العربية.
4. توضيح الأثر المتوقع وتوصية باختبارات إضافية.

يجب أن تعيد الإجابة بصيغة JSON صالحة وصارمة فقط دون أي نصوص تمهيدية أو ختامية (No markdown outside of JSON block, just raw json):
{{
  "root_cause_ar": "تحليل السبب الجذري للمشكلة بالتفصيل باللغة العربية...",
  "rationale_ar": "مبررات اختيار هذا الحل وكيفية معالجته للخطأ...",
  "modifications": [
    {{
      "old_string": "نص الكود القديم الدقيق المراد استبداله (يجب أن يكون فريداً ومطابقاً تماماً لما هو موجود في الملف)",
      "new_string": "نص الكود الجديد المستبدل"
    }}
  ],
  "estimated_impact": "شرح للأثر المتوقع على الأداء والأمان وجوانب المعمارية باللغة العربية...",
  "additional_tests": "اقتراحات لسيناريوهات اختبار إضافية لتغطية هذا الخلل في المستقبل..."
}}
"""
            # التحقق من ميزانية التوكينز المتبقية قبل الاستدعاء
            if error_packet.token_spent >= error_packet.token_budget:
                logger.warning("🚨 AI Strategist: Token budget exceeded! Halting internal simulation loop.")
                break

            # استدعاء الـ LLM
            response_text, tokens_used = self._call_multi_provider_llm(prompt)
            error_packet.token_spent += tokens_used

            if "❌" in response_text:
                logger.error("❌ AI Strategist: LLM connection failure during proposal generation.")
                break

            # تنظيف الرد لاستخلاص الـ JSON
            try:
                # تنظيف علامات الـ markdown للـ json إن وجدت
                cleaned_text = response_text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()
                
                proposal_data = json.loads(cleaned_text)
            except Exception as e:
                logger.error(f"❌ AI Strategist: Failed to parse LLM response as JSON. Error: {e}. Raw response: {response_text[:300]}...")
                continue

            # إجراء المحاكاة الداخلية (Simulating the proposal in sandbox)
            modifications = proposal_data.get("modifications", [])
            if not modifications:
                logger.warning("⚠️ AI Strategist: Proposal has empty modifications.")
                continue

            simulated_code = self._apply_modifications_to_code(current_code, modifications)
            
            # التحقق من الكود المولد عبر المأمور الأمني Security Warden قبل تشغيله في الـ Sandbox
            scan_res = self.sandbox.warden.scan_code(simulated_code)
            if not scan_res["safe"]:
                logger.warning("🛡️ AI Strategist [Security Warden Blocked]: Simulated code violated safety policies during internal testing. Refining...")
                current_error = f"[Security Warden Blocked] The proposed code is UNSAFE. Violations: {', '.join(scan_res['violations'] + scan_res['secrets'])}"
                continue

            # تشغيل الكود المصحح في الـ Sandbox لاختباره
            logger.info("🧪 AI Strategist: Simulating proposed fix in Sandbox...")
            sim_result = self.sandbox.execute_in_sandbox("AI_CODE_DEVELOPER", simulated_code)
            sim_status = sim_result.get("status")
            sim_output = sim_result.get("output", "")

            # إضافة المحاولة لسجل المقترح
            proposal_data["simulation_attempt"] = attempt + 1
            proposal_data["simulation_status"] = sim_status
            proposal_data["simulation_output"] = sim_output[:1000]  # اقتصاص لتجنب تضخم البيانات

            if sim_status == "success":
                logger.info(f"🎉 AI Strategist [SUCCESS]: Proposal validated and passed simulation on attempt {attempt + 1}!")
                proposal_data["confidence_level"] = "100% (تم التحقق والمحاكاة بنجاح 🟢)"
                proposals.append(proposal_data)
                all_resolved = True
                break
            else:
                logger.warning(f"⚠️ AI Strategist: Simulated code failed with error. Output: {sim_output[:200]}")
                proposal_data["confidence_level"] = f"50% (فشلت المحاكاة، الخلل: {sim_status} ❌)"
                proposals.append(proposal_data)
                
                # استخدام الخطأ الجديد لإعادة صياغة الكود تكرارياً (Iterative Self-Correction)
                current_code = simulated_code
                current_error = sim_output

        return proposals, all_resolved


class AssistedDebuggingLoop:
    """
    حلقة وحلقة التصحيح المدعومة بشرياً (Assisted Debugging Loop)
    ============================================================
    المنسق المركزي لبروتوكول التصحيح المدعوم بشرياً لنيكسوم. يجمع بين WardenMonitor و AIStrategist،
    ويتحكم في تدفق العمليات وتتبع ميزانية التوكينز وتوثيق السجلات وتصيير التقارير الموجهة لـ معتز.
    """
    def __init__(self, sandbox: Optional[SandboxRuntime] = None):
        self.sandbox = sandbox or SandboxRuntime()
        self.monitor = SecurityWardenMonitor(self.sandbox)
        self.strategist = AIStrategist(self.sandbox)

    def execute_debugging_flow(self, agent_id: str, script_content: str, code_path: str, token_budget: int = 30000) -> Dict[str, Any]:
        """
        تنفيذ بروتوكول التصحيح والمراقبة بالكامل.
        """
        logger.info(f"🚀 AssistedDebuggingLoop: Starting debugging loop for file [{code_path}]...")
        
        # 1. المراقبة والتشغيل الأولي
        success, error_packet, raw_output = self.monitor.run_and_monitor(agent_id, script_content, code_path)
        
        if success:
            logger.info("🟢 AssistedDebuggingLoop: Script executed successfully in sandbox, no healing needed.")
            return {
                "resolved": True,
                "report_ar": "🟢 تم تشغيل الكود بنجاح داخل بيئة الـ Sandbox دون أي أخطاء تجميع أو تشغيل.",
                "output": raw_output
            }

        # 2. في حال الفشل، تشخيص المشكلة وصياغة المقترحات عبر AI Strategist
        if not error_packet:
            return {
                "resolved": False,
                "report_ar": "❌ حدث خطأ غير متوقع أثناء تشغيل الكود ولم يتمكن النظام من تكوين حزمة التشخيص.",
                "output": raw_output
            }

        # ضبط ميزانية التوكينز لحزمة التشخيص الحالية
        error_packet.token_budget = token_budget
        
        # 3. استدعاء المخطط الذكي للتحليل وصياغة المقترحات في حلقة محاكاة داخلية
        proposals, all_resolved = self.strategist.analyze_and_formulate_proposals(error_packet)
        
        # 4. بناء تقرير التصحيح باللغة العربية (Mutaz Preference)
        report_lines = []
        report_lines.append("🏛️ <b>بروتوكول التصحيح الذاتي والترميم البرمجي المدعوم بشرياً</b>")
        report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        report_lines.append(f"📁 <b>الملف المستهدف:</b> <code>{code_path}</code>")
        report_lines.append(f"🛡️ <b>بوابة الأمان (Warden):</b> تم التقاط الخطأ وتوثيقه تشفيرياً.")
        report_lines.append(f"🔑 <b>توقيع السجل السيادي:</b> <code>{error_packet.signature[:16]}...</code>")
        report_lines.append(f"🔋 <b>استهلاك الطاقة التوكينية:</b> {error_packet.token_spent} / {error_packet.token_budget} Tokens")
        report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━\n")

        if proposals:
            report_lines.append("💡 <b>الحلول والمقترحات الموصى بها من قبل الـ AI Strategist:</b>\n")
            for idx, prop in enumerate(proposals):
                status_icon = "🟢" if "100%" in prop.get("confidence_level", "") else "❌"
                report_lines.append(f"<b>[المقترح {idx + 1}] (مستوى الثقة: {prop.get('confidence_level')})</b>")
                report_lines.append(f"🔍 <b>السبب الجذري للخلل:</b> {prop.get('root_cause_ar')}")
                report_lines.append(f"⚙️ <b>مسببات الحل الفني:</b> {prop.get('rationale_ar')}")
                report_lines.append(f"📊 <b>الأثر المتوقع على النظام:</b> {prop.get('estimated_impact')}")
                report_lines.append(f"🧪 <b>سيناريوهات اختبار موصى بها:</b> {prop.get('additional_tests')}")
                
                # إظهار التعديلات البرمجية المقترحة بشكل واضح وجميل لـ معتز ليعتمدها بنقرة واحدة
                report_lines.append("\n🛠️ <b>التعديل المقترح (Code Modification Suggestion):</b>")
                for mod_idx, mod in enumerate(prop.get("modifications", [])):
                    report_lines.append(f"  <i>تعديل {mod_idx + 1}:</i>")
                    report_lines.append(f"  ❌ <b>البحث عن واستبدال:</b>\n<code>{mod.get('old_string')}</code>")
                    report_lines.append(f"  ✅ <b>بالنص الجديد:</b>\n<code>{mod.get('new_string')}</code>")
                
                # توثيق محاولة المحاكاة الداخلية
                report_lines.append(f"\n🔬 <b>نتائج المحاكاة الداخلية للـ Sandbox:</b>")
                report_lines.append(f"  - المحاولة الرقمية: {prop.get('simulation_attempt')}")
                report_lines.append(f"  - حالة تجميع الكود: {prop.get('simulation_status')}")
                report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━\n")
        else:
            report_lines.append("🚨 <b>إشعار تصعيد للوكيل البشري (AI-Unresolvable Incident):</b>")
            report_lines.append("فشل الـ AI Strategist في صياغة مقترح حل متكامل ومضمون ضمن عدد المحاولات وميزانية التوكينز المحددة.")
            report_lines.append("يرجى تدخل المطور معتز يدوياً لحل المشكلة البرمجية.")
            report_lines.append(f"❌ <b>رسالة الخطأ الخام:</b>\n<code>{raw_output[:500]}</code>")
            report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━\n")

        report_lines.append("👑 <b>القرار النهائي وبوابة الأمان:</b>")
        report_lines.append("🔒 تطبيق التعديلات البرمجية <b>مغلق تماماً</b> بانتظار موافقتك الصريحة واليدوية (Human-Gated Approval) لحماية واستقرار نواة نظام نيكسوم السيادي.")
        
        full_report = "\n".join(report_lines)
        
        return {
            "resolved": all_resolved,
            "error_packet": error_packet.to_dict(),
            "proposals": proposals,
            "report_ar": full_report,
            "raw_output": raw_output
        }


# دالة خلفية متوافقة للاستدعاء والتوافقية الرجعية
def execute_with_reflection(code_path: str, run_command: str = "python3") -> Tuple[bool, str]:
    """
    دالة التوافقية الرجعية (Backwards-compatibility wrapper).
    تستدعي بروتوكول التصحيح والترميم الجديد بالكامل لضمان تشغيل النظام دون أي انكسار للوظائف القديمة.
    """
    logger.info(f"🔄 Backward Compatibility Triggered: Executing self_correction for {code_path}")
    
    # قراءة الكود الحالي المراد تنفيذه وتصحيحه
    try:
        with open(code_path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        return False, f"❌ فشل قراءة الملف البرمجي: {e}"

    loop = AssistedDebuggingLoop()
    result = loop.execute_debugging_flow(
        agent_id="AI_CODE_DEVELOPER",
        script_content=code_content,
        code_path=code_path
    )
    
    # إرجاع حالة النجاح ومخرجات التقرير العربي
    return result["resolved"], result["report_ar"]
