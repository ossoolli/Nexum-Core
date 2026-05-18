import html as html_module
import telebot

def send_terminal_output(bot, chat_id, status: str, output: str, step_info: str = ""):
    """
    دالة آمنة لإرسال مخرجات التيرمينال بدون كسر HTML
    تتعامل مع أي رموز خاصة تلقائياً
    """
    icon = "✅" if status == 'success' else "❌" if status in ('failed','error') else "⏳"
    
    # تنظيف المخرجات من أي رمز يكسر HTML
    clean_output = html_module.escape(str(output))
    
    # تقطيع الرسائل الطويلة
    max_len = 3000
    chunks = [clean_output[i:i+max_len] for i in range(0, len(clean_output), max_len)]
    
    for i, chunk in enumerate(chunks):
        prefix = f"{icon} <b>{step_info}</b>\n" if (i == 0 and step_info) else ""
        try:
            bot.send_message(
                chat_id,
                f"{prefix}<pre>{chunk}</pre>",
                parse_mode="HTML"
            )
        except Exception as e:
            # fallback: إرسال نص عادي بدون تنسيق
            bot.send_message(
                chat_id,
                f"{icon} {step_info}\n{str(output)[:3000]}".replace('<','').replace('>','')
            )

def safe_reply(bot, message, text: str, markup=None):
    """إرسال رسالة نصية آمنة مع HTML"""
    try:
        bot.reply_to(
            message,
            text,
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception:
        # fallback بدون تنسيق
        clean = re.sub(r'<[^>]+>', '', text)
        bot.reply_to(message, clean, reply_markup=markup)
