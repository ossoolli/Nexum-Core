# -*- coding: utf-8 -*-
"""
🔍 SemanticBrowser — محرك البحث الدلالي المتقدم (Pillar 3)
======================================================
- يستخدم Playwright لجلب محتوى المواقع.
- يستخدم Gemini لتحليل المحتوى واستخراج المعلومات المطلوبة بدقة دلالية.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger("nexum.tools.semantic_browser")

def semantic_search_web(url: str, query: str) -> str:
    """
    يقوم بزيارة موقع ويب والبحث فيه عن إجابة لسؤال محدد باستخدام الذكاء الاصطناعي.
    :param url: رابط الموقع
    :param query: السؤال أو المعلومة المطلوبة
    """
    from core.browser_sandbox import execute_browser_command
    from services.gemini_service import gemini_service
    
    # 1. جلب محتوى الصفحة (Scrape)
    res = execute_browser_command(action="scrape", url=url)
    content = res.get("output", "")
    
    if len(content) < 100:
        return f"❌ فشل جلب المحتوى من {url}"
        
    # 2. تحليل دلالي عبر Gemini
    prompt = (
        f"You are the Nexum Semantic Browser.\n"
        f"Content from {url}:\n"
        f"--------------------------\n"
        f"{content[:8000]} # Truncated for token limits\n"
        f"--------------------------\n"
        f"Task: Answer the following question based ONLY on the content above: {query}\n"
        f"If the answer is not in the content, say so."
    )
    
    answer, _ = gemini_service.ask(prompt, system_instruction="You extract precise facts from web content.")
    return answer


def advanced_scrape(url: str) -> str:
    """
    يقوم بجلب المحتوى النصي الكامل لصفحة الويب وتنسيقه بشكل مقروء وواضح.
    :param url: رابط الموقع المطلوب كشطه
    """
    from core.browser_sandbox import execute_browser_command
    
    logger.info(f"[SemanticBrowser] Running advanced scrape on {url}...")
    res = execute_browser_command(action="scrape", url=url)
    content = res.get("output", "")
    
    if len(content) < 100:
        return f"❌ فشل جلب المحتوى من {url}"
        
    return content
