"""
🏗️ BotBuilderAgent — يبني بوتات Telegram كاملة من وصف نصي
===========================================================
يرث من BaseAgent — يستخدم LLM + قوالب لتوليد بوتات جاهزة.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.base_agent import BaseAgent
from core.bot_fleet import bot_fleet


class BotBuilderAgent(BaseAgent):
    """مهندس بوتات — يحول وصفاً نصياً لبوت Telegram عامل"""

    DOMAIN_PERSONAS = {
        "عقارات": "أنت مساعد عقاري ذكي. تساعد في البحث عن عقارات، مقارنة الأسعار، وتقديم تقييمات موثوقة للسوق العقاري.",
        "خدمة عملاء": "أنت وكيل خدمة عملاء احترافي. ترد بأدب ولطف، تحل مشاكل العملاء بكفاءة، وتصعّد للإدارة عند الحاجة.",
        "أخبار": "أنت بوت إخباري. تجلب آخر الأخبار، تلخّصها بوضوح، وتنشرها بتنسيق احترافي.",
        "تجارة": "أنت مساعد تجارة إلكترونية. تعرض المنتجات، تدير الطلبات، وتساعد العملاء في الشراء.",
        "جدولة": "أنت مساعد جدولة ذكي. تدير المواعيد، ترسل تذكيرات، وتنظّم الجداول الزمنية.",
        "عام": "أنت مساعد ذكي متعدد المهام. تجيب على الأسئلة بدقة، تقدم معلومات مفيدة، وتساعد في المهام اليومية.",
    }

    def __init__(self):
        super().__init__(
            name="bot_builder",
            description="يبني بوتات Telegram كاملة من وصف نصي",
            version="1.0"
        )

    def run(self, input_data: dict) -> dict:
        """نقطة الدخول الرئيسية"""
        return self.build_bot_from_description(
            description=input_data.get("description", "بوت مساعد عام"),
            name=input_data.get("name", "my_bot"),
            token=input_data.get("token", ""),
            admin_id=input_data.get("admin_id", 0)
        )

    def build_bot_from_description(
        self,
        description: str,
        name: str,
        token: str,
        admin_id: int
    ) -> dict:
        """
        يبني بوت كامل من وصف نصي:
        1. يولّد شخصية مناسبة
        2. يحدد القدرات من الوصف
        3. يستدعي BotFleet.spawn_bot()
        """
        try:
            self.log(f"Building bot '{name}' from: {description[:60]}")

            # تحديد الشخصية
            persona = self.generate_bot_persona(description)

            # تحديد القدرات تلقائياً
            capabilities = self._detect_capabilities(description)

            # إنشاء البوت
            result = bot_fleet.spawn_bot(
                name=name,
                token=token,
                personality=persona,
                capabilities=capabilities,
                admin_id=admin_id
            )

            self.record_metric("bots_built", self.metrics.get("bots_built", 0) + 1)
            return result

        except Exception as e:
            self.log(f"Build failed: {e}", level="ERROR")
            return {"status": "error", "error": str(e)}

    def generate_bot_persona(self, domain_or_description: str) -> str:
        """يولّد system_instruction مناسب للمجال"""
        lower = domain_or_description.lower()
        for key, persona in self.DOMAIN_PERSONAS.items():
            if key in lower:
                return persona
        # إذا لم يطابق أي مجال → نستخدم الوصف كشخصية
        return f"أنت مساعد ذكي متخصص في: {domain_or_description}. تتحدث بالعربية وتقدم إجابات دقيقة ومفيدة."

    def add_capability(self, bot_name: str, capability: str) -> bool:
        """يضيف قدرة لبوت موجود"""
        try:
            registry = bot_fleet._load_registry()
            bot = registry["bots"].get(bot_name)
            if not bot:
                return False
            if capability not in bot.get("capabilities", []):
                bot["capabilities"].append(capability)
            bot_fleet._save_registry()
            bot_fleet.restart_bot(bot_name)
            return True
        except Exception:
            return False

    def _detect_capabilities(self, description: str) -> list:
        """يحدد القدرات تلقائياً من الوصف"""
        caps = ["chat"]
        lower = description.lower()
        if any(w in lower for w in ["بحث", "search", "ابحث"]):
            caps.append("web_search")
        if any(w in lower for w in ["قناة", "نشر", "بث", "channel", "broadcast"]):
            caps.append("broadcast")
        if any(w in lower for w in ["اختبار", "فحص", "test", "qa"]):
            caps.append("qa")
        if any(w in lower for w in ["ملف", "صورة", "pdf", "file"]):
            caps.append("file_analysis")
        return caps


# Singleton
bot_builder = BotBuilderAgent()
