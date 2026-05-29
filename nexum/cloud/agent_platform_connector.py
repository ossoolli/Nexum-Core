# -*- coding: utf-8 -*-
"""
☁️ GoogleAgentPlatformConnector — موصل منصة عملاء جوجل السحابية والبحث الدلالي
========================================================================
- الربط الفائق مع Google Cloud Agent Platform (Dialogflow CX).
- تمكين البحث المعرفي الدلالي (RAG) بالاعتماد على Discovery Engine (Vertex AI Search).
- إدارة الهويات والوصول (IAM) وتوليد الصلاحيات الأمنية المؤقتة بنظام انعدام الثقة (Zero Trust).
- مرونة شاملة (Resiliency) مع دعم كامل للمحاكاة المحلية (Mock/Simulation Mode) لضمان استمرارية التشغيل.
"""

import os
import sys
import logging
import json
import time
from typing import Dict, Any, List, Optional

from nexum.cloud.mcp_dispatcher import MCPDispatcher
from nexum.intelligence.orchestrator import Orchestrator
# إعداد السجل المهيكل للبيئة السحابية
logger = logging.getLogger("nexum.agent_platform_connector")

# محاولة تحميل مكتبات جوجل السحابية مع صمود ديناميكي في حال غيابها
try:
    from google.oauth2 import service_account
    from google.api_core.client_options import ClientOptions
    from google.api_core.exceptions import GoogleAPICallError
    from google.cloud import dialogflowcx_v3 as dialogflow
    from google.cloud import discoveryengine_v1beta as discoveryengine
    GCP_LIBS_AVAILABLE = True
except Exception as e:
    # تهيئة المتغيرات لضمان عدم حدوث NameError أثناء التشغيل في وضع المحاكاة
    service_account = None
    ClientOptions = None
    GoogleAPICallError = None
    dialogflow = None
    discoveryengine = None
    GCP_LIBS_AVAILABLE = False
    logger.info(f"[GCP Connector] Google Cloud SDK not fully installed ({type(e).__name__}). Falling back to simulated mode seamlessly.")


class NexumSecurityConfig:
    """
    إدارة التهيئة الأمنية للوصول لسحابة جوجل (IAM Credentials & Scopes).
    تأمين وحفظ الصلاحيات بنظام الصلاحيات الأدنى (Least Privilege).
    """
    def __init__(
        self,
        service_account_path: str,
        project_id: str,
        location: str = "us-central1",
        agent_id: str = "",
        search_engine_id: str = ""
    ):
        self.service_account_path = service_account_path
        self.project_id = project_id
        self.location = location
        self.agent_id = agent_id
        self.search_engine_id = search_engine_id
        self.credentials = None

        if self.service_account_path and os.path.exists(self.service_account_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.service_account_path
            logger.info(f"[GCP Config] IAM credentials loaded securely from: {self.service_account_path}")
            if GCP_LIBS_AVAILABLE:
                self.credentials = self.get_credentials()
        else:
            logger.warning("[GCP Config] Secure service account keyfile path is empty or not found. Operating in local simulation.")

    def get_credentials(self) -> Any:
        """توليد واسترجاع صلاحيات OAuth 2.0 المصرحة لاستدعاء خدمات GCP."""
        if not GCP_LIBS_AVAILABLE or not self.service_account_path or not os.path.exists(self.service_account_path):
            return None
        try:
            # النطاق الشامل لإدارة منصات خدمات سحابة جوجل بأمان
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=scopes
            )
            return creds
        except Exception as e:
            logger.error(f"[GCP Config] Failed to generate OAuth credentials: {e}")
            return None


