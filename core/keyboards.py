"""
🔱 NEXUM CORE — نظام لوحات المفاتيح الشامل
جميع الأزرار التفاعلية (Inline Keyboards) لكل أقسام البوت
"""

from telebot import types


# ═══════════════════════════════════════════════════
# 🏠 القائمة الرئيسية
# ═══════════════════════════════════════════════════
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 المراقبة", callback_data="menu_monitor"),
        types.InlineKeyboardButton("🚀 النشر والكود", callback_data="menu_deploy"),
    )
    markup.add(
        types.InlineKeyboardButton("🐳 Docker", callback_data="menu_docker"),
        types.InlineKeyboardButton("🤖 الذكاء", callback_data="menu_ai"),
    )
    markup.add(
        types.InlineKeyboardButton("⚙️ الإعدادات", callback_data="menu_settings"),
        types.InlineKeyboardButton("💰 المالية", callback_data="menu_finance"),
    )
    markup.add(
        types.InlineKeyboardButton("🌐 لوحة التحكم", callback_data="open_webapp"),
    )
    return markup


# ═══════════════════════════════════════════════════
# 📊 قائمة المراقبة
# ═══════════════════════════════════════════════════
def monitor_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📈 تقرير شامل", callback_data="mon_full"),
        types.InlineKeyboardButton("🖥️ CPU", callback_data="mon_cpu"),
    )
    markup.add(
        types.InlineKeyboardButton("🧠 RAM", callback_data="mon_ram"),
        types.InlineKeyboardButton("💾 القرص", callback_data="mon_disk"),
    )
    markup.add(
        types.InlineKeyboardButton("🌐 الشبكة", callback_data="mon_network"),
        types.InlineKeyboardButton("📋 العمليات", callback_data="mon_processes"),
    )
    markup.add(
        types.InlineKeyboardButton("⏱️ Uptime", callback_data="mon_uptime"),
        types.InlineKeyboardButton("🌡️ الحرارة", callback_data="mon_temp"),
    )
    markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main"))
    return markup


# ═══════════════════════════════════════════════════
# 🚀 قائمة النشر والكود
# ═══════════════════════════════════════════════════
def deploy_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📝 Git Status", callback_data="dep_status"),
        types.InlineKeyboardButton("⬇️ Git Pull", callback_data="dep_pull"),
    )
    markup.add(
        types.InlineKeyboardButton("⬆️ Git Push", callback_data="dep_push"),
        types.InlineKeyboardButton("🚀 نشر كامل", callback_data="dep_full"),
    )
    markup.add(
        types.InlineKeyboardButton("📜 آخر Commits", callback_data="dep_log"),
        types.InlineKeyboardButton("🔄 Git Diff", callback_data="dep_diff"),
    )
    markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main"))
    return markup


# ═══════════════════════════════════════════════════
# 🐳 قائمة Docker
# ═══════════════════════════════════════════════════
def docker_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📦 الحاويات", callback_data="dock_ps"),
        types.InlineKeyboardButton("🖼️ الصور", callback_data="dock_images"),
    )
    markup.add(
        types.InlineKeyboardButton("📋 Logs", callback_data="dock_logs"),
        types.InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="dock_restart"),
    )
    markup.add(
        types.InlineKeyboardButton("⏹️ إيقاف حاوية", callback_data="dock_stop"),
        types.InlineKeyboardButton("▶️ تشغيل حاوية", callback_data="dock_start"),
    )
    markup.add(
        types.InlineKeyboardButton("🧹 تنظيف", callback_data="dock_prune"),
        types.InlineKeyboardButton("📊 استهلاك", callback_data="dock_stats"),
    )
    markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main"))
    return markup


