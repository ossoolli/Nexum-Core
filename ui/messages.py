class UIMessage:
    @staticmethod
    def success(title: str, body: str = "", time_taken: float = None) -> str:
        text = f"✅ *{title}*"
        if body:
            text += f"\n\n{body}"
        if time_taken is not None:
            text += f"\n\n⏱ الوقت: `{time_taken:.1f}s`"
        return text

    @staticmethod
    def error(title: str, error: str, hint: str = None) -> str:
        text = f"❌ *{title}*\n\nالخطأ:\n`{error}`"
        if hint:
            text += f"\n\n💡 *الحل:* {hint}"
        return text

    @staticmethod
    def loading(title: str, step: str = None) -> str:
        text = f"🔄 *{title}*"
        if step:
            text += f"\n\nالمرحلة الحالية: `{step}`"
        else:
            text += f"\n\nيرجى الانتظار..."
        return text

    @staticmethod
    def info(title: str, body: str) -> str:
        return f"ℹ️ *{title}*\n\n{body}"

    @staticmethod
    def warning(title: str, body: str) -> str:
        return f"⚠️ *{title}*\n\n{body}"
