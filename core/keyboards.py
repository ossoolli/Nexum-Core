import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

class HybridInterfaceBuilder:
    """
    Hybrid Telegram Interface Architecture (Conversational Layer + Mini App)
    يولد الأزرار السريعة للمحادثة ويربط النظام بطبقة تطبيق الويب المصغر.
    """
    
    def __init__(self):
        # رابط التطبيق المصغر المرفوع (أو المحلي عبر ngrok)
        self.webapp_url = os.getenv("WEBAPP_URL", "https://your-ngrok-or-cloud-run-url.com")

    def build_main_control_plane(self) -> InlineKeyboardMarkup:
        """
        واجهة الطبقة الأولى السريعة (Quick Controls Layer)
        تُدمج مع المحادثة لاتخاذ القرارات أو فتح لوحة التحكم السيادية.
        """
        markup = InlineKeyboardMarkup(row_width=2)
        
        # 1. زر التحكم السيادي (يفتح الـ Mini App) - أهم عنصر في المنظومة
        btn_webapp = InlineKeyboardButton(
            text="🎛️ Sovereign Control Panel", 
            web_app=WebAppInfo(url=self.webapp_url)
        )
        markup.add(btn_webapp)

        # 2. أزرار المهام السريعة الحوارية
        btn_status = InlineKeyboardButton(text="📊 Runtime Status", callback_data="hw_status")
        btn_agents = InlineKeyboardButton(text="🤖 Agent Roster", callback_data="list_agents")
        markup.row(btn_status, btn_agents)
        
        btn_github = InlineKeyboardButton(text="🐙 Auto-Deploy Mode", callback_data="github_deploy")
        btn_logs = InlineKeyboardButton(text="📋 Audit Logs", callback_data="audit_logs")
        markup.row(btn_github, btn_logs)
        
        return markup

    def build_agent_approval_card(self, agent_name: str, task: str) -> InlineKeyboardMarkup:
        """
        زر الموافقة (Approval/Governance Layer)
        تستخدم عندما يطلب وكيل القيام بمهمة خطيرة تقع خارج صلاحياته المباشرة.
        """
        markup = InlineKeyboardMarkup(row_width=2)
        btn_approve = InlineKeyboardButton(text="✅ Approve", callback_data=f"agent_approve:{agent_name}")
        btn_deny = InlineKeyboardButton(text="❌ Deny", callback_data=f"agent_deny:{agent_name}")
        markup.row(btn_approve, btn_deny)
        return markup

ui_builder = HybridInterfaceBuilder()
