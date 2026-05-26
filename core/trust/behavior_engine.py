# -*- coding: utf-8 -*-
"""
core/trust/behavior_engine.py
محرك السلوك والتقرير اليومي -- Nexum Pro (v7.2.5)
===================================================
- يترجم التكامل بين مستوى الثقة والفهم السياقي لإنتاج نمط السلوك الآمن.
- تقرير يومي شفاف يعرض كل ما تم تنفيذه بصمت ومستويات الثقة الحالية.
"""

from core.trust.trust_engine import TrustEngine
from core.context.context_engine import ContextEngine


class BehaviorEngine:
    """محرك السلوك: يترجم التكامل بين مستوى الثقة والفهم السياقي لنمط السلوك الآمن."""

    def __init__(self, trust_engine: TrustEngine, context_engine: ContextEngine):
        self.trust = trust_engine
        self.context = context_engine

    def decide(self, action: str, category: str) -> dict:
        """يتخذ القرار النهائي بدمج مستوى الثقة مع تقييم السياق."""
        trust_status = self.trust.get_trust_level(category)
        context_eval = self.context.evaluate_action(action)

        level = trust_status["level"]

        # حماية مطلقة: إذا رفض محرك السياق الأمر، يتم حظره فورا
        final = context_eval.get("final_decision", {})
        if not final.get("proceed") and final.get("action") == "BLOCK":
            return {
                "execute": False,
                "mode": "BLOCKED_BY_CONTEXT",
                "message": final.get("message", "Action blocked by context engine.")
            }

        if level == 0:
            return self._observe_mode(action, context_eval)
        elif level == 1:
            return self._suggest_mode(action, context_eval)
        elif level == 2:
            return self._notify_mode(action, context_eval)
        elif level == 3:
            return self._autonomous_mode(action, context_eval)
        else:
            return self._sovereign_mode(action, context_eval)

    def _observe_mode(self, action: str, context: dict) -> dict:
        risk_score = context.get("risk_assessment", {}).get("risk_score", 0)
        return {
            "execute": False,
            "mode": "OBSERVE",
            "message": (
                f"NEXUM [Observation Mode]\n"
                f"- Detected action: {action}\n"
                f"- Risk Level: {int(risk_score * 100)}%\n"
                f"System is in learning phase for this category."
            )
        }

    def _suggest_mode(self, action: str, context: dict) -> dict:
        return {
            "execute": False,
            "mode": "SUGGEST",
            "awaiting_approval": True,
            "message": context.get("final_decision", {}).get(
                "message", "Awaiting your approval."
            )
        }

    def _notify_mode(self, action: str, context: dict) -> dict:
        risk_score = context.get("risk_assessment", {}).get("risk_score", 0)
        # حماية إضافية: المخاطر المتوسطة تجبر النظام على العودة لوضع الاقتراح
        if risk_score >= 0.50:
            return self._suggest_mode(action, context)

        return {
            "execute": True,
            "mode": "NOTIFY",
            "notify_after": True,
            "message": f"[Execute & Notify] Running: {action}... Report will follow."
        }

    def _autonomous_mode(self, action: str, context: dict) -> dict:
        risk_score = context.get("risk_assessment", {}).get("risk_score", 0)
        if risk_score >= 0.70:
            return self._suggest_mode(action, context)

        return {
            "execute": True,
            "mode": "AUTONOMOUS",
            "silent": True,
            "log_in_daily_report": True
        }

    def _sovereign_mode(self, action: str, context: dict) -> dict:
        risk_score = context.get("risk_assessment", {}).get("risk_score", 0)
        if risk_score >= 0.80:
            return self._suggest_mode(action, context)

        return {
            "execute": True,
            "mode": "SOVEREIGN",
            "silent": True,
            "learn_and_improve": True,
            "can_initiate": True
        }


class DailyReport:
    """محرك التقرير اليومي الشفاف لمستويات الثقة والعمليات."""

    def __init__(self, trust_engine: TrustEngine):
        self.trust = trust_engine

    def generate(self) -> str:
        """يولد تقريرا شاملا لمصفوفة الثقة والأداء."""
        status = self.trust.trust_scores
        if not status:
            return "NEXUM Daily Report: No trust data available yet."

        icons = {0: "[O]", 1: "[S]", 2: "[N]", 3: "[A]", 4: "[V]"}
        lines = []

        for category, data in status.items():
            level = data.get("level", 0)
            score = data.get("score", 0.0)
            icon = icons.get(level, "[?]")
            filled = int(score * 10)
            bar = "#" * filled + "-" * (10 - filled)
            level_name = TrustEngine.LEVELS.get(level, "OBSERVE")
            lines.append(
                f"  {icon} {category.ljust(20)}: [{bar}] {int(score * 100)}% ({level_name})"
            )

        categories_report = "\n".join(lines)

        total_actions = sum(d.get("total_actions", 0) for d in status.values())
        total_success = sum(d.get("successful", 0) for d in status.values())
        total_overrides = sum(d.get("user_overrides", 0) for d in status.values())
        total_failed = sum(d.get("failed", 0) for d in status.values())

        return (
            f"NEXUM PRO Daily Transparency Report\n"
            f"{'=' * 40}\n\n"
            f"Trust Matrix Status:\n{categories_report}\n\n"
            f"Efficiency Summary:\n"
            f"  - Total Operations: {total_actions}\n"
            f"  - Successful (Auto): {total_success}\n"
            f"  - Failed: {total_failed}\n"
            f"  - User Overrides: {total_overrides}\n\n"
            f"System operating under Zero-Fault Tolerance policy."
        )
