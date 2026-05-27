# -*- coding: utf-8 -*-
"""
🧬 SovereignEvolutionEngine — محرك التطور والترميم السيادي الذاتي (v1.0.0)
========================================================================
- يقوم بمسح ملفات السجلات والأخطاء لاكتشاف أي انهيار في الوكلاء المولدة.
- يقرأ سياق المحادثات الأخيرة لتحديد الفجوات المعرفية أو الأدوات المفقودة.
- يقوم بالترميم التلقائي للأكواد (Self-Healing Code Repair) وإصلاح الأخطاء ذاتياً عبر Gemini.
- يولد تلقائياً مواصفات وكلاء جدد ويسجلهم لحل الفجوات المكتشفة.
"""

import os
import re
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from services.gemini_service import gemini_service
from core.agent_registry import agent_registry

logger = logging.getLogger(__name__)

class SovereignEvolutionEngine:
    def __init__(self, sovereign_memory=None, council=None):
        self.memory = sovereign_memory
        self.council = council
        self.evolution_log_path = os.path.join(BASE_DIR, "storage", "logs", "evolution.log")
        os.makedirs(os.path.dirname(self.evolution_log_path), exist_ok=True)

    def log_evolution(self, message: str, level: str = "INFO"):
        """تسجيل خاص بمسار التطور الذاتي"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}\n"
        try:
            with open(self.evolution_log_path, "a", encoding="utf-8") as f:
                f.write(line)
        except:
            pass
        logger.info(f"[Evolution] {message}")

    def run_diagnostics_and_evolve(self, admin_id: int) -> dict:
        """تشغيل دورة الفحص الشاملة والتطوير الذاتي"""
        self.log_evolution("Starting autonomous diagnostics and evolution cycle...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "scanned_errors": 0,
            "repaired_agents": [],
            "discovered_gaps": [],
            "spawned_agents": [],
            "status": "nominal"
        }

        # 1. ──── الترميم التلقائي للأكواد (Self-Healing Code Repair) ────
        try:
            repaired = self.scan_and_repair_broken_agents()
            report["repaired_agents"] = repaired
            report["scanned_errors"] = len(repaired)
            if repaired:
                self.log_evolution(f"Self-healing successfully repaired agents: {', '.join(repaired)}")
        except Exception as e:
            self.log_evolution(f"Self-healing scan error: {e}", level="ERROR")

        # 2. ──── مسح الفجوات المعرفية وبناء وكلاء جدد ────
        try:
            gaps = self.scan_capability_gaps(admin_id)
            report["discovered_gaps"] = gaps
            
            for gap in gaps:
                self.log_evolution(f"Discovered capability gap: '{gap['objective']}'. Initiating agent synthesis.")
                spawned = self.synthesize_agent_for_gap(gap["agent_name"], gap["objective"])
                if spawned:
                    report["spawned_agents"].append(spawned)
                    self.log_evolution(f"Autonomously synthesized and registered agent: {spawned}")
        except Exception as e:
            self.log_evolution(f"Capability evolution error: {e}", level="ERROR")

        # 3. ──── حفظ تقرير التطور ────
        try:
            history_path = os.path.join(BASE_DIR, "storage", "sovereign_memory", "evolution_history.json")
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            history = []
            if os.path.exists(history_path):
                with open(history_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            
            history.append(report)
            if len(history) > 30:
                history.pop(0)
                
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.log_evolution(f"Failed to save history: {e}", level="ERROR")

        return report

    # ═══════════════════════════════════════════════════════
    # 1. الترميم التلقائي للأكواد (Self-Healing)
    # ═══════════════════════════════════════════════════════
    def scan_and_repair_broken_agents(self) -> List[str]:
        """فحص السجلات لإصلاح الوكلاء المعطوبين ذاتياً"""
        repaired_names = []
        err_log_path = os.path.join(BASE_DIR, "storage", "logs", "err.log")
        
        if not os.path.exists(err_log_path):
            return repaired_names

        try:
            with open(err_log_path, "r", encoding="utf-8") as f:
                error_content = f.read()
        except:
            return repaired_names

        # البحث عن استثناءات بايثون التي تشير لـ generated agents
        # مثال: Traceback ... in generated/xxx_agent.py
        agent_error_pattern = r"agents[\\/]generated[\\/](\w+)_agent\.py"
        matches = re.findall(agent_error_pattern, error_content)
        if not matches:
            return repaired_names

        # استبعاد المكرر
        broken_agents = list(set(matches))
        
        for agent_name in broken_agents:
            agent_file = os.path.join(BASE_DIR, "agents", "generated", f"{agent_name}_agent.py")
            if not os.path.exists(agent_file):
                continue
                
            self.log_evolution(f"⚠️ Detected crash/error in agent file: {agent_file}. Initiating repair...")
            
            # جلب آخر 50 سطر من الخطأ المتعلق بالوكيل
            lines = error_content.splitlines()
            related_error = []
            for line in reversed(lines):
                if f"{agent_name}_agent.py" in line or "Error" in line or "Exception" in line:
                    related_error.append(line)
                if len(related_error) > 15:
                    break
            related_error_str = "\n".join(reversed(related_error))

            # قراءة الكود الحالي للوكيل
            try:
                with open(agent_file, "r", encoding="utf-8") as f:
                    current_code = f.read()
            except:
                continue

            # طلب إصلاح الكود من Gemini
            prompt = (
                f"You are the Sovereign Self-Healing Engine of NEXUM PRO. "
                f"A generated agent has crashed with the following traceback:\n"
                f"----------------------------------------\n"
                f"{related_error_str}\n"
                f"----------------------------------------\n\n"
                f"Here is the current code of the agent ({agent_name}_agent.py):\n"
                f"```python\n"
                f"{current_code}\n"
                f"```\n\n"
                f"Analyze the error, fix the bugs (e.g. missing imports, syntax, logical errors), "
                f"and return the complete, corrected Python code for the agent.\n"
                f"Rules:\n"
                f"1. Make sure to preserve imports and subclassing of BaseAgent.\n"
                f"2. Return ONLY the raw Python code. Start with 'import' and do not add any markdown blocks or explanations."
            )

            repaired_code, _ = gemini_service.ask(prompt)
            if not repaired_code or "class" not in repaired_code:
                self.log_evolution(f"❌ Failed to get a valid repaired code for {agent_name}", level="WARNING")
                continue

            # تنظيف كود البلوك
            repaired_code = re.sub(r'^```(?:python)?\s*', '', repaired_code.strip())
            repaired_code = re.sub(r'\s*```$', '', repaired_code.strip())
            repaired_code = repaired_code.strip()

            # حفظ الكود المصلح
            try:
                with open(agent_file, "w", encoding="utf-8") as f:
                    f.write(repaired_code)
                self.log_evolution(f"🛡️ Successfully patched agent file: {agent_file}")
                repaired_names.append(agent_name)
            except Exception as e:
                self.log_evolution(f"❌ Failed to write patch for {agent_name}: {e}", level="ERROR")

        return repaired_names

    # ═══════════════════════════════════════════════════════
    # 2. كشف الفجوات المعرفية (Capability Gaps)
    # ═══════════════════════════════════════════════════════
    def scan_capability_gaps(self, admin_id: int) -> List[dict]:
        """البحث في سياق المحادثات الأخيرة عن فجوات معرفية أو مأموريات مفقودة"""
        gaps = []
        try:
            from core.memory_local import context_memory
            history = context_memory.get_context(admin_id)
        except:
            return gaps

        if not history:
            return gaps

        # تحويل المحادثة الأخيرة لنص واحد لتحليله
        conversation_text = ""
        for msg in history[-8:]:  # آخر 8 رسائل
            role = msg.get("role", "user")
            content = msg.get("parts", [{}])[0].get("text", "") if msg.get("parts") else ""
            conversation_text += f"{role}: {content}\n"

        prompt = (
            f"You are the Sovereign Evolution Engine of NEXUM PRO.\n"
            f"Analyze the following recent conversation history and identify if the user explicitly or implicitly "
            f"requested a capability, a task, or a specialized monitoring agent that is NOT supported or currently built in the system.\n\n"
            f"Conversation:\n{conversation_text}\n"
            f"Respond with a JSON list of gaps. If no gaps are found or the system already fully supports them, return an empty list `[]`.\n\n"
            f"Format:\n"
            f'[\n'
            f'  {{\n'
            f'    "agent_name": "اسم_الوكيل_المناسب (e.g. crypto_tracker)",\n'
            f'    "objective": "الدور الدقيق للوكيل (e.g. monitor crypto rates and alert when high)"\n'
            f'  }}\n'
            f']'
        )

        try:
            res, _ = gemini_service.ask(prompt)
            json_match = re.search(r'\[.*\]', res, re.DOTALL)
            if json_match:
                gaps = json.loads(json_match.group())
        except Exception as e:
            self.log_evolution(f"Failed to parse capability gaps: {e}", level="WARNING")

        return gaps

    def synthesize_agent_for_gap(self, agent_name: str, objective: str) -> Optional[str]:
        """توليد وكيل جديد لسد الثغرة المكتشفة وتفعيله فوراً"""
        try:
            from agents.agent_smith import agent_smith
            safe_name = agent_name.replace(" ", "_").lower()
            
            # 1. تصميم
            spec_res = agent_smith.design_agent(
                safe_name, 
                purpose=f"وكيل سيادي مستقل مولد تلقائياً للقيام بـ: {objective}", 
                tools_needed=["search_web", "fetch_webpage"], 
                triggers=["every_hour"]
            )
            if spec_res.get("status") != "success":
                return None
                
            # 2. بناء
            filepath = agent_smith.build_agent(safe_name)
            if "❌" in filepath or not os.path.exists(filepath):
                return None

            # 3. تسجيل
            reg_ok = agent_smith.register_agent(safe_name)
            if reg_ok:
                return safe_name
        except Exception as e:
            self.log_evolution(f"Autonomous synthesis failed for {agent_name}: {e}", level="ERROR")
        return None
