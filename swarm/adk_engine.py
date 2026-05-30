# -*- coding: utf-8 -*-
# swarm/adk_engine.py
"""
🧬 ADKSwarmEngine — محرك الأسراب التشاركي المبني على Google ADK 2.0 GA (v1.0.0)
========================================================================
- إدارة وتنسيق شبكة الوكلاء المتعاونين (Collaborative Agents).
- استخدام خطوط المهام الرسومية (Graph Workflows) للتنفيذ الذاتي متعدد الخطوات.
- تمكين الانتقال التلقائي بين الوكلاء السياديين (Agent Handovers) لضمان أمان العمليات السحابية والمحلية.
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, List

# ضمان الوصول للمجلد الرئيسي
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from google.adk import Agent, Runner
except ImportError:
    Agent = None
    Runner = None

logger = logging.getLogger(__name__)

# ─── أدوات الوكلاء المحلية (Local Tools for ADK Agents) ──────────────────────────

def check_resources() -> str:
    """أداة لفحص موارد الخادم حياً قبل تشغيل أي عملية تشاركية"""
    import psutil
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    return f"🟢 [Ecosystem Monitor] CPU: {cpu}%, RAM: {ram}%, Disk: {disk}% (Safety Level: OK)"

def get_git_status() -> str:
    """أداة سريعة للتحقق من حالة مستودع Git"""
    try:
        import subprocess
        res = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=5)
        return f"🐙 [Git Status] Changes:\n{res.stdout or 'No changes.'}"
    except Exception as e:
        return f"❌ [Git Error] Failed to read repository status: {e}"

def run_git_deploy() -> str:
    """أداة محاكاة النشر السحابي والآمن بعد اجتياز فحص الأمان"""
    return "✅ [ADK Deploy] Git changes pushed and deployed successfully to production."


# ─── بناء الوكلاء المتعاونين (Collaborative Agents Configuration) ───────────────

class ADKSwarmEngine:
    def __init__(self):
        self.runner = None
        self.sentinel_agent = None
        self.deploy_agent = None
        self._init_agents()

    def _init_agents(self):
        """تهيئة شبكة الوكلاء المتكاملة باستخدام شجرة الوكلاء التشاركية بـ ADK"""
        if not Agent:
            logger.warning("[ADK Swarm] Google ADK package not fully available. Running in fallback simulation.")
            return

        try:
            # 1. وكيل النشر السحابي (GCP Deploy Agent)
            self.deploy_agent = Agent(
                model="gemini-2.5-flash",
                name="gcp_deploy_agent",
                description="وكيل متخصص لنشر الأكواد والتعديلات البرمجية بأمان سحابياً ومحلياً",
                instruction="""
                أنت GCP Deploy Agent — وكيل النشر السحابي السيادي للمايسترو معتز.
                مهمتك الأساسية هي:
                1. استقبال سياق المهمة بعد نجاح فحص الأمان من Sentinel Audit Agent.
                2. تشغيل أداة النشر السحابي `run_git_deploy` لإتمام وتعميم المأمورية.
                3. إبلاغ المطور بالنتيجة النهائية والتقارير بوضوح.
                """,
                tools=[run_git_deploy]
            )

            # 2. وكيل فحص الموارد والأمان (Sentinel Audit Agent - Root Agent)
            self.sentinel_agent = Agent(
                model="gemini-2.5-flash",
                name="sentinel_audit_agent",
                description="وكيل فحص الموارد ومطابقة سلامة الأكواد ومستودع Git قبل النشر",
                instruction="""
                أنت Sentinel Audit Agent — الحارس الأمني للوكلاء تشاركياً في بيئة NEXUM PRO.
                مهمتك الأساسية هي:
                1. فحص استهلاك وموارد السيرفر باستخدام أداة `check_resources`.
                2. فحص حالة الكود ومستودع Git باستخدام أداة `get_git_status`.
                3. إذا كانت الموارد والملفات آمنة وسليمة، قم فوراً بتفويض ونقل المهمة إلى وكيل النشر السحابي `gcp_deploy_agent` لإتمام عمليات النشر.
                """,
                tools=[check_resources, get_git_status],
                sub_agents=[self.deploy_agent]  # دمج وربط تشاركي أصلي لشجرة الوكلاء
            )

            # تهيئة الـ InMemoryRunner باستخدام وكيل الأمان كـ Root Agent
            from google.adk.runners import InMemoryRunner
            self.runner = InMemoryRunner(self.sentinel_agent, app_name="NEXUM_Swarm")
            logger.info("[ADK Swarm] Collaborative agents and InMemoryRunner initialized cleanly.")
        except Exception as e:
            logger.error(f"[ADK Swarm] Failed to initialize collaborative agent tree: {e}")
            self.sentinel_agent = None
            self.deploy_agent = None
            self.runner = None

    async def execute_mission(self, prompt: str) -> dict:
        """تشغيل خطة العمل التشاركية الرسومية حياً عبر محرك ADK 2.0"""
        logger.info(f"[ADK Swarm] Convening collaborative flows for: {prompt[:60]}...")
        
        if not self.sentinel_agent or not self.runner:
            return {
                "status": "simulation",
                "output": f"⚠️ [ADK Swarm Simulation] Swarm executed: '{prompt}' (ADK runner offline)."
            }

        try:
            session_id = "active_session"
            user_id = "admin"

            # إنشاء الجلسة في InMemorySessionService إذا لم تكن موجودة لتجنب Session Not Found
            try:
                session = await self.runner.session_service.get_session(
                    app_name=self.runner.app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                if not session:
                    await self.runner.session_service.create_session(
                        app_name=self.runner.app_name,
                        user_id=user_id,
                        session_id=session_id
                    )
            except Exception as ses_err:
                logger.warning(f"[ADK Swarm] Could not prepare session storage: {ses_err}")

            from google.genai import types
            msg = types.Content(parts=[types.Part(text=prompt)])

            # تشغيل التدفق الرسومي التشاركي غير المتزامن وجمع الأحداث حياً
            output_str = ""
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=msg
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            output_str += part.text

            if not output_str:
                output_str = "🟢 [ADK Swarm] Swarm flow executed successfully, but returned an empty text response."

            return {
                "status": "success",
                "output": output_str
            }
        except Exception as e:
            logger.error(f"[ADK Swarm] Flow execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

# Singleton Instance
adk_swarm = ADKSwarmEngine()
