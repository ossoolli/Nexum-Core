"""
core/stream_reporter.py
يبث خطوات التنفيذ لحظة بلحظة عبر Telegram
"""
import time
from typing import Optional

class StreamReporter:
    """
    نمط التقرير:
    ─ يُرسل رسالة أولى: "جاري التنفيذ..."
    ─ يُعدّلها مع كل خطوة (edit_message)
    ─ يُنهيها برسالة نهائية واضحة
    """

    def __init__(self):
        self._bot = None
        self._chat_id = None
        self._message_id = None
        self._steps = []
        self._start_time = None

    def init(self, bot, chat_id: int):
        self._bot = bot
        self._chat_id = chat_id
        self._steps = []
        self._start_time = time.time()

    def start(self, title: str) -> Optional[int]:
        """يُرسل رسالة بداية ويعيد message_id للتعديل عليها"""
        if not self._bot:
            return None
        text = f"⚙️ <b>{title}</b>\n<code>جاري البدء...</code>"
        try:
            msg = self._bot.send_message(self._chat_id, text, parse_mode="HTML")
            self._message_id = msg.message_id
            return msg.message_id
        except Exception:
            return None

    def step(self, icon: str, text: str, status: str = "running"):
        """يضيف خطوة ويُعدّل الرسالة الحالية"""
        icons = {"running": "⚙️", "done": "✅", "error": "❌", "warn": "⚠️", "info": "ℹ️"}
        symbol = icons.get(status, icon)
        self._steps.append(f"{symbol} {text}")

        if self._bot and self._message_id:
            body = "\n".join(self._steps[-8:])  # آخر 8 خطوات
            elapsed = round(time.time() - self._start_time, 1)
            full_text = f"{body}\n\n<i>⏱ {elapsed}s</i>"
            try:
                self._bot.edit_message_text(
                    full_text,
                    self._chat_id,
                    self._message_id,
                    parse_mode="HTML"
                )
            except Exception:
                pass

    def finish(self, summary: str, success: bool = True, details: Optional[str] = None):
        """يُنهي التقرير برسالة نهائية كاملة"""
        elapsed = round(time.time() - self._start_time, 1)
        icon = "✅" if success else "❌"
        all_steps = "\n".join(self._steps)
        text = (
            f"{icon} <b>{'اكتمل' if success else 'فشل'}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"{all_steps}\n"
            f"━━━━━━━━━━━━━━\n"
            f"📋 <b>الملخص:</b> {summary}\n"
        )
        if details:
            text += f"\n<pre>{details[:800]}</pre>"
        text += f"\n<i>⏱ الوقت الكلي: {elapsed}s</i>"

        if self._bot:
            try:
                if self._message_id:
                    self._bot.edit_message_text(
                        text, self._chat_id, self._message_id, parse_mode="HTML"
                    )
                else:
                    self._bot.send_message(self._chat_id, text, parse_mode="HTML")
            except Exception as e:
                self._bot.send_message(self._chat_id, text, parse_mode="HTML")

    def code_output(self, output: str):
        """يُرسل خرج كود كرسالة منفصلة"""
        if self._bot and output.strip():
            self._bot.send_message(
                self._chat_id,
                f"<pre>{output[:3000]}</pre>",
                parse_mode="HTML"
            )


stream_reporter = StreamReporter()
