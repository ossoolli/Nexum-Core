# -*- coding: utf-8 -*-
"""
🧠 PromptCompiler — محرك تجميع وتحسين المطالبات (v1.0.0)
======================================================
- يقوم بتحليل تاريخ نجاح وفشل المهام (Task History).
- يستخدم تقنيات مستوحاة من DSPy لتحسين المطالبات البرمجية (Prompts).
- يولد نسخاً محسنة من التعليمات الأساسية (System Instructions) لكل نوع من الوكلاء.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
logger = logging.getLogger("nexum.learning.prompt_compiler")

class PromptCompiler:
    def __init__(self, gemini_service=None):
        self.gemini = gemini_service
        self.registry_path = BASE_DIR / "storage" / "learning" / "prompt_registry.json"
        self.history_path = BASE_DIR / "storage" / "sovereign_memory" / "evolution_history.json"
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_registry()

    def _load_registry(self):
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    self.registry = json.load(f)
            except Exception:
                self.registry = {}
        else:
            self.registry = {}

    def _save_registry(self):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=4)

    def get_optimized_prompt(self, context_key: str, default_prompt: str) -> str:
        """جلب المطالبة المحسنة إذا كانت موجودة، وإلا إرجاع الافتراضية"""
        return self.registry.get(context_key, {}).get("optimized_prompt", default_prompt)

    async def compile_all(self):
        """دورة التجميع والتحسين الشاملة"""
        logger.info("[PromptCompiler] Starting global prompt compilation cycle...")
        
        # تحليل سجل التطور لاكتشاف الأخطاء المتكررة
        history = self._load_history()
        
        # أنواع الوكلاء/السياقات التي نحتاج لتحسينها
        contexts = ["agent_synthesis", "self_healing", "task_execution"]
        
        for ctx in contexts:
            await self.optimize_context(ctx, history)

    def _load_history(self) -> List[Dict[str, Any]]:
        if self.history_path.exists():
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    async def optimize_context(self, context_key: str, history: List[Dict[str, Any]]):
        """تحسين مطالبة محددة بناءً على البيانات التاريخية"""
        if not self.gemini:
            from services.gemini_service import gemini_service
            self.gemini = gemini_service

        # استخراج الأخطاء والنجاحات المتعلقة بهذا السياق
        failures = []
        successes = []
        
        for record in history:
            # مثال بسيط للتصفية (يمكن توسيعه)
            if context_key == "self_healing" and record.get("repaired_agents"):
                successes.append(f"Repaired: {record['repaired_agents']}")
            if record.get("status") == "error":
                failures.append(record.get("discovered_gaps", []))

        current_prompt = self.registry.get(context_key, {}).get("optimized_prompt", "Standard Instructions")
        
        # طلب التحسين من Gemini (DSPy logic)
        optimization_prompt = (
            f"You are the Nexum Prompt Optimizer (Inspired by DSPy/GEPA).\n"
            f"Context: {context_key}\n"
            f"Current Prompt: {current_prompt}\n"
            f"Historical Success Patterns: {successes[:5]}\n"
            f"Historical Failure Patterns: {failures[:5]}\n\n"
            f"Task: Rewrite the 'System Instruction' for this context to be more precise, robust, "
            f"and specifically address the observed failure patterns. "
            f"Ensure the tone is Sovereign, Technical, and emphasizes Security (HMAC, Sandbox).\n"
            f"Output ONLY the new optimized prompt text."
        )

        res, _ = self.gemini.ask(optimization_prompt)
        
        if res and len(res) > 50:
            self.registry[context_key] = {
                "optimized_prompt": res,
                "last_optimized": str(Path().cwd()), # Placeholder for time
                "version": self.registry.get(context_key, {}).get("version", 0) + 1
            }
            self._save_registry()
            logger.info(f"[PromptCompiler] Optimized prompt for {context_key} (v{self.registry[context_key]['version']})")

# Singleton
prompt_compiler = PromptCompiler()
