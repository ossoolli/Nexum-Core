"""
NEXUM Safe Sender — Telegram Message Safety Layer
===================================================
يضمن أن جميع الرسائل المرسلة للتليجرام آمنة ولن تسبب أخطاء.
يدعم: تقسيم الرسائل الطويلة، تنظيف HTML، الإرسال عبر message أو chat_id.
"""
import html
import re

MAX_LEN = 4000

ALLOWED_TAGS = ["b", "i", "u", "s", "code", "pre", "a"]


def sanitize_html(text: str) -> str:
    """إزالة وسوم HTML غير المدعومة في تليجرام"""
    def repl(match):
        tag = match.group(1)
        if tag in ALLOWED_TAGS:
            return match.group(0)
        return html.escape(match.group(0))
    return re.sub(r"</?([a-zA-Z0-9]+).*?>", repl, text)


def split_message(text: str):
    """تقسيم الرسائل الطويلة"""
    return [text[i:i + MAX_LEN] for i in range(0, len(text), MAX_LEN)]


def safe_reply(bot, message_or_chat_id, text, markup=None, is_chat_id=False):
    """
    إرسال رد آمن — يدعم كلا النمطين:
    - safe_reply(bot, message, text)        → reply_to
    - safe_reply(bot, chat_id, text, is_chat_id=True) → send_message
    """
    try:
        clean = sanitize_html(str(text))
        chunks = split_message(clean)
        
        for chunk in chunks:
            if is_chat_id or isinstance(message_or_chat_id, (int, str)):
                chat_id = int(message_or_chat_id) if not isinstance(message_or_chat_id, int) else message_or_chat_id
                # Check if it's actually a chat_id (number) or a message object
                if hasattr(message_or_chat_id, 'chat'):
                    bot.reply_to(message_or_chat_id, chunk, parse_mode="HTML", reply_markup=markup)
                else:
                    bot.send_message(message_or_chat_id, chunk, parse_mode="HTML", reply_markup=markup)
            else:
                bot.reply_to(message_or_chat_id, chunk, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        error_msg = f"⚠️ Error\n<code>{html.escape(str(e))}</code>"
        try:
            if is_chat_id or isinstance(message_or_chat_id, int):
                bot.send_message(message_or_chat_id, error_msg, parse_mode="HTML")
            else:
                bot.reply_to(message_or_chat_id, error_msg, parse_mode="HTML")
        except:
            pass


def send_terminal_output(bot, chat_id, status, output, markup=None):
    """
    إرسال مخرجات التيرمينال بأمان.
    يدعم: send_terminal_output(bot, chat_id, status, output)
    """
    status_emoji = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
    safe_output = html.escape(str(output))[:3500]
    text = f"{status_emoji} <b>Terminal Output:</b>\n<pre>{safe_output}</pre>"
    
    try:
        chunks = split_message(text)
        for chunk in chunks:
            if hasattr(chat_id, 'chat'):
                bot.reply_to(chat_id, chunk, parse_mode="HTML", reply_markup=markup)
            else:
                bot.send_message(chat_id, chunk, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        try:
            cid = chat_id if isinstance(chat_id, int) else chat_id.chat.id
            bot.send_message(cid, f"⚠️ <code>{html.escape(str(e))}</code>", parse_mode="HTML")
        except:
            pass