# ═══════════════════════════════════════════════════
# 🤖 قائمة الذكاء الاصطناعي
# ═══════════════════════════════════════════════════
def ai_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💬 محادثة Gemini", callback_data="ai_gemini"),
        types.InlineKeyboardButton("🧠 GPT-4o Expert", callback_data="ai_gpt"),
    )
    markup.add(
        types.InlineKeyboardButton("🔍 مراجعة كود", callback_data="ai_review"),
        types.InlineKeyboardButton("📝 توليد كود", callback_data="ai_generate"),
    )
    markup.add(
        types.InlineKeyboardButton("🐛 تحليل أخطاء", callback_data="ai_debug"),
        types.InlineKeyboardButton("📖 شرح كود", callback_data="ai_explain"),
    )
    markup.add(
        types.InlineKeyboardButton("🧹 مسح السياق", callback_data="ai_clear"),
    )
    markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main"))
    return markup


# ═══════════════════════════════════════════════════
# ⚙️ قائمة الإعدادات
# ═══════════════════════════════════════════════════
def settings_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🧠 الذاكرة", callback_data="set_memory"),
        types.InlineKeyboardButton("📋 السجلات", callback_data="set_logs"),
    )
    markup.add(
        types.InlineKeyboardButton("🔄 إعادة تشغيل البوت", callback_data="set_restart"),
        types.InlineKeyboardButton("🔑 فحص المفاتيح", callback_data="set_keys"),
    )
    markup.add(
        types.InlineKeyboardButton("💾 نسخة احتياطية", callback_data="set_backup"),
        types.InlineKeyboardButton("🗑️ مسح الكاش", callback_data="set_clear_cache"),
    )
    markup.add(
        types.InlineKeyboardButton("ℹ️ معلومات النظام", callback_data="set_info"),
    )
    markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main"))
    return markup


# ═══════════════════════════════════════════════════
# 💰 قائمة المالية
# ═══════════════════════════════════════════════════
def finance_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("⭐ ترقية بالنجوم", callback_data="fin_upgrade"),
        types.InlineKeyboardButton("📊 حالة الاشتراك", callback_data="fin_status"),
    )
    markup.add(
        types.InlineKeyboardButton("📜 سجل المعاملات", callback_data="fin_history"),
        types.InlineKeyboardButton("🎁 كوبون تخفيض", callback_data="fin_coupon"),
    )
    markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main"))
    return markup


# ═══════════════════════════════════════════════════
# 🔧 أزرار مساعدة
# ═══════════════════════════════════════════════════
def confirm_action(action_data):
    """أزرار تأكيد/إلغاء عامة"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تأكيد", callback_data=f"confirm_{action_data}"),
        types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_action"),
    )
    return markup


def back_button(target="back_main"):
    """زر الرجوع العام"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data=target))
    return markup


def container_action_buttons(container_name):
    """أزرار أفعال لحاوية معينة"""
    markup = types.InlineKeyboardMarkup(row_width=3)
    safe_name = container_name[:30]
    markup.add(
        types.InlineKeyboardButton("📋 Logs", callback_data=f"ctn_logs_{safe_name}"),
        types.InlineKeyboardButton("🔄 Restart", callback_data=f"ctn_restart_{safe_name}"),
        types.InlineKeyboardButton("⏹️ Stop", callback_data=f"ctn_stop_{safe_name}"),
    )
    markup.add(types.InlineKeyboardButton("🔙 Docker", callback_data="menu_docker"))
    return markup


def webapp_button(url):
    """زر Mini App"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🌐 فتح لوحة التحكم", web_app=types.WebAppInfo(url=url))
    )
    return markup


# ═══════════════════════════════════════════════════
# 📌 مسار القوائم (لإدارة التنقل)
# ═══════════════════════════════════════════════════
MENU_MAP = {
    "menu_monitor": ("📊 قسم المراقبة والنبض", monitor_menu),
    "menu_deploy": ("🚀 قسم النشر وإدارة الكود", deploy_menu),
    "menu_docker": ("🐳 قسم إدارة Docker", docker_menu),
    "menu_ai": ("🤖 قسم الذكاء الاصطناعي", ai_menu),
    "menu_settings": ("⚙️ قسم الإعدادات والنظام", settings_menu),
    "menu_finance": ("💰 قسم المالية والاشتراكات", finance_menu),
}
