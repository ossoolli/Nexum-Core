import os
import json
import logging
from datetime import datetime
from core.base_agent import BaseAgent
from services.gemini_service import gemini_service
from services.email_service import email_service

logger = logging.getLogger(__name__)

class MarketingAgent(BaseAgent):
    """
    MarketingAgent — التواجد الرقمي
    يولد محتوى تسويقي ويدير قنوات النشر.
    """

    def __init__(self):
        super().__init__(
            name="marketing_agent",
            description="وكيل التسويق وصناعة المحتوى (Growth Hacker)",
            version="1.0"
        )
        self.queue_file = "/home/madarmutaz/Nexum-Core/storage/content_queue.json"

    def generate_campaign(self, topic: str, language: str = "ar") -> dict:
        """توليد حملة تسويقية متكاملة"""
        prompt = f"""
        أنت خبير تسويق رقمي. قم بإنشاء حملة تسويقية لموضوع: {topic}
        اللغة: {language}
        
        المطلوب هو JSON يحتوي على:
        1. article: مقال (800 كلمة)
        2. twitter_posts: قائمة بـ 5 تغريدات مع هاشتاقات
        3. linkedin_posts: قائمة بـ 3 منشورات احترافية
        4. instagram_bio: وصف مختصر
        
        أعد JSON فقط.
        """
        response, _ = gemini_service.ask(prompt)
        try:
            # تنظيف واستخراج JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            content = json.loads(json_match.group())
            return content
        except Exception as e:
            self.log(f"Content generation failed: {e}", level="ERROR")
            return {}

    def schedule_post(self, content: dict, platform: str, schedule_time: str):
        """إضافة منشور للجدولة"""
        try:
            queue = []
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r') as f:
                    queue = json.load(f)
            
            queue.append({
                "id": len(queue) + 1,
                "platform": platform,
                "content": content,
                "schedule_time": schedule_time,
                "status": "pending"
            })
            
            with open(self.queue_file, 'w') as f:
                json.dump(queue, f, indent=4)
            return True
        except Exception as e:
            self.log(f"Scheduling failed: {e}", level="ERROR")
            return False

    def run(self, input_data: dict) -> dict:
        """تشغيل الوكيل لبناء حملة"""
        topic = input_data.get("topic")
        lang = input_data.get("language", "ar")
        
        if not topic:
            return {"status": "error", "error": "الموضوع مطلوب"}
            
        campaign = self.generate_campaign(topic, lang)
        
        if campaign:
            self.record_metric("campaigns_generated", self.metrics.get("campaigns_generated", 0) + 1)
            return {"status": "success", "campaign": campaign}
            
        return {"status": "error", "error": "فشل توليد الحملة"}

marketing_agent = MarketingAgent()
