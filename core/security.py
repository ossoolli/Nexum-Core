import re
import shlex

# الأوامر التي تحتاج تأكيد قبل التنفيذ
DANGEROUS_PATTERNS = [
    "rm -rf", "mkfs", "dd if=", "chmod 777",
    "reboot", "shutdown", ":(){ :|:& };:"
]

# الأوامر المحظورة تماماً بغض النظر عن أي شيء
ABSOLUTE_BLOCKS = [
    "cat .env", "cat.*passwd", "history",
]

class SecurityValidator:
    def __init__(self):
        self.blocked = re.compile(
            r'(' + '|'.join(re.escape(p) for p in ABSOLUTE_BLOCKS) + r')',
            re.IGNORECASE
        )

    def is_safe(self, cmd: str) -> tuple[bool, str]:
        """
        Returns: (allowed, reason)
        reason: 'free' | 'confirm' | 'blocked'
        """
        if not cmd or len(cmd) > 500:
            return False, "blocked"

        # محظور مطلقاً
        if self.blocked.search(cmd):
            return False, "blocked"

        # يحتاج تأكيد
        for danger in DANGEROUS_PATTERNS:
            if danger in cmd:
                return True, "confirm"

        return True, "free"

validator = SecurityValidator()

# ===== إضافة validate_command للتوافق مع planner.py =====
class SecurityValidator:
    def validate_command(self, cmd):
        allowed, reason = validator.is_safe(cmd)
        if not allowed:
            return False, "🚫 أمر محظور أمنياً."
        if reason == 'confirm':
            return True, "⚠️ أمر حساس - يحتاج تأكيداً."
        return True, "✅ آمن."

security = SecurityValidator()

# ===== إضافة validate_command للتوافق مع planner.py =====
class SecurityValidator:
    def validate_command(self, cmd):
        allowed, reason = validator.is_safe(cmd)
        if not allowed:
            return False, "🚫 أمر محظور أمنياً."
        if reason == 'confirm':
            return True, "⚠️ أمر حساس - يحتاج تأكيداً."
        return True, "✅ آمن."

security = SecurityValidator()
