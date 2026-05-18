import html
import re

MAX_LEN = 4000

ALLOWED_TAGS = [
    "b",
    "i",
    "u",
    "s",
    "code",
    "pre",
    "a"
]

def sanitize_html(text: str) -> str:
    """
    Remove unsupported Telegram HTML tags.
    """

    def repl(match):
        tag = match.group(1)

        if tag in ALLOWED_TAGS:
            return match.group(0)

        return html.escape(match.group(0))

    text = re.sub(
        r"</?([a-zA-Z0-9]+).*?>",
        repl,
        text
    )

    return text


def split_message(text: str):
    """
    Split long messages into Telegram-safe chunks.
    """
    return [
        text[i:i + MAX_LEN]
        for i in range(0, len(text), MAX_LEN)
    ]


def safe_reply(bot, message, text, markup=None):
    """
    Safe Telegram sender:
    - sanitizes HTML
    - splits long messages
    - prevents Telegram crashes
    """

    try:
        clean = sanitize_html(str(text))

        chunks = split_message(clean)

        for chunk in chunks:
            bot.reply_to(
                message,
                chunk,
                parse_mode="HTML",
                reply_markup=markup
            )

    except Exception as e:

        fallback = html.escape(str(e))

        bot.reply_to(
            message,
            f"⚠️ Telegram Send Error\n<code>{fallback}</code>",
            parse_mode="HTML"
        )
        