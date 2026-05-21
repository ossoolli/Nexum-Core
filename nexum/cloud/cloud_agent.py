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
    from google.adk.agents.llm_agent import LlmAgent
except ImportError:
    LlmAgent = None

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
        if LlmAgent:
            for service in ["storage", "bigquery", "compute", "logging", "monitoring", "aiplatform"]:
                try:
                    toolset = gcp_mcp.get_toolset(service)
                    if toolset:
                        self._tools.append(toolset)
                except Exception as e:
                    self.log(f"تعذر تحميل {service}: {e}", level="WARNING")

            # وكيل Gemini مع كل أدوات GCP
            try:
                self._agent = LlmAgent(
                    model="gemini-1.5-flash-latest",
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
            except Exception as e:
                self.log(f"Failed to init LlmAgent: {e}", level="ERROR")
                self._agent = None
        else:
            self._agent = None
            self.log("LlmAgent (ADK) not available", level="ERROR")

    def run(self, input_data: dict) -> dict:
        command = input_data.get("text", "")
        if not self._agent:
            return {"status": "error", "error": "Cloud Agent ADK is not initialized. Check dependencies."}
            
        try:
            # تنفيذ الأمر عبر الوكيل الذكي
            response = self._agent.run(command)
            # استخراج النص من رد الوكيل (ADK response format)
            return {"status": "success", "output": str(response)}
        except Exception as e:
            self.log(f"Cloud command failure: {e}", level="ERROR")
            return {"status": "error", "error": str(e)}

# Singleton
cloud_agent = CloudAgent()
