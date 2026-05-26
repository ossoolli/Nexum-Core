# -*- coding: utf-8 -*-
"""
core/learning/engines.py
محركات ومحللات التعلم المستمر -- Nexum Pro (v7.2.5)
====================================================
- ExperienceAnalyzer: يفكك المأموريات المنتهية لاستخلاص القواعد الوقائية
- PatternExtractor: يراقب التجارب المتراكمة ويحدد الأنماط المتكررة
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from core.memory.sovereign_memory import SovereignMemory


class ExperienceAnalyzer:
    """محلل التجارب: يفكك المأموريات المنتهية جراحيا لاستخلاص الأسباب الجذرية."""

    def __init__(self, memory: SovereignMemory, llm_interface=None):
        self.memory = memory
        self.llm = llm_interface

    def analyze(self, mission: dict) -> dict:
        """تحليل مأمورية منتهية واستخلاص القواعد والخبرات."""
        # 1. صياغة المخرجات الأساسية
        what_happened = {
            "success": mission.get("result") == "success",
            "speed": "normal" if mission.get("duration", 0) < 10 else "slow",
            "intervened": mission.get("user_intervened", False)
        }

        # 2. تحديد السبب الجذري
        why = (
            "Routine successful execution."
            if what_happened["success"]
            else "Action failed or developer overrode the decision."
        )
        if self.llm:
            try:
                prompt = (
                    f"Mission: {mission.get('goal', 'unknown')}\n"
                    f"Result: {mission.get('result', 'unknown')}\n"
                    f"Analyze root cause in one English line."
                )
                response, _ = self.llm.ask(prompt)
                why = response.strip()[:500]
            except Exception:
                pass

        # 3. استخلاص القاعدة الوقائية
        goal_word = "generic"
        if mission.get("goal"):
            words = mission["goal"].split()
            if words:
                goal_word = words[0].lower()

        rule = {
            "condition": f"if_action_contains_{goal_word}",
            "action": (
                "verify_environment_before_execution"
                if not what_happened["success"]
                else "proceed_normally"
            ),
            "reason": why
        }

        experience = {
            "mission_id": mission.get("id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "what_happened": what_happened,
            "root_cause": why,
            "extracted_rule": rule,
            "confidence": 0.90 if what_happened["success"] else 0.50
        }

        # حفظ التجربة في الذاكرة السيادية
        self.memory.add_experience(experience)
        return experience


class PatternExtractor:
    """مستخلص الأنماط: يراقب التجارب المتراكمة ويحدد الأنماط المتكررة."""

    def __init__(self, memory: SovereignMemory):
        self.memory = memory
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> list:
        """تحميل الأنماط المكتشفة سابقا."""
        infra_map = self.memory.infrastructure.map
        return infra_map.get("discovered_patterns", [])

    def scan_for_patterns(self) -> list:
        """فحص التجارب المتراكمة واستخلاص أنماط جديدة."""
        infra_map = self.memory.infrastructure.map
        experiences = infra_map.get("experience_pool", [])
        new_patterns = []

        # يتطلب 3 تجارب على الأقل لبدء استخلاص الأنماط
        if len(experiences) < 3:
            return new_patterns

        existing_descriptions = {p.get("description") for p in self.patterns}

        # 1. فحص أنماط الفشل المتكررة
        failures = [
            e for e in experiences
            if not e.get("what_happened", {}).get("success", True)
        ]
        if len(failures) >= 3:
            desc = f"Detected recurring failures: {len(failures)} incidents recorded."
            if desc not in existing_descriptions:
                new_patterns.append({
                    "type": "recurring_failure",
                    "description": desc,
                    "suggested_fix": "Enable pre-execution checks and apply strict risk constraints.",
                    "confidence": min(len(failures) / 10, 1.0),
                    "discovered_at": datetime.now().isoformat()
                })

        # 2. فحص أنماط البطء المتكررة
        slow_ops = [
            e for e in experiences
            if e.get("what_happened", {}).get("speed") == "slow"
        ]
        if len(slow_ops) >= 3:
            desc = f"Detected slow operations pattern: {len(slow_ops)} slow executions."
            if desc not in existing_descriptions:
                new_patterns.append({
                    "type": "performance_pattern",
                    "description": desc,
                    "suggested_fix": "Optimize execution pipeline or increase timeout thresholds.",
                    "confidence": min(len(slow_ops) / 10, 1.0),
                    "discovered_at": datetime.now().isoformat()
                })

        # 3. فحص أنماط التوقيت
        hour = datetime.now().hour
        timing_desc = f"System stability analysis at hour {hour}:00"
        if timing_desc not in existing_descriptions:
            new_patterns.append({
                "type": "timing_pattern",
                "description": timing_desc,
                "recommendation": "Continue automated low-risk operations.",
                "discovered_at": datetime.now().isoformat()
            })

        # حفظ الأنماط الجديدة
        if new_patterns:
            self.patterns.extend(new_patterns)
            # حصر عدد الأنماط
            self.patterns = self.patterns[-100:]
            self.memory.infrastructure.update_field("discovered_patterns", self.patterns)

        return new_patterns
