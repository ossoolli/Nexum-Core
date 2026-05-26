# -*- coding: utf-8 -*-
"""
core/memory/sovereign_memory.py
الواجهة السيادية الموحدة لإدارة الذاكرة -- Nexum Pro (v7.2.5)
==============================================================
تستدعيها النواة لدمج سياق المحطة والقرارات السابقة مع معالج الذكاء الاصطناعي.
تعتمد على المكونات الفرعية المعزولة في components.py.
"""

import os
import json
from datetime import datetime
from typing import Any

from core.memory.components import InfrastructureMap, DecisionMemory, MissionLog


class SovereignMemory:
    """
    المحرك الرئيسي والواجهة الموحدة للذاكرة السيادية المزامنة مع النواة.
    تجمع: خرائط البنية التحتية + أنماط القرارات + سجل المأموريات.
    """

    def __init__(self, base_path: str = "storage/sovereign_memory"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

        self.infrastructure = InfrastructureMap(os.path.join(base_path, "infra.json"))
        self.decisions = DecisionMemory(os.path.join(base_path, "decisions.json"))
        self.missions = MissionLog(os.path.join(base_path, "missions.json"))

    def get_full_context(self) -> str:
        """توليد النص السياقي الشامل لحقنه في تعليمات الـ LLM."""
        infra_data = self.infrastructure.map

        hardware = infra_data.get("servers", {})
        projects = [p.get("name") for p in infra_data.get("projects", [])]
        priorities = [
            p.get("context") for p in infra_data.get("priorities", [])
            if isinstance(p, dict) and p.get("active")
        ]

        summary = {
            "hardware_recap": (
                f"{hardware.get('os', 'N/A')} "
                f"({hardware.get('cpu_cores', '?')} CPU Cores, "
                f"{hardware.get('ram_gb', '?')}GB RAM)"
            ),
            "monitored_repos": projects[:10],
            "active_goals": priorities[:5],
            "experiences_count": len(infra_data.get("experience_pool", [])),
            "decision_patterns_tracked": len(self.decisions.decisions),
            "historical_missions": len(self.missions.log)
        }

        return json.dumps(summary, ensure_ascii=False, indent=4)

    def add_experience(self, experience: dict) -> None:
        """إدراج خبرة مستخلصة وحفظها في بنك التجارب."""
        infra_map = self.infrastructure.map
        experiences = infra_map.get("experience_pool", [])

        clamped_experience = {
            "mission_id": experience.get("mission_id", "unknown"),
            "timestamp": experience.get("timestamp", datetime.now().isoformat()),
            "what_happened": str(experience.get("what_happened", ""))[:1500],
            "root_cause": str(experience.get("root_cause", ""))[:1500],
            "extracted_rule": experience.get("extracted_rule", {}),
            "confidence": round(float(experience.get("confidence", 0.5)), 2)
        }

        experiences.append(clamped_experience)
        if len(experiences) > 50:
            experiences.pop(0)

        self.infrastructure.update_field("experience_pool", experiences)

    def before_action(self, planned_action: str) -> dict:
        """استشارة الذاكرة واستباق القرارات وحساب الثقة قبل التنفيذ."""
        prediction = self.decisions.predict_preference(planned_action)
        lessons = self.missions.get_lessons_for(planned_action)

        proceed_autonomously = False
        if prediction["prediction"] == "approve" and prediction["confidence"] >= 0.8:
            proceed_autonomously = True

        return {
            "predicted_approval": prediction,
            "relevant_lessons": lessons,
            "proceed_autonomously": proceed_autonomously
        }

    def get_summary(self) -> dict:
        """يعيد ملخصا شاملا عن حالة الذاكرة السيادية."""
        return {
            "infrastructure_scanned": bool(self.infrastructure.map.get("servers")),
            "total_projects": len(self.infrastructure.map.get("projects", [])),
            "total_decisions": len(self.decisions.decisions),
            "total_missions": len(self.missions.log),
            "mission_success_rate": self.missions.get_success_rate(),
            "top_experiences": len(self.infrastructure.map.get("experience_pool", []))
        }
