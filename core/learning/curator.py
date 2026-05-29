# -*- coding: utf-8 -*-
"""
Curator — محرك تقطير المهارات والذكاء (v1.0.0)
==============================================
- يقوم بتقطير المهام الناجحة من كانبان إلى صيغة مهارات (SKILL.md).
- يتكامل مع مجلس الحكماء للتصديق على المهارات الجديدة.
"""

import os
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
logger = logging.getLogger(__name__)

class Curator:
    def __init__(self, council=None):
        self.council = council
        self.skills_dir = BASE_DIR / "storage" / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    async def distill_task(self, task: Dict[str, Any]) -> Optional[str]:
        """تقطير مهمة ناجحة إلى مهارة (SKILL.md) بعد تصديق المجلس"""
        logger.info(f"[Curator] Distilling task: {task.get('title')}")
        
        # 1. تصميم المهارة
        skill_proposal = self._propose_skill(task)
        
        # 2. عرضها على المجلس
        if self.council:
            consensus = await self.council.deliberate(
                f"Approve skill distillation for: {task.get('title')}", 
                code=skill_proposal
            )
            if not consensus.approved:
                logger.warning(f"[Curator] Skill proposal rejected by Council: {task.get('title')}")
                return None
            
            # Use merged output if available
            if consensus.merged_output:
                skill_proposal = consensus.merged_output

        # 3. حفظ المهارة
        return self._save_skill(task.get("title") or "unknown_task", skill_proposal)

    def _propose_skill(self, task: Dict[str, Any]) -> str:
        """توليد مهارة من المهمة (باستخدام Gemini)"""
        from services.gemini_service import gemini_service
        prompt = (
            f"You are the Sovereign Curator. Transform this completed task into a reusable SKILL.\n"
            f"Task: {task.get('title')}\n"
            f"Description: {task.get('description')}\n"
            f"Create a SKILL.md file with YAML frontmatter (name, description, version) and markdown body.\n"
            f"The body should contain the 'How-To' instructions.\n"
            f"Output ONLY the file content."
        )
        res, _ = gemini_service.ask(prompt)
        return res

    def _save_skill(self, title: str, content: str) -> str:
        """حفظ المهارة في ملف"""
        filename = f"{title.lower().replace(' ', '_')}.md"
        file_path = self.skills_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"[Curator] Skill saved: {file_path}")
        return str(file_path)
