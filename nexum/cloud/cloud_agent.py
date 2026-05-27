"""
☁️ CloudAgent — الوكيل السيادي لـ Google Cloud
يتحدث بالعربية ويتحكم في كل موارد GCP
"""
import os
import sys

# ضمان الوصول للمجلد الرئيسي
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from google.adk import Agent
except ImportError:
    Agent = None

from nexum.cloud.gcp_mcp import gcp_mcp
from core.base_agent import BaseAgent

class CloudAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="cloud_agent",
            description="يتحكم في Google Cloud — Storage، BigQuery، Compute، Monitoring",
            version="1.0"
        )
        # تحميل الأدوات من MCP Servers
        self._tools = []
        if Agent:
            for service in ["storage", "bigquery", "compute", "logging", "monitoring", "aiplatform"]:
                try:
                    toolset = gcp_mcp.get_toolset(service)
                    if toolset:
                        self._tools.append(toolset)
                except Exception as e:
                    self.log(f"تعذر تحميل {service}: {e}", level="WARNING")

            # وكيل Gemini مع كل أدوات GCP
            try:
                self._agent = Agent(
                    model="gemini-3.5-flash",
                    name="nexum_cloud_agent",
                    instruction="""
أنت NEXUM Cloud Agent — المتحكم السيادي في Google Cloud للمايسترو معتز.

مشروعك: mytest-496209
صلاحياتك: BigQuery، Cloud Storage، Compute Engine، Logging، Monitoring، Vertex AI

قواعد:
1. تحدث بالعربية دائماً
2. نفّذ ما يطلبه المايسترو مباشرة بدون تردد
3. بعد كل عملية أخبره بالنتيجة بوضوح
4. إذا فشلت العملية أخبره بالسبب واقترح البديل
5. للعمليات الحساسة (حذف، تعديل إعدادات) اطلب تأكيداً
                    """,
                    tools=self._tools,
                )
                from google.adk.runners import InMemoryRunner
                self._runner = InMemoryRunner(self._agent, app_name="NEXUM_Cloud")
            except Exception as e:
                self.log(f"Failed to init Agent or InMemoryRunner: {e}", level="ERROR")
                self._agent = None
                self._runner = None
        else:
            self._agent = None
            self._runner = None
            self.log("Agent (ADK) not available", level="ERROR")

    def run(self, input_data: dict) -> dict:
        command = input_data.get("text", "")
        if not self._agent or not self._runner:
            return {"status": "error", "error": "Cloud Agent ADK or runner is not initialized. Check dependencies."}
            
        try:
            session_id = "cloud_session"
            user_id = "admin"

            # إنشاء الجلسة في InMemorySessionService إذا لم تكن موجودة لتجنب Session Not Found
            session = self._runner.session_service.get_session_sync(
                app_name=self._runner.app_name,
                user_id=user_id,
                session_id=session_id
            )
            if not session:
                self._runner.session_service.create_session_sync(
                    app_name=self._runner.app_name,
                    user_id=user_id,
                    session_id=session_id
                )

            from google.genai import types
            msg = types.Content(parts=[types.Part(text=command)])

            # تشغيل التدفق الرسومي التشاركي وجمع الأحداث حياً بشكل متزامن للمطور
            events = self._runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=msg
            )

            output_str = ""
            for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            output_str += part.text

            if not output_str:
                output_str = "🟢 [Cloud Agent] Command executed, but returned an empty response."

            return {"status": "success", "output": output_str}
        except Exception as e:
            self.log(f"Cloud command failure: {e}", level="ERROR")
            return {"status": "error", "error": str(e)}

# Singleton
cloud_agent = CloudAgent()
