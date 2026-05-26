# -*- coding: utf-8 -*-
"""
core/trust/trust_engine.py
قلب نظام الثقة المتدرج -- Nexum Pro (v7.2.5)
===============================================
- يحسب ويدير مستويات الثقة لكل فئة قرار بشكل مستقل.
- عتبة العقوبة أعلى من المكافأة لضمان الهبوط الفوري عند السلوك غير المتوقع.
- تخزين مستويات الثقة ديناميكيا داخل خريطة الذاكرة السيادية الموحدة.
"""

from datetime import datetime
from core.memory.sovereign_memory import SovereignMemory


class TrustEngine:
    """يحسب ويدير مستويات الثقة لكل فئة قرار بشكل مستقل."""

    LEVELS = {
        0: "OBSERVE",       # يراقب ويتعلم فقط
        1: "SUGGEST",       # يقترح وينتظر موافقة
        2: "NOTIFY",        # ينفذ ويخبر المستخدم فورا
        3: "AUTONOMOUS",    # ينفذ بصمت (تقرير يومي)
        4: "SOVEREIGN"      # يتصرف، يتعلم، ويقترح تحسينات بمبادرة ذاتية
    }

    CATEGORIES = [
        "system_monitoring",
        "file_management",
        "service_control",
        "code_operations",
        "security_actions",
        "infrastructure"
    ]

    # عتبات الترقية الصارمة
    THRESHOLDS = {0: 0.30, 1: 0.60, 2: 0.80, 3: 0.95}

    def __init__(self, memory: SovereignMemory, bot_interface=None):
        self.memory = memory
        self.bot = bot_interface
        self.trust_scores = self._load_scores()
        self._initialize_categories()

    def _load_scores(self) -> dict:
        """قراءة درجات الثقة المخزنة في خريطة الذاكرة السيادية."""
        infra_map = self.memory.infrastructure.map
        return infra_map.get("trust_matrix", {})

    def _save(self) -> None:
        """حفظ مصفوفة الثقة ذريا."""
        self.memory.infrastructure.update_field("trust_matrix", self.trust_scores)

    def _initialize_categories(self) -> None:
        """تهيئة الفئات غير الموجودة بقيم دفاعية (البدء من الصفر)."""
        updated = False
        for category in self.CATEGORIES:
            if category not in self.trust_scores:
                self.trust_scores[category] = {
                    "level": 0,
                    "score": 0.0,
                    "total_actions": 0,
                    "successful": 0,
                    "failed": 0,
                    "user_overrides": 0,
                    "history": []
                }
                updated = True
        if updated:
            self._save()

    def get_trust_level(self, category: str) -> dict:
        """استرجاع مستوى الثقة الحالي لفئة محددة."""
        if category not in self.trust_scores:
            category = "system_monitoring"

        data = self.trust_scores[category]
        level = data.get("level", 0)
        return {
            "category": category,
            "level": level,
            "level_name": self.LEVELS.get(level, "OBSERVE"),
            "score": data.get("score", 0.0),
            "can_proceed_autonomously": level >= 2
        }

    def record_outcome(self, category: str, action: str, result: str,
                       user_intervened: bool = False) -> None:
        """تسجيل نتيجة عملية وتحديث مصفوفة الثقة ديناميكيا."""
        if category not in self.trust_scores:
            category = "system_monitoring"

        data = self.trust_scores[category]
        data["total_actions"] += 1

        if result == "success" and not user_intervened:
            data["successful"] += 1
            self._increase_trust(category)
        elif result == "failed":
            data["failed"] += 1
            self._decrease_trust(category, penalty=0.20)
        elif user_intervened:
            data["user_overrides"] += 1
            self._decrease_trust(category, penalty=0.10)

        # تسجيل الحدث في التاريخ
        data["history"].append({
            "action": (action or "")[:500],
            "result": result,
            "intervened": user_intervened,
            "timestamp": datetime.now().isoformat()
        })

        # الحفاظ على آخر 20 عملية فقط
        data["history"] = data["history"][-20:]
        self._save()

    def get_stats(self) -> dict:
        """استرجاع ملخص شامل لحالة مصفوفة الثقة."""
        stats = {}
        for cat, data in self.trust_scores.items():
            stats[cat] = {
                "level": data.get("level", 0),
                "level_name": self.LEVELS.get(data.get("level", 0), "OBSERVE"),
                "score": data.get("score", 0.0),
                "total": data.get("total_actions", 0),
                "success_rate": (
                    round(data["successful"] / data["total_actions"], 2)
                    if data.get("total_actions", 0) > 0 else 0.0
                )
            }
        return stats

    def _increase_trust(self, category: str, reward: float = 0.10) -> None:
        """زيادة درجة الثقة مع فحص عتبات الترقية."""
        data = self.trust_scores[category]
        data["score"] = min(1.0, round(data["score"] + reward, 2))

        current_level = data["level"]
        if current_level < 4:
            threshold = self.THRESHOLDS.get(current_level, 1.0)
            if data["score"] >= threshold:
                data["level"] += 1
                self._notify_level_change(category, data["level"], direction="UP")

    def _decrease_trust(self, category: str, penalty: float) -> None:
        """خفض درجة الثقة مع فحص عتبة الهبوط."""
        data = self.trust_scores[category]
        data["score"] = max(0.0, round(data["score"] - penalty, 2))

        if data["score"] < 0.25 and data["level"] > 0:
            data["level"] -= 1
            self._notify_level_change(category, data["level"], direction="DOWN")

    def _notify_level_change(self, category: str, new_level: int, direction: str) -> None:
        """إشعار بتغيير مستوى الثقة (طباعة + Telegram إن توفر)."""
        level_name = self.LEVELS.get(new_level, "OBSERVE")
        if direction == "UP":
            console_msg = f"[Trust LEVEL UP] Category [{category}] promoted to: {level_name}"
            tg_msg = f"[NEXUM TRUST LEVEL UP] Category [{category}] promoted to: {level_name}."
        else:
            console_msg = f"[Trust LEVEL DOWN] Category [{category}] demoted to: {level_name}"
            tg_msg = f"[NEXUM TRUST LEVEL DOWN] Category [{category}] demoted to: {level_name} due to errors/overrides."

        print(console_msg)

        if self.bot and hasattr(self.bot, '_admin_id'):
            try:
                self.bot.send_message(self.bot._admin_id, tg_msg)
            except Exception:
                pass
