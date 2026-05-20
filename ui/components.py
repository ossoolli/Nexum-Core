from telebot import types

STATUS_ICONS = {
    "RUNNING": "🟢", 
    "WARNING": "🟡", 
    "ERROR": "🔴", 
    "IDLE": "⚪",
    "PROCESSING": "🔵",
    "AI": "🟣"
}

def breadcrumbs(*paths) -> str:
    """ يولد مسار مرئي، مثال: 🏠 الرئيسية › 🤖 الوكلاء """
    return " › ".join(paths) + "\n\n"

def progress_bar(percent: int, length: int = 10) -> str:
    """ يولد شريط تحميل مرئي (مثال: ██████░░░░) """
    if percent < 0: percent = 0
    if percent > 100: percent = 100
    filled = int((percent / 100) * length)
    return "█" * filled + "░" * (length - filled)

def create_btn(text: str, cb_data: str) -> types.InlineKeyboardButton:
    """ إنشاء زر مختصرة """
    return types.InlineKeyboardButton(text, callback_data=cb_data)

def format_card(title: str, details: dict, status: str = None) -> str:
    """ يولد بطاقة عرض معلومات موحدة """
    lines = []
    icon = STATUS_ICONS.get(status, "") if status else ""
    lines.append(f"{icon} *{title}*")
    lines.append("─────────────────")
    
    for k, v in details.items():
        lines.append(f"{k}: `{v}`")
        
    return "\n".join(lines)
