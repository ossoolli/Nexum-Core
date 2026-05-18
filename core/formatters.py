"""
🔱 NEXUM CORE — منسق الرسائل المحسّن
تنسيق HTML جميل ومرتب لجميع رسائل البوت
"""

import html as html_module
from datetime import datetime


class NexumFormatter:
    """تنسيق الرسائل بشكل احترافي"""

    HEADER = "🔱"
    SEPARATOR = "━━━━━━━━━━━━━━━━━━"

    @staticmethod
    def header(title: str, subtitle: str = "") -> str:
        sub = f"\n<i>{html_module.escape(subtitle)}</i>" if subtitle else ""
        return (
            f"🔱 <b>{html_module.escape(title)}</b>{sub}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

    @staticmethod
    def section(icon: str, title: str, content: str) -> str:
        return f"\n{icon} <b>{html_module.escape(title)}</b>\n{content}"

    @staticmethod
    def code_block(text: str, max_len: int = 3000) -> str:
        safe = html_module.escape(str(text)[:max_len])
        return f"<pre>{safe}</pre>"

    @staticmethod
    def inline_code(text: str) -> str:
        return f"<code>{html_module.escape(str(text))}</code>"

    @staticmethod
    def progress_bar(percent: float, width: int = 10) -> str:
        filled = int(percent / 100 * width)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        if percent > 90:
            color = "🔴"
        elif percent > 70:
            color = "🟡"
        else:
            color = "🟢"
        return f"{color} {bar} {percent:.1f}%"

    @staticmethod
    def key_value(key: str, value: str) -> str:
        return f"  ├ <b>{key}:</b> {value}"

    @staticmethod
    def key_value_last(key: str, value: str) -> str:
        return f"  └ <b>{key}:</b> {value}"

    @staticmethod
    def timestamp() -> str:
        return f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    @staticmethod
    def success(text: str) -> str:
        return f"✅ <b>{html_module.escape(text)}</b>"

    @staticmethod
    def error(text: str) -> str:
        return f"❌ <b>{html_module.escape(text)}</b>"

    @staticmethod
    def warning(text: str) -> str:
        return f"⚠️ <b>{html_module.escape(text)}</b>"

    @staticmethod
    def info(text: str) -> str:
        return f"ℹ️ {html_module.escape(text)}"

    # ═══════════════════════════════════════════════
    # تقارير جاهزة
    # ═══════════════════════════════════════════════

    @classmethod
    def system_report(cls, cpu, ram, disk, net, uptime_str, hostname) -> str:
        lines = [
            cls.header("تقرير حالة السيرفر", hostname),
            cls.timestamp(),
            "",
            cls.section("🖥️", "المعالج (CPU)", cls.progress_bar(cpu)),
            cls.section("🧠", "الذاكرة (RAM)",
                f"{cls.progress_bar(ram['percent'])}\n"
                f"  └ {ram['used']}MB / {ram['total']}MB"),
            cls.section("💾", "القرص (Disk)",
                f"{cls.progress_bar(disk['percent'])}\n"
                f"  └ متبقي: {disk['free']}GB"),
            cls.section("🌐", "الشبكة",
                f"  ├ ⬆️ مرسل: {net['sent']}MB\n"
                f"  └ ⬇️ مستقبل: {net['recv']}MB"),
            cls.section("⏱️", "وقت التشغيل", f"  └ {uptime_str}"),
        ]

        # تنبيهات ذكية
        warnings = []
        if cpu > 80: warnings.append("⚠️ ضغط مرتفع على المعالج!")
        if ram['percent'] > 90: warnings.append("⚠️ الذاكرة ممتلئة!")
        if disk['percent'] > 95: warnings.append("⚠️ القرص ممتلئ!")

        if warnings:
            lines.append(cls.section("🚨", "تنبيهات", "\n".join(warnings)))
        else:
            lines.append("\n🟢 <b>جميع المؤشرات ضمن النطاق الآمن</b>")

        return "\n".join(lines)

    @classmethod
    def cpu_report(cls, cpu_percent, cpu_count, cpu_freq, per_cpu) -> str:
        lines = [
            cls.header("تقرير المعالج التفصيلي"),
            cls.timestamp(),
            "",
            cls.section("📊", "الاستخدام الكلي", cls.progress_bar(cpu_percent)),
            cls.key_value("الأنوية", str(cpu_count)),
        ]
        if cpu_freq:
            lines.append(cls.key_value("التردد", f"{cpu_freq:.0f} MHz"))

        if per_cpu:
            lines.append(cls.section("🔢", "لكل نواة", ""))
            for i, pct in enumerate(per_cpu):
                lines.append(f"  Core {i}: {cls.progress_bar(pct)}")

        return "\n".join(lines)

    @classmethod
    def ram_report(cls, mem) -> str:
        return "\n".join([
            cls.header("تقرير الذاكرة التفصيلي"),
            cls.timestamp(),
            "",
            cls.section("📊", "الاستخدام", cls.progress_bar(mem['percent'])),
            cls.key_value("الكلي", f"{mem['total']}MB"),
            cls.key_value("المستخدم", f"{mem['used']}MB"),
            cls.key_value("المتاح", f"{mem['available']}MB"),
            cls.key_value_last("الكاش", f"{mem.get('cached', 0)}MB"),
        ])

    @classmethod
    def disk_report(cls, disk) -> str:
        return "\n".join([
            cls.header("تقرير القرص التفصيلي"),
            cls.timestamp(),
            "",
            cls.section("📊", "الاستخدام", cls.progress_bar(disk['percent'])),
            cls.key_value("الكلي", f"{disk['total']}GB"),
            cls.key_value("المستخدم", f"{disk['used']}GB"),
            cls.key_value_last("المتبقي", f"{disk['free']}GB"),
        ])

    @classmethod
    def network_report(cls, net) -> str:
        return "\n".join([
            cls.header("تقرير الشبكة"),
            cls.timestamp(),
            "",
            cls.key_value("⬆️ مرسل", f"{net['sent']}MB"),
            cls.key_value("⬇️ مستقبل", f"{net['recv']}MB"),
            cls.key_value("📤 حزم مرسلة", str(net.get('packets_sent', 'N/A'))),
            cls.key_value_last("📥 حزم مستقبلة", str(net.get('packets_recv', 'N/A'))),
        ])

    @classmethod
    def deploy_report(cls, stage: str, output: str, status: str = "success") -> str:
        icon = "✅" if status == "success" else "❌"
        return "\n".join([
            cls.header("تقرير النشر"),
            cls.timestamp(),
            "",
            f"{icon} <b>{html_module.escape(stage)}</b>",
            cls.code_block(output, 2000),
        ])

    @classmethod
    def docker_container_card(cls, name, status, ports, image) -> str:
        status_icon = "🟢" if "Up" in status else "🔴" if "Exited" in status else "🟡"
        return (
            f"{status_icon} <b>{html_module.escape(name)}</b>\n"
            f"  ├ الحالة: <code>{html_module.escape(status)}</code>\n"
            f"  ├ الصورة: <code>{html_module.escape(image)}</code>\n"
            f"  └ المنافذ: <code>{html_module.escape(ports or 'لا يوجد')}</code>"
        )

    @classmethod
    def welcome_message(cls) -> str:
        return "\n".join([
            "🔱 <b>NEXUM CORE OS v2.0</b>",
            "<i>نظام التشغيل السيادي — التحكم الكامل</i>",
            "━━━━━━━━━━━━━━━━━━",
            "",
            "🎛️ استخدم الأزرار أدناه للتحكم الكامل",
            "💬 أو اكتب أي أمر/سؤال مباشرة",
            "",
            "📌 <b>أوامر سريعة:</b>",
            "  /run <code>أمر</code> — تنفيذ مباشر",
            "  /planx <code>هدف</code> — تخطيط ذكي",
            "  /docker — إدارة الحاويات",
            "  /status — نبض السيرفر",
        ])


fmt = NexumFormatter()
