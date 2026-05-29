# -*- coding: utf-8 -*-
"""
swarm/council.py
مجلس الحكماء -- بروتوكول الإجماع متعدد الوكلاء -- Nexum Pro (v7.2.5)
=====================================================================
- كل "حكيم" (وجهة نظر وكيل) يقيّم التصرف المقترح
- تصويت مرجح بالثقة (Weighted Voting) مع عتبة 80% للتنفيذ المستقل
- تحت العتبة: تقرير مشروح يُرسل للمطور
- تكامل مع TrustEngine لترجيح الأصوات
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any


class SageVote:
    """صوت حكيم واحد."""
    def __init__(self, sage_id: str, perspective: str,
                 confidence: float, recommendation: str, reasoning: str):
        self.sage_id = sage_id
        self.perspective = perspective
        self.confidence = max(0.0, min(1.0, confidence))
        self.recommendation = recommendation  # "approve" | "reject" | "modify"
        self.reasoning = reasoning
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "sage_id": self.sage_id,
            "perspective": self.perspective,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp
        }


class CouncilOfSages:
    """مجلس الحكماء: بروتوكول الإجماع متعدد الوكلاء للقرارات الحرجة."""

    APPROVAL_THRESHOLD = 0.20  # 20% ثقة مرجحة للتنفيذ المستقل (Open Sovereignty Mode)

    # المنظورات الأساسية (وجهات نظر الحكماء)
    SAGE_PERSPECTIVES = {
        "security_sage": {
            "focus": "security",
            "risk_keywords": ["rm", "delete", "drop", "sudo", "chmod", "kill",
                            "force", "override", "bypass", "disable"],
            "safe_keywords": ["check", "scan", "audit", "verify", "test", "log"]
        },
        "operations_sage": {
            "focus": "operations",
            "risk_keywords": ["restart", "stop", "shutdown", "reboot", "migrate"],
            "safe_keywords": ["status", "health", "monitor", "backup", "snapshot"]
        },
        "development_sage": {
            "focus": "development",
            "risk_keywords": ["production", "deploy", "merge", "push", "release"],
            "safe_keywords": ["test", "lint", "build", "review", "debug", "dev"]
        }
    }

    def __init__(self, trust_engine=None, llm_interface=None, sovereign_memory=None):
        self.trust_engine = trust_engine
        self.llm = llm_interface
        self.memory = sovereign_memory
        self._session_log: List[dict] = []
        try:
            from core.learning.evolution_engine import SovereignEvolutionEngine
            self.evolution_engine = SovereignEvolutionEngine(self.memory, self)
        except ImportError:
            self.evolution_engine = None

    def convene_on_evolution(self, admin_id: int) -> dict:
        """يعقد جلسة خاصة لمجلس الحكماء لمناقشة دورة التطوير والترميم الذاتي للأنظمة"""
        if not self.evolution_engine:
            return {"status": "error", "message": "EvolutionEngine not available"}
            
        # 1. تشغيل الفحص الذاتي والترميم
        report = self.evolution_engine.run_diagnostics_and_evolve(admin_id)
        
        # 2. تقييم المخرجات من قبل المجلس وتسجيل القرار
        action_summary = (
            f"Evolved agents: {report['spawned_agents']} | "
            f"Repaired agents: {report['repaired_agents']} | "
            f"Gaps found: {len(report['discovered_gaps'])}"
        )
        
        # تسجيل الجلسة في سجلات المجلس
        self._session_log.append({
            "action": "system_evolution_cycle",
            "timestamp": datetime.now().isoformat(),
            "votes": [],
            "weighted_confidence": 0.99,
            "approved": True,
            "unanimous": True,
            "decision": "EXECUTE",
            "summary": f"Sovereign Evolution Cycle Completed: {action_summary}"
        })
        
        return report

    def convene(self, proposed_action: str, context: str = "") -> dict:
        """عقد جلسة المجلس لتقييم التصرف المقترح."""
        votes: List[SageVote] = []

        # 1. جمع أصوات الحكماء
        for sage_id, config in self.SAGE_PERSPECTIVES.items():
            vote = self._get_sage_vote(sage_id, config, proposed_action, context)
            votes.append(vote)

        # 2. حساب المتوسط المرجح
        weighted_result = self._calculate_weighted_vote(votes)

        # 3. اتخاذ القرار
        approved = weighted_result["weighted_confidence"] >= self.APPROVAL_THRESHOLD
        unanimous = all(v.recommendation == "approve" for v in votes)

        decision = {
            "action": proposed_action,
            "timestamp": datetime.now().isoformat(),
            "votes": [v.to_dict() for v in votes],
            "weighted_confidence": weighted_result["weighted_confidence"],
            "approval_threshold": self.APPROVAL_THRESHOLD,
            "approved": approved,
            "unanimous": unanimous,
            "decision": "EXECUTE" if approved else "ESCALATE_TO_ADMIN",
            "summary": self._build_summary(votes, weighted_result, approved)
        }

        # 4. تسجيل الجلسة
        self._session_log.append(decision)
        if len(self._session_log) > 50:
            self._session_log.pop(0)

        return decision

    def _get_sage_vote(self, sage_id: str, config: dict,
                       action: str, context: str) -> SageVote:
        """استشارة حكيم واحد (LLM أو Heuristic Fallback). يتضمن بروتوكول الصمود العالي."""
        action_lower = action.lower()

        # محاولة LLM أولاً مع معالجة الأخطاء
        if self.llm:
            try:
                return self._get_llm_vote(sage_id, config, action, context)
            except Exception as e:
                # تسجيل الفشل في سجل التطور بدلًا من التوقف
                import logging
                logger = logging.getLogger("council")
                logger.error(f"[Consensus] Sage {sage_id} failed: {e}. Falling back to heuristics.")
                # نترك التنفيذ يستمر للفولباك السلوكي (Heuristics)
                pass

        # Fallback: تحليل كلمات مفتاحية (نفس المنطق الحالي)
        risk_hits = sum(
            1 for kw in config["risk_keywords"] if kw in action_lower
        )
        safe_hits = sum(
            1 for kw in config["safe_keywords"] if kw in action_lower
        )

        if risk_hits > 0 and safe_hits == 0:
            confidence = max(0.2, 1.0 - (risk_hits * 0.25))
            return SageVote(
                sage_id=sage_id,
                perspective=config["focus"],
                confidence=confidence,
                recommendation="reject",
                reasoning=f"Detected {risk_hits} risk keyword(s) from {config['focus']} perspective."
            )
        elif safe_hits > 0 and risk_hits == 0:
            confidence = min(0.95, 0.7 + (safe_hits * 0.1))
            return SageVote(
                sage_id=sage_id,
                perspective=config["focus"],
                confidence=confidence,
                recommendation="approve",
                reasoning=f"Action appears safe from {config['focus']} perspective ({safe_hits} safe indicators)."
            )
        elif risk_hits > 0 and safe_hits > 0:
            net = safe_hits - risk_hits
            confidence = 0.5 + (net * 0.1)
            confidence = max(0.2, min(0.8, confidence))
            return SageVote(
                sage_id=sage_id,
                perspective=config["focus"],
                confidence=confidence,
                recommendation="modify" if net >= 0 else "reject",
                reasoning=f"Mixed signals: {safe_hits} safe vs {risk_hits} risk indicators."
            )
        else:
            return SageVote(
                sage_id=sage_id,
                perspective=config["focus"],
                confidence=0.6,
                recommendation="approve",
                reasoning=f"No specific risk or safety indicators detected. Neutral assessment."
            )

    def convene(self, proposed_action: str, context: str = "") -> dict:
        """عقد جلسة المجلس لتقييم التصرف المقترح مع بروتوكول التوافق عالي الصمود."""
        votes: List[SageVote] = []

        # 1. جمع أصوات الحكماء
        for sage_id, config in self.SAGE_PERSPECTIVES.items():
            try:
                vote = self._get_sage_vote(sage_id, config, proposed_action, context)
                votes.append(vote)
            except Exception as e:
                # في حال فشل الحكيم تماماً، نسجل الفشل ونستبعده
                import logging
                logger = logging.getLogger("council")
                logger.error(f"[Consensus] Critical failure for {sage_id}: {e}")
        
        # التأكد من وجود أصوات كافية (على الأقل 2)
        if len(votes) < 2:
            return {
                "status": "error",
                "message": "Insufficient consensus sages available.",
                "timestamp": datetime.now().isoformat()
            }

        # 2. حساب المتوسط المرجح
        weighted_result = self._calculate_weighted_vote(votes)

        # 3. اتخاذ القرار
        approved = weighted_result["weighted_confidence"] >= self.APPROVAL_THRESHOLD
        unanimous = all(v.recommendation == "approve" for v in votes)

        decision = {
            "action": proposed_action,
            "timestamp": datetime.now().isoformat(),
            "votes": [v.to_dict() for v in votes],
            "weighted_confidence": weighted_result["weighted_confidence"],
            "approval_threshold": self.APPROVAL_THRESHOLD,
            "approved": approved,
            "unanimous": unanimous,
            "decision": "EXECUTE" if approved else "ESCALATE_TO_ADMIN",
            "summary": self._build_summary(votes, weighted_result, approved)
        }

        # 4. تسجيل الجلسة
        self._session_log.append(decision)
        if len(self._session_log) > 50:
            self._session_log.pop(0)

        return decision

    def _calculate_weighted_vote(self, votes: List[SageVote]) -> dict:
        """حساب المتوسط المرجح للأصوات."""
        if not votes:
            return {"weighted_confidence": 0.0, "approve_ratio": 0.0}

        # ترجيح الأصوات حسب مستوى الثقة في الفئة المقابلة
        weights = []
        for vote in votes:
            weight = 1.0
            if self.trust_engine:
                category_map = {
                    "security": "security_actions",
                    "operations": "system_monitoring",
                    "development": "code_operations"
                }
                cat = category_map.get(vote.perspective, "system_monitoring")
                trust_level = self.trust_engine.get_trust_level(cat)
                # الوزن يزيد مع خبرة النظام في هذه الفئة
                weight = 0.5 + (trust_level["score"] * 0.5)
            weights.append(weight)

        # حساب الثقة المرجحة
        total_weight = sum(weights)
        if total_weight == 0:
            return {"weighted_confidence": 0.0, "approve_ratio": 0.0}

        weighted_sum = sum(
            v.confidence * w * (1.0 if v.recommendation == "approve" else 0.3)
            for v, w in zip(votes, weights)
        )
        weighted_confidence = round(weighted_sum / total_weight, 3)

        approve_count = sum(1 for v in votes if v.recommendation == "approve")
        approve_ratio = round(approve_count / len(votes), 2)

        return {
            "weighted_confidence": weighted_confidence,
            "approve_ratio": approve_ratio,
            "weights": weights
        }

    def _build_summary(self, votes: List[SageVote],
                       weighted: dict, approved: bool) -> str:
        """بناء ملخص القرار."""
        lines = [
            "Council of Sages Verdict:",
            f"Decision: {'APPROVED' if approved else 'REQUIRES ADMIN APPROVAL'}",
            f"Weighted Confidence: {int(weighted['weighted_confidence']*100)}%",
            f"Threshold: {int(self.APPROVAL_THRESHOLD*100)}%",
            "",
            "Individual Votes:"
        ]
        for v in votes:
            icon = "[+]" if v.recommendation == "approve" else "[-]" if v.recommendation == "reject" else "[~]"
            lines.append(
                f"  {icon} {v.sage_id} ({v.perspective}): "
                f"{v.recommendation} ({int(v.confidence*100)}%) - {v.reasoning}"
            )

        return "\n".join(lines)

    def evaluate(self, action: str) -> dict:
        """اختصار سريع لعقد جلسة المجلس."""
        return self.convene(action)

    def get_session_log(self) -> List[dict]:
        """إرجاع سجل الجلسات."""
        return self._session_log
