# -*- coding: utf-8 -*-
"""
core/learning/initiative_engine.py
محرك التنبؤ والمبادرة الذاتية -- Nexum Pro (v7.2.5)
=====================================================
- PredictionEngine: يتوقع المشاكل والفرص قبل حدوثها
- InitiativeEngine: العقل الاستباقي الذي يبادر بحماية وتحسين بيئة العمل
"""

import json
from datetime import datetime
from typing import Optional, Dict, List

from core.memory.sovereign_memory import SovereignMemory
from core.trust.trust_engine import TrustEngine
from core.trust.behavior_engine import BehaviorEngine
from core.learning.engines import PatternExtractor


class PredictionEngine:
    """محرك التنبؤ: يتوقع المشاكل والفرص التقنية بناء على الأنماط المستخلصة."""

    def __init__(self, memory: SovereignMemory, pattern_extractor: PatternExtractor):
        self.memory = memory
        self.extractor = pattern_extractor

    def predict(self, current_context: dict = None) -> dict:
        """يولد تنبؤات بالمشاكل والفرص المحتملة."""
        if current_context is None:
            current_context = {}

        patterns = self.extractor.patterns
        predicted_problems = []
        predicted_opportunities = []

        # 1. التنبؤ بالمشاكل المحتملة من الأنماط المكتشفة
        for pattern in patterns:
            if (pattern.get("type") == "recurring_failure"
                    and pattern.get("confidence", 0) > 0.6):
                predicted_problems.append({
                    "problem": pattern["description"],
                    "probability": pattern["confidence"],
                    "suggested_prevention": pattern.get("suggested_fix", "Manual review required."),
                    "urgency": "high"
                })

        # 2. فحص فرص الصيانة الاستباقية (نافذة ليلية أو حمل منخفض)
        hour = datetime.now().hour
        cpu_usage = current_context.get("cpu_usage", 10)

        if 0 <= hour <= 6 or cpu_usage < 30:
            predicted_opportunities.append({
                "type": "maintenance_window",
                "description": "System load is low. Ideal time for maintenance.",
                "suggested_actions": [
                    "Clean temporary files",
                    "Check dependency updates",
                    "Optimize memory usage"
                ]
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "predicted_problems": predicted_problems,
            "predicted_opportunities": predicted_opportunities
        }


class InitiativeEngine:
    """العقل الاستباقي لـ Nexum Pro: يبادر بحماية وتحسين بيئة العمل تلقائيا وبأمان."""

    def __init__(self, memory: SovereignMemory,
                 prediction_engine: PredictionEngine,
                 trust_engine: TrustEngine,
                 behavior_engine: BehaviorEngine,
                 llm_interface=None):
        self.memory = memory
        self.prediction = prediction_engine
        self.trust = trust_engine
        self.behavior = behavior_engine
        self.llm = llm_interface

    def run_proactive_cycle(self, mock_cpu_usage: int = 15) -> list:
        """تشغيل الدورة الاستباقية لفحص الفرص وحماية السيرفر."""
        context = {
            "cpu_usage": mock_cpu_usage,
            "timestamp": datetime.now().isoformat()
        }
        predictions = self.prediction.predict(context)
        actions_taken = []

        # التعامل الاستباقي مع المشاكل المتوقعة
        for problem in predictions.get("predicted_problems", []):
            if problem.get("probability", 0) >= 0.70:
                action = problem.get("suggested_prevention", "Review required")
                # التحقق الصارم من مستوى الثقة قبل المبادرة المستقلة
                trust_status = self.trust.get_trust_level("infrastructure")

                if trust_status["level"] >= 3:  # AUTONOMOUS أو أعلى فقط
                    result = self.behavior.decide(action, "infrastructure")
                    actions_taken.append({
                        "action": action,
                        "trigger": f"Proactive prevention: {problem['problem']}",
                        "result": "executed_silently" if result.get("silent") else "suggested",
                        "mode": result.get("mode", "UNKNOWN")
                    })
                else:
                    actions_taken.append({
                        "action": action,
                        "trigger": f"Proactive prevention: {problem['problem']}",
                        "result": "suggestion_only",
                        "mode": "SUGGEST",
                        "note": f"Trust level too low ({trust_status['level_name']}). Converted to suggestion."
                    })

        return actions_taken

    def check_proactive(self, sovereign_data: dict = None,
                        learning_stats: dict = None,
                        trust_stats: dict = None) -> list:
        """فحص بسيط للفرص الاستباقية بدون تنفيذ -- يعيد قائمة اقتراحات."""
        suggestions = []

        # فحص أنماط الفشل
        if sovereign_data:
            exp_count = sovereign_data.get("top_experiences", 0)
            if exp_count > 10:
                suggestions.append({
                    "type": "experience_review",
                    "message": f"Experience pool has {exp_count} entries. Consider pattern analysis."
                })

        # فحص الثقة المتدنية
        if trust_stats:
            for cat, data in trust_stats.items():
                if isinstance(data, dict) and data.get("score", 1.0) < 0.2:
                    suggestions.append({
                        "type": "low_trust_alert",
                        "category": cat,
                        "message": f"Trust score critically low for [{cat}]: {data['score']}"
                    })

        return suggestions

    def generate_self_improvement_plan(self) -> dict:
        """يولد خطة تحسين ذاتي بناء على حالة النظام الحالية."""
        infra_map = self.memory.infrastructure.map
        experiences_count = len(infra_map.get("experience_pool", []))
        patterns_count = len(infra_map.get("discovered_patterns", []))
        trust_status = self.trust.trust_scores

        # محاولة استخدام LLM
        if self.llm:
            try:
                prompt = (
                    f"Analyze performance:\n"
                    f"Experiences: {experiences_count}\n"
                    f"Patterns: {patterns_count}\n"
                    f"Trust Matrix: {json.dumps(trust_status)}\n"
                    f"Generate a self-improvement plan as JSON with keys: "
                    f"weakest_points (list), learning_goals (list), target_weekly_improvement_score (str)"
                )
                response, _ = self.llm.ask(prompt)
                # محاولة استخلاص JSON من الاستجابة
                cleaned = response.strip()
                if "```" in cleaned:
                    import re
                    match = re.search(r'\{[\s\S]*\}', cleaned)
                    if match:
                        cleaned = match.group()
                return json.loads(cleaned)
            except Exception:
                pass

        # خطة تحسين دفاعية
        weak_categories = []
        for cat, data in trust_status.items():
            if isinstance(data, dict) and data.get("score", 0) < 0.5:
                weak_categories.append(cat)

        return {
            "weakest_points": weak_categories or ["Need more decision samples in some categories."],
            "learning_goals": [
                "Accumulate more patterns for file management operations.",
                f"Current experience pool: {experiences_count} entries."
            ],
            "target_weekly_improvement_score": "95% Stability Index"
        }
