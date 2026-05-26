"""
NEXUM PRIME — Interactive Sovereign Control System
====================================================
نظام واجهات تفاعلية شامل يحول التليجرام من بوت أوامر إلى لوحة تحكم سيادية.
كل شيء يعمل بالنقر، البطاقات، والقوائم الديناميكية.
"""
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


class SovereignUIBuilder:
    """
    المحرك البصري السيادي — يولّد جميع واجهات التفاعل في التليجرام.
    المبدأ: Click-first, Type-never.
    """

    def __init__(self):
        self.webapp_url = os.getenv("WEBAPP_URL", "https://ossoolli.github.io/Nexum-Core/")

    # ╔══════════════════════════════════════════╗
    # ║         الشاشة الرئيسية (Home)          ║
    # ╚══════════════════════════════════════════╝
    def build_main_control_plane(self) -> InlineKeyboardMarkup:
        """القائمة الرئيسية — 9 أقسام تفاعلية"""
        m = InlineKeyboardMarkup(row_width=2)

        # زر Mini App العلوي
        m.add(InlineKeyboardButton(
            "🎛️ Open Sovereign Dashboard",
            web_app=WebAppInfo(url=self.webapp_url)
        ))

        # الصف الأول: Runtime + Agents
        m.row(
            InlineKeyboardButton("⚡ Runtime", callback_data="menu_runtime"),
            InlineKeyboardButton("🤖 Agents", callback_data="menu_agents")
        )
        # الصف الثاني: Protocols + Deployments
        m.row(
            InlineKeyboardButton("🧬 Protocols", callback_data="menu_protocols"),
            InlineKeyboardButton("🚀 Deployments", callback_data="menu_deploy")
        )
        # الصف الثالث: AI + Security
        m.row(
            InlineKeyboardButton("🧠 AI Brain", callback_data="menu_ai"),
            InlineKeyboardButton("🛡️ Security", callback_data="menu_security")
        )
        # الصف الرابع: Memory + Docker
        m.row(
            InlineKeyboardButton("💾 Memory", callback_data="menu_memory"),
            InlineKeyboardButton("🐳 Docker", callback_data="menu_docker")
        )
        # الصف الخامس: Settings + Audit Logs
        m.row(
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("📋 Audit Logs", callback_data="audit_logs")
        )
        # الصف السادس: Google Cloud (جديد) 🔱
        m.add(InlineKeyboardButton("☁️ Google Cloud", callback_data="menu_cloud"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║         قائمة Runtime الفرعية           ║
    # ╚══════════════════════════════════════════╝
    def build_runtime_menu(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("📊 System Status", callback_data="hw_status"),
            InlineKeyboardButton("📈 Live Metrics", callback_data="rt_metrics")
        )
        m.row(
            InlineKeyboardButton("🔌 WebSocket", callback_data="rt_websocket"),
            InlineKeyboardButton("📡 Event Bus", callback_data="rt_eventbus")
        )
        m.row(
            InlineKeyboardButton("🔄 Restart Runtime", callback_data="rt_restart"),
            InlineKeyboardButton("🧹 Clear Cache", callback_data="rt_clear_cache")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║         قائمة Agents الفرعية            ║
    # ╚══════════════════════════════════════════╝
    def build_agents_menu(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("📋 Agent Roster", callback_data="list_agents"),
            InlineKeyboardButton("➕ Spawn Agent", callback_data="ag_spawn")
        )
        m.row(
            InlineKeyboardButton("🔍 Inspect Agent", callback_data="ag_inspect"),
            InlineKeyboardButton("📊 Agent Metrics", callback_data="ag_metrics")
        )
        m.row(
            InlineKeyboardButton("⏹️ Stop All", callback_data="ag_stop_all"),
            InlineKeyboardButton("🔄 Restart All", callback_data="ag_restart_all")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
        return m

    def build_agent_card(self, agent_id, agent_name, status) -> InlineKeyboardMarkup:
        """بطاقة تحكم لوكيل محدد"""
        m = InlineKeyboardMarkup(row_width=3)
        m.row(
            InlineKeyboardButton("▶️ Start", callback_data=f"agctl_start:{agent_id}"),
            InlineKeyboardButton("⏹️ Stop", callback_data=f"agctl_stop:{agent_id}"),
            InlineKeyboardButton("🔄 Restart", callback_data=f"agctl_restart:{agent_id}")
        )
        m.row(
            InlineKeyboardButton("📋 Logs", callback_data=f"agctl_logs:{agent_id}"),
            InlineKeyboardButton("🧠 Memory", callback_data=f"agctl_memory:{agent_id}"),
            InlineKeyboardButton("📊 Tasks", callback_data=f"agctl_tasks:{agent_id}")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Agents", callback_data="menu_agents"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║       قائمة Protocols الفرعية           ║
    # ╚══════════════════════════════════════════╝
    def build_protocols_menu(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("📜 Active Protocols", callback_data="pr_list"),
            InlineKeyboardButton("🆕 Create Protocol", callback_data="pr_create")
        )
        m.row(
            InlineKeyboardButton("🔬 Protocol Inspector", callback_data="pr_inspect"),
            InlineKeyboardButton("📊 Execution Graph", callback_data="pr_graph")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║        قائمة Deployments الفرعية        ║
    # ╚══════════════════════════════════════════╝
    def build_deploy_menu(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("🐙 Git Status", callback_data="dp_git_status"),
            InlineKeyboardButton("📦 Git Push", callback_data="dp_git_push")
        )
        m.row(
            InlineKeyboardButton("🌐 Deploy Pages", callback_data="dp_pages"),
            InlineKeyboardButton("☁️ Deploy Cloud Run", callback_data="dp_cloud")
        )
        m.row(
            InlineKeyboardButton("📋 Deploy History", callback_data="dp_history"),
            InlineKeyboardButton("🔄 Rollback", callback_data="dp_rollback")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║          قائمة AI Brain                 ║
    # ╚══════════════════════════════════════════╝
    def build_ai_menu(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("💬 Chat Mode", callback_data="ai_chat"),
            InlineKeyboardButton("🔍 Web Search", callback_data="ai_search")
        )
        m.row(
            InlineKeyboardButton("📄 Analyze File", callback_data="ai_analyze"),
            InlineKeyboardButton("🕸️ Web Scrape", callback_data="ai_scrape")
        )
        m.row(
            InlineKeyboardButton("📝 Generate Code", callback_data="ai_codegen"),
            InlineKeyboardButton("🧪 Run Experiment", callback_data="ai_experiment")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║         قائمة Security                  ║
    # ╚══════════════════════════════════════════╝
    def build_security_menu(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("🔒 Lockdown Mode", callback_data="sec_lockdown"),
            InlineKeyboardButton("🔓 Open Mode", callback_data="sec_open")
        )
        m.row(
            InlineKeyboardButton("🛡️ Security Audit", callback_data="sec_audit"),
            InlineKeyboardButton("📋 Access Logs", callback_data="sec_access_logs")
        )
        m.row(
            InlineKeyboardButton("🔑 Rotate Keys", callback_data="sec_rotate"),
            InlineKeyboardButton("🧬 Integrity Check", callback_data="sec_integrity")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║         قائمة Memory                    ║
    # ╚══════════════════════════════════════════╝
    def build_memory_menu(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("💾 DB Status", callback_data="mem_status"),
            InlineKeyboardButton("📊 Usage Stats", callback_data="mem_stats")
        )
        m.row(
            InlineKeyboardButton("🗑️ Clear Chat Memory", callback_data="mem_clear_chat"),
            InlineKeyboardButton("🗑️ Clear All Logs", callback_data="mem_clear_logs")
        )
        m.row(
            InlineKeyboardButton("☁️ Sync to Cloud", callback_data="mem_sync"),
            InlineKeyboardButton("📥 Export Data", callback_data="mem_export")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║          قائمة Docker                   ║
    # ╚══════════════════════════════════════════╝
    def build_docker_menu(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("📦 Containers", callback_data="dk_containers"),
            InlineKeyboardButton("🖼️ Images", callback_data="dk_images")
        )
        m.row(
            InlineKeyboardButton("🔄 Restart All", callback_data="dk_restart"),
            InlineKeyboardButton("🧹 Prune", callback_data="dk_prune")
        )
        m.row(
            InlineKeyboardButton("📋 Docker Logs", callback_data="dk_logs"),
            InlineKeyboardButton("📊 Stats", callback_data="dk_stats")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║          قائمة Settings                 ║
    # ╚══════════════════════════════════════════╝
    def build_settings_menu(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("🤖 AI Model", callback_data="set_model"),
            InlineKeyboardButton("🌐 WebApp URL", callback_data="set_webapp")
        )
        m.row(
            InlineKeyboardButton("🔔 Notifications", callback_data="set_notif"),
            InlineKeyboardButton("🎨 Theme", callback_data="set_theme")
        )
        m.row(
            InlineKeyboardButton("ℹ️ System Info", callback_data="set_sysinfo"),
            InlineKeyboardButton("🔄 Restart Bot", callback_data="set_restart_bot")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║          قائمة Google Cloud             ║
    # ╚══════════════════════════════════════════╝
    def build_cloud_menu(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("☁️ Cloud Storage", callback_data="cloud_storage"),
            InlineKeyboardButton("📊 BigQuery", callback_data="cloud_bq")
        )
        m.row(
            InlineKeyboardButton("🖥️ Compute VMs", callback_data="cloud_vms"),
            InlineKeyboardButton("📋 Cloud Logs", callback_data="cloud_logs")
        )
        m.row(
            InlineKeyboardButton("🧠 Vertex AI", callback_data="cloud_ai"),
            InlineKeyboardButton("🛡️ Cloud Shell", callback_data="cloud_shell")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
        return m

    # ╔══════════════════════════════════════════╗
    # ║      Quick Actions (إجراءات سريعة)      ║
    # ╚══════════════════════════════════════════╝
    def build_quick_actions(self) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=3)
        m.row(
            InlineKeyboardButton("🔄", callback_data="qa_restart"),
            InlineKeyboardButton("📊", callback_data="hw_status"),
            InlineKeyboardButton("🤖", callback_data="list_agents"),
            InlineKeyboardButton("📋", callback_data="audit_logs"),
            InlineKeyboardButton("🚀", callback_data="dp_git_push"),
            InlineKeyboardButton("🛡️", callback_data="sec_audit")
        )
        return m

    # ╔══════════════════════════════════════════╗
    # ║      Confirmation Dialog                ║
    # ╚══════════════════════════════════════════╝
    def build_confirm(self, action_id: str, label: str = "هل أنت متأكد؟") -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("✅ نعم، نفّذ", callback_data=f"confirm_yes:{action_id}"),
            InlineKeyboardButton("❌ إلغاء", callback_data="back_main")
        )
        return m

    def build_agent_approval_card(self, agent_name: str, task: str) -> InlineKeyboardMarkup:
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("✅ Approve", callback_data=f"agent_approve:{agent_name}"),
            InlineKeyboardButton("❌ Deny", callback_data=f"agent_deny:{agent_name}")
        )
        return m

    def build_model_selector_menu(self) -> InlineKeyboardMarkup:
        """قائمة تبديل نموذج الذكاء الاصطناعي"""
        m = InlineKeyboardMarkup(row_width=1)
        m.row(
            InlineKeyboardButton("⚡ Gemini 2.5 Flash (سريع واقتصادي)", callback_data="setmod_gemini-2.5-flash"),
            InlineKeyboardButton("🧠 Gemini 2.5 Pro (ذكي وقوي)", callback_data="setmod_gemini-2.5-pro")
        )
        m.row(
            InlineKeyboardButton("🧪 Gemini 2.0 Flash Exp (سريع تجريبي)", callback_data="setmod_gemini-2.0-flash-exp")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Settings", callback_data="menu_settings"))
        return m

    def build_theme_selector_menu(self) -> InlineKeyboardMarkup:
        """قائمة اختيار السمات المرئية للوحة التحكم"""
        m = InlineKeyboardMarkup(row_width=2)
        m.row(
            InlineKeyboardButton("🖤 Glassmorphism", callback_data="settheme_glassmorphism"),
            InlineKeyboardButton("💚 Emerald Matrix", callback_data="settheme_matrix")
        )
        m.row(
            InlineKeyboardButton("💙 Cosmic Sovereign", callback_data="settheme_cosmic"),
            InlineKeyboardButton("💜 Cyber Neon", callback_data="settheme_cyberpunk")
        )
        m.add(InlineKeyboardButton("⬅️ Back to Settings", callback_data="menu_settings"))
        return m


# Singleton
ui_builder = SovereignUIBuilder()