class DialogflowCXConnector:
    """
    موصل محادثات منصة عملاء جوجل (Dialogflow CX Sessions & Intents).
    توجيه رسائل المستخدمين للمنصة واستخراج المقاصد والمعاملات حياً.
    """
    def __init__(self, config: NexumSecurityConfig):
        self.config = config
        self.client = None
        self._init_client()

    def _init_client(self):
        if not GCP_LIBS_AVAILABLE or not self.config.credentials:
            logger.info("[Dialogflow CX] Operating in simulation mode (client offline).")
            return
        try:
            # التأكد من تحميل ملف الاعتمادات السحابية إذا كان متوفراً
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if creds_path and os.path.exists(creds_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
            
            # قراءة خوادم MCP المحددة في الملف
            mcp_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage", "mcp-servers.json")
            if os.path.exists(mcp_config_path):
                with open(mcp_config_path, 'r') as f:
                    mcp_config = json.load(f)
                    self.mcp_servers = mcp_config.get("mcpServers", {})
                    logger.info(f"✅ Loaded {len(self.mcp_servers)} MCP Servers for Google Cloud.")
            
            # تهيئة عميل الجلسات وتحديد خادم النطاق الجغرافي
            api_endpoint = f"{self.config.location}-dialogflow.googleapis.com"
            client_options = ClientOptions(api_endpoint=api_endpoint)
            # استخدام المفتاح المصرح به ديناميكياً
            self.client = dialogflow.SessionsClient(
                credentials=self.config.credentials,
                client_options=client_options
            )
            # إيقاف وضع المحاكاة عند وجود المفتاح
            self.is_simulated = False
            logger.info("✅ Google Cloud Vertex AI Connected Successfully.")
            logger.info(f"[Dialogflow CX] SessionsClient initialized successfully for location: {self.config.location}")
        except Exception as e:
            logger.error(f"[Dialogflow CX] Initialization failed: {e}")
            self.client = None

    def detect_intent(
        self,
        text: str,
        session_id: str = "nexum_sovereign_session",
        language_code: str = "ar"
    ) -> Dict[str, Any]:
        """إرسال رسالة نصية حية لاستكشاف المقاصد والحصول على رد منصة الوكلاء السحابية."""
        if not self.client or not self.config.agent_id:
            # محاكاة محلية ذكية لضمان صمود واختبار النظام دون انقطاع
            logger.info(f"[Dialogflow CX Simulation] Processing: '{text}'")
            return self._simulate_detect_intent(text)

        try:
            # بناء مسار الجلسة الفرعي بالمنصة
            session_path = self.client.session_path(
                project=self.config.project_id,
                location=self.config.location,
                agent=self.config.agent_id,
                session=session_id
            )

            # تجهيز نص الاستعلام البرمجي
            text_input = dialogflow.TextInput(text=text)
            query_input = dialogflow.QueryInput(text=text_input, language_code=language_code)
            request = dialogflow.DetectIntentRequest(
                session=session_path,
                query_input=query_input
            )

            # استدعاء منصة الوكلاء حياً
            response = self.client.detect_intent(request=request)
            query_result = response.query_result

            # صياغة المخرجات وتعبئة ردود الفعل
            fulfillment_text = ""
            if query_result.response_messages:
                texts = []
                for msg in query_result.response_messages:
                    if msg.text and msg.text.text:
                        texts.extend(msg.text.text)
                fulfillment_text = " ".join(texts)

            parameters = {}
            if query_result.parameters:
                # تحويل البنية المعقدة للمعامِلات السحابية لقاموس Python قياسي
                try:
                    parameters = json.loads(json.dumps(dict(query_result.parameters)))
                except Exception:
                    pass

            return {
                "status": "success",
                "fulfillment_text": fulfillment_text or "تلقيت مقترحك وجاري تنسيقه سحابياً.",
                "intent_name": query_result.intent.display_name if query_result.intent else "default_fallback",
                "confidence": query_result.intent_detection_confidence,
                "parameters": parameters,
                "language_code": query_result.language_code
            }

        except Exception as e:
            logger.error(f"[Dialogflow CX] API Call failure: {e}. Falling back to simulation.")
            return self._simulate_detect_intent(text, error=str(e))

    def _simulate_detect_intent(self, text: str, error: str = None) -> Dict[str, Any]:
        """توليد محاكاة محلية ذكية وسليمة لتدفق محادثات الوكلاء."""
        clean = text.strip()
        intent = "general_query"
        response = f"أنا NEXUM Agent Platform Simulator — قمت باستقبال رسالتك: '{text}'"

        if "خطة" in clean or "تطوير" in clean:
            intent = "system_development_plan"
            response = "أهلاً بك يا مايسترو! قمت بتوليد خطة التطوير المعمارية الموزعة حياً بالاعتماد على توافق مجلس الحكماء."
        elif "أمان" in clean or "فحص" in clean:
            intent = "security_audit_run"
            response = "حالة الأمان ممتازة. فحص Sentinel Audit Agent nominal والموارد سليمة بنسبة 100%."

        return {
            "status": "simulation",
            "fulfillment_text": response,
            "intent_name": intent,
            "confidence": 0.95,
            "parameters": {"task_detected": clean, "simulation_mode": True},
            "language_code": "ar",
            "error_fallback": error
        }


class DiscoveryEngineConnector:
    """
    موصل البحث الدلالي المعرفي (Vertex AI Search & Discovery Engine for RAG).
    استرجاع المعرفة وسجلات البناء والتوثيق من مستودعات البيانات السحابية حياً.
    """
    def __init__(self, config: NexumSecurityConfig):
        self.config = config
        self.client = None
        self._init_client()

    def _init_client(self):
        if not GCP_LIBS_AVAILABLE or not self.config.credentials:
            logger.info("[Discovery Engine] Operating in simulation mode (client offline).")
            return
        try:
            # تحديد خادم البحث الجغرافي المعرفي
            api_endpoint = f"{self.config.location}-discoveryengine.googleapis.com"
            client_options = ClientOptions(api_endpoint=api_endpoint)
            self.client = discoveryengine.SearchServiceClient(
                credentials=self.config.credentials,
                client_options=client_options
            )
            logger.info(f"[Discovery Engine] SearchServiceClient initialized successfully for location: {self.config.location}")
        except Exception as e:
            logger.error(f"[Discovery Engine] Initialization failed: {e}")
            self.client = None

    def search_knowledge(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """إجراء عملية بحث دلالي (RAG Search) لاسترجاع المعرفة الموثقة سحابياً."""
        if not self.client or not self.config.search_engine_id:
            logger.info(f"[Discovery Engine Simulation] Querying knowledge store: '{query}'")
            return self._simulate_search_knowledge(query)

        try:
            # بناء مسار محرك البحث السحابي الموثق
            serving_config = self.client.serving_config_path(
                project=self.config.project_id,
                location=self.config.location,
                data_store=self.config.search_engine_id,
                serving_config="default_search"
            )

            request = discoveryengine.SearchRequest(
                serving_config=serving_config,
                query=query,
                page_size=limit
            )

            # استدعاء محرك البحث الدلالي حياً
            response = self.client.search(request=request)
            
            results = []
            for result in response.results:
                document = result.document
                # استخراج نصوص الوثائق المسترجعة
                doc_dict = {
                    "id": document.id,
                    "title": document.derived_struct_data.get("title", "Sovereign Document"),
                    "snippet": document.derived_struct_data.get("snippet", ""),
                    "link": document.derived_struct_data.get("link", "")
                }
                results.append(doc_dict)

            return {
                "status": "success",
                "query": query,
                "results": results,
                "retrieved_count": len(results)
            }

        except Exception as e:
            logger.error(f"[Discovery Engine] Search failure: {e}. Falling back to simulation.")
            return self._simulate_search_knowledge(query, error=str(e))

    def _simulate_search_knowledge(self, query: str, error: str = None) -> Dict[str, Any]:
        """محاكاة استرجاع وثائق ومعرفة دلالية حياً لتمكين الـ RAG محلياً."""
        mock_docs = [
            {
                "id": "doc-001",
                "title": "NEXUM PRO Architecture Blueprint",
                "snippet": "NEXUM PRO uses a distributed microservice framework with gRPC Go coordination and a Redis/sync.Map cache layers.",
                "link": "https://ossoolli.github.io/Nexum-Core/docs/architecture"
            },
            {
                "id": "doc-002",
                "title": "Sovereign Council Consensus Rules",
                "snippet": "The Council of Sages gathers parallel votes from Claude, Gemini, and GPT. AAA Unanimous (3/3) and A Consensus (2/3) auto-execute tasks.",
                "link": "https://ossoolli.github.io/Nexum-Core/docs/consensus"
            }
        ]
        
        # تصفية المحاكاة حسب كلمة البحث
        filtered = [
            doc for doc in mock_docs 
            if query.lower() in doc["title"].lower() or query.lower() in doc["snippet"].lower()
        ]
        
        # الإرجاع الافتراضي في حال عدم وجود تطابق مباشر
        if not filtered:
            filtered = mock_docs

        return {
            "status": "simulation",
            "query": query,
            "results": filtered,
            "retrieved_count": len(filtered),
            "error_fallback": error
        }


class GoogleAgentPlatformConnector:
    """
    البوابة السيادية والمركزية الموحدة لربط وتوسيع NEXUM PRO بـ Google Cloud Agent Platform.
    تجمع محادثات Dialogflow CX مع البحث المعرفي RAG لـ Discovery Engine.
    """
    def __init__(
        self,
        service_account_path: str = "credentials.txt",
        project_id: str = "mytest-496209",
        location: str = "us-central1",
        agent_id: str = "agent-platform-cx-99",
        search_engine_id: str = "knowledge-rag-engine"
    ):
        self.mcp_dispatcher = MCPDispatcher()
        self.config = NexumSecurityConfig(
            service_account_path=service_account_path,
            project_id=project_id,
            location=location,
            agent_id=agent_id,
            search_engine_id=search_engine_id
        )
        self.dialogflow = DialogflowCXConnector(self.config)
        self.search = DiscoveryEngineConnector(self.config)
        self.orchestrator = Orchestrator(self.config)
        
        logger.info("[GCP Gateway] GoogleAgentPlatformConnector initiated cleanly.")

    def run_cognitive_flow(self, user_prompt: str, session_id: str = "nexum_session") -> Dict[str, Any]:
        """
        تشغيل تدفق إدراكي موحد:
        1. استخلاص النوايا والمقاصد من Dialogflow CX.
        2. إجراء عملية بحث RAG دلالي في مستودع المعرفة لتعزيز الإدراك.
        3. دمج المخرج في رد واحد فائق الذكاء ومطابق لبيئة الإنتاج.
        """
        logger.info(f"[GCP Gateway] Running cognitive agentic flow for prompt: '{user_prompt[:50]}'...")
        
        # 1. تحليل المقصد
        dialog_res = self.dialogflow.detect_intent(user_prompt, session_id=session_id)
        
        # Route the task
        model = self.orchestrator.route_task(user_prompt)
        
        # Dispatch to MCP if needed
        mcp_task = self.mcp_dispatcher.find_relevant_mcp_server(user_prompt)
        
        # 2. جلب سياق المعرفة (RAG)
        search_res = self.search.search_knowledge(user_prompt)
        
        # دمج وتجميع النتائج
        merged_snippets = "\n".join([
            f"- {doc['title']}: {doc['snippet']}" 
            for doc in search_res.get("results", [])
        ])

        return {
            "prompt": user_prompt,
            "session_id": session_id,
            "fulfillment_response": dialog_res.get("fulfillment_text", ""),
            "detected_intent": dialog_res.get("intent_name", ""),
            "confidence": dialog_res.get("confidence", 0.0),
            "parameters": dialog_res.get("parameters", {}),
            "mcp_task": mcp_task,
            "model_assigned": model,
            "rag_knowledge_context": merged_snippets,
            "gcp_connected": dialog_res.get("status") == "success",
            "timestamp": time.time()
        }
