# -*- coding: utf-8 -*-
"""
core/context/context_engine.py
المحرك الموحد للفهم السياقي -- Nexum Pro (v7.2.5)
===================================================
يجمع الأولويات والتفويض والمخاطر لإصدار القرار النهائي.
"""

from core.memory.sovereign_memory import SovereignMemory
from core.context.engines import PriorityEngine, DelegationEngine, RiskEngine


class ContextEngine:
    """المحرك الموحد للفهم السياقي: يجمع الأولويات والتفويض والمخاطر لإصدار القرار النهائي."""

    def __init__(self, memory: SovereignMemory, llm_interface=None):
        self.memory = memory
        self.priority = PriorityEngine(memory, llm_interface)
        self.delegation = DelegationEngine(memory)
        self.risk = RiskEngine(llm_interface)

    def evaluate_action(self, proposed_action: str) -> dict:
        """تقييم شامل للتصرف المقترح عبر المحركات الثلاثة."""
        priority_score = self.priority.score_action(proposed_action)
        delegation = self.delegation.evaluate(proposed_action)
        risk = self.risk.assess(proposed_action, self.memory.get_full_context())

        final_decision = self._make_final_decision(priority_score, delegation, risk)

        return {
            "action": proposed_action,
            "priority_alignment": priority_score,
            "delegation_level": delegation,
            "risk_assessment": risk,
            "final_decision": final_decision
        }

    def _make_final_decision(self, priority: dict, delegation: dict, risk: dict) -> dict:
        """اتخاذ القرار النهائي بناء على تكامل المعطيات الثلاثة."""

        # 1. المخاطرة المفرطة (> 80%) -- حظر فوري
        if risk["risk_score"] >= 0.8:
            return {
                "proceed": False,
                "action": "BLOCK",
                "message": (
                    f"Action BLOCKED! Risk too high ({int(risk['risk_score']*100)}%).\n"
                    f"Mitigation: {risk['mitigation']}"
                )
            }

        # 2. صلاحية مستقلة + مخاطرة منخفضة + توافق الأولويات
        if delegation["proceed"] and risk["risk_score"] < 0.4 and priority["aligned"]:
            return {
                "proceed": True,
                "action": "EXECUTE",
                "message": f"Safe autonomous execution [Reason: {delegation['reason']}]"
            }

        # 3. المنطقة الرمادية -- اقتراح مشروح
        return {
            "proceed": False,
            "action": "SUGGEST",
            "message": self._build_suggestion_msg(priority, risk, delegation)
        }

    def _build_suggestion_msg(self, priority: dict, risk: dict, delegation: dict) -> str:
        """بناء رسالة الاقتراح المفصلة للمطور."""
        alignment = "Aligned with your priorities" if priority["aligned"] else "Not aligned with current priorities"
        return (
            f"NEXUM Context Advisory:\n"
            f"- Action: {risk['action']}\n"
            f"- Goal Alignment: {alignment}\n"
            f"- Delegation: {delegation['reason']}\n"
            f"- Risk Level: {int(risk['risk_score']*100)}%\n"
            f"- Rollback Plan: {risk['rollback_plan']}\n"
            f"\nAwaiting your explicit approval to proceed."
        )
