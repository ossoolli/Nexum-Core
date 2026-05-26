# -*- coding: utf-8 -*-
"""
core/context/engines.py
المحركات الفرعية للفهم السياقي العميق -- Nexum Pro (v7.2.5)
==========================================================
- PriorityEngine: يزن التصرفات بناء على أهداف المستخدم الحالية
- DelegationEngine: فحص مستويات الصلاحية واتخاذ قرارات الاستقلالية
- RiskEngine: حساب معامل الخطورة وبناء خطط التراجع (Rollback)
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from core.memory.sovereign_memory import SovereignMemory


class PriorityEngine:
    """محرك الأولويات: يزن التصرفات بناء على أهداف المستخدم الحالية."""

    def __init__(self, memory: SovereignMemory, llm_interface=None):
        self.memory = memory
        self.llm = llm_interface
        self.current_priorities = self._load_priorities()

    def _load_priorities(self) -> list:
        """قراءة الأولويات من الذاكرة السيادية."""
        infra_map = self.memory.infrastructure.map
        return infra_map.get("priorities", [])

    def set_priority(self, context: str, weight: float, deadline: str = None) -> None:
        """تسجيل أولوية جديدة وحفظها ذريا في الذاكرة السيادية."""
        priority = {
            "context": context[:2000],
            "weight": max(0.0, min(weight, 1.0)),  # حصر القيمة بين 0 و 1
            "deadline": deadline,
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        self.current_priorities.append(priority)
        self.memory.infrastructure.update_field("priorities", self.current_priorities)

    def deactivate_priority(self, index: int) -> bool:
        """تعطيل أولوية بناء على ترتيبها في القائمة."""
        if 0 <= index < len(self.current_priorities):
            self.current_priorities[index]["active"] = False
            self.memory.infrastructure.update_field("priorities", self.current_priorities)
            return True
        return False

    def score_action(self, proposed_action: str) -> dict:
        """يحسب درجة توافق التصرف المقترح مع الأولويات النشطة."""
        if not self.current_priorities:
            return {
                "action": proposed_action,
                "priority_score": 0.5,
                "aligned": True,
                "breakdown": []
            }

        scores = []
        for priority in self.current_priorities:
            if not priority.get("active", False):
                continue

            relevance = self._calculate_relevance(proposed_action, priority["context"])
            scores.append({
                "priority": priority["context"][:100],
                "relevance": relevance,
                "weight": priority["weight"],
                "final_score": round(relevance * priority["weight"], 2)
            })

        total = sum(s["final_score"] for s in scores)
        return {
            "action": proposed_action,
            "priority_score": round(total, 2),
            "aligned": total >= 0.4 or not scores,
            "breakdown": scores
        }

    def _calculate_relevance(self, action: str, priority: str) -> float:
        """حساب مدى ارتباط التصرف بالأولوية -- LLM أو Keyword Fallback."""
        if not self.llm:
            # تحليل دفاعي مبدئي بتطابق كلمات مفتاحية
            action_words = set(action.lower().split())
            priority_words = set(priority.lower().split())
            if action_words.intersection(priority_words):
                return 0.8
            return 0.3

        try:
            prompt = (
                f"Priority: {priority}\nAction: {action}\n"
                f"Rate relevance from 0.0 to 1.0. Output numbers only."
            )
            response, _ = self.llm.ask(prompt)
            # استخلاص أول رقم عشري من الاستجابة
            for token in response.strip().split():
                try:
                    val = float(token)
                    if 0.0 <= val <= 1.0:
                        return val
                except ValueError:
                    continue
            return 0.5
        except Exception:
            return 0.5


class DelegationEngine:
    """محرك التفويض: فحص مستويات الصلاحية واتخاذ قرارات الاستقلالية."""

    # الأوامر المحظورة تماما -- تتطلب إذن صريح دائما
    ALWAYS_ASK = [
        "delete", "rm ", "drop", "sudo", "config", "stop",
        "db", "production", "kill", "ufw", "shutdown",
        "reboot", "mkfs", "dd if=", "chmod 777",
        "git push --force", "truncate"
    ]

    # الأوامر الروتينية الآمنة -- تنفيذ مستقل
    ALWAYS_PROCEED = [
        "cat ", "grep", "status", "ls ", "df ", "free",
        "log", "check", "echo", "pwd", "whoami", "uptime",
        "tree", "find", "head", "tail", "wc "
    ]

    def __init__(self, memory: SovereignMemory):
        self.memory = memory
        self.custom_rules = self._load_custom_rules()

    def _load_custom_rules(self) -> list:
        """تحميل القواعد المخصصة من الذاكرة السيادية."""
        infra_map = self.memory.infrastructure.map
        return infra_map.get("custom_delegation_rules", [])

    def evaluate(self, action: str) -> dict:
        """تقييم التصرف وتحديد مستوى الصلاحية المطلوب."""
        action_lower = action.lower()

        # 1. فحص الكلمات المحظورة (Strict Security Check)
        if any(blocked in action_lower for blocked in self.ALWAYS_ASK):
            return {
                "level": "MUST_ASK",
                "reason": "Action touches system safety/security - explicit permission required.",
                "proceed": False
            }

        # 2. فحص القواعد المخصصة التي أضافها المستخدم
        for rule in self.custom_rules:
            if rule.get("pattern", "").lower() in action_lower:
                return {
                    "level": rule.get("level", "MUST_ASK"),
                    "reason": f"Custom rule match: {rule['pattern']}",
                    "proceed": rule.get("level") == "AUTONOMOUS"
                }

        # 3. فحص العمليات الروتينية الآمنة
        if any(allowed in action_lower for allowed in self.ALWAYS_PROCEED):
            return {
                "level": "AUTONOMOUS",
                "reason": "Routine safe query operation.",
                "proceed": True
            }

        # 4. القرارات الرمادية -- استشارة ذاكرة القرارات
        prediction = self.memory.decisions.predict_preference(action)
        if prediction["confidence"] >= 0.85 and prediction["prediction"] == "approve":
            return {
                "level": "AUTONOMOUS",
                "reason": f"High confidence ({int(prediction['confidence']*100)}%) based on prior decisions.",
                "proceed": True
            }
        elif prediction["confidence"] >= 0.5:
            return {
                "level": "SUGGEST",
                "reason": "Medium confidence - developer review preferred.",
                "proceed": False
            }

        return {
            "level": "MUST_ASK",
            "reason": "Novel situation not found in decision history.",
            "proceed": False
        }

    def add_custom_rule(self, action_pattern: str, level: str) -> None:
        """إضافة قاعدة تفويض مخصصة وحفظها في الذاكرة السيادية."""
        valid_levels = {"AUTONOMOUS", "SUGGEST", "MUST_ASK"}
        if level not in valid_levels:
            level = "MUST_ASK"

        self.custom_rules.append({
            "pattern": action_pattern,
            "level": level,
            "added_at": datetime.now().isoformat()
        })
        self.memory.infrastructure.update_field("custom_delegation_rules", self.custom_rules)


class RiskEngine:
    """محرك تقييم المخاطر: حساب معامل الخطورة وبناء خطط التراجع (Rollback)."""

    # مصفوفة المخاطر الأساسية
    RISK_MATRIX = {
        "data_loss": 0.9,
        "downtime": 0.7,
        "config_change": 0.6,
        "performance": 0.4,
        "cosmetic": 0.1
    }

    def __init__(self, llm_interface=None):
        self.llm = llm_interface

    def assess(self, action: str, context: str = "") -> dict:
        """تقييم شامل للمخاطر مع خطة تراجع."""
        risks = self._identify_risks(action)
        score = self._calculate_risk_score(risks, action)

        return {
            "action": action,
            "risks_identified": risks,
            "risk_score": score,
            "mitigation": (
                "Ensure backup exists and monitor live logs."
                if score > 0.5
                else "Low-risk operation."
            ),
            "rollback_plan": self._build_rollback(action)
        }

    def _identify_risks(self, action: str) -> list:
        """تحديد أنواع المخاطر بناء على الكلمات المفتاحية."""
        action_lower = action.lower()
        detected = []

        if any(k in action_lower for k in ["rm ", "delete", "drop", "clear", "truncate"]):
            detected.append("data_loss")
        if any(k in action_lower for k in ["restart", "stop", "reboot", "shutdown", "kill"]):
            detected.append("downtime")
        if any(k in action_lower for k in ["config", "env", "chmod", "chown", "nginx"]):
            detected.append("config_change")
        if any(k in action_lower for k in ["build", "compile", "update", "upgrade", "install"]):
            detected.append("performance")

        if not detected:
            detected.append("cosmetic")
        return detected

    def _calculate_risk_score(self, risks: list, action: str) -> float:
        """حساب الدرجة النهائية للمخاطر."""
        base_score = max(
            [self.RISK_MATRIX.get(r, 0.1) for r in risks]
        ) if risks else 0.1

        # كلمات Production ترفع المخاطرة تلقائيا
        if "prod" in action.lower():
            base_score = max(base_score, 0.85)

        return round(base_score, 2)

    def _build_rollback(self, action: str) -> str:
        """بناء خطة تراجع (LLM أو Fallback دفاعي)."""
        if self.llm:
            try:
                response, _ = self.llm.ask(
                    f"How to rollback this command quickly: '{action}'? Concise steps."
                )
                return response.strip()[:500]
            except Exception:
                pass

        # خطط تراجع دفاعية افتراضية
        action_lower = action.lower()
        if "restart" in action_lower:
            return "Restart the service again or check journalctl/Event Viewer."
        if "mv " in action_lower or "cp " in action_lower:
            return "Reverse the file move/copy using the inverse command."
        if "rm " in action_lower or "delete" in action_lower:
            return "Restore from backup. Check .bak files or version control."
        if "install" in action_lower or "update" in action_lower:
            return "Pin to previous version or rollback with package manager."

        return "No automated rollback available. Manual system state inspection required."
