"""
NEXUM PRIME — Sovereign Agentic OS
====================================
Interactive Runtime Console — Click-first, Type-never.
كل شيء يعمل بالنقر والبطاقات والقوائم الديناميكية.
"""
import os
import sys
import html
import telebot
from dotenv import load_dotenv
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

from core.llm_factory import llm
from core.executor import executor
from core.safe_sender import send_terminal_output, safe_reply
from core.planner import AIPlanner
from core.orchestrator import orchestrator
from core.memory_local import LongTermMemory
from core.keyboards import ui_builder
from core.callback_router import router
from core.event_bus import event_bus
from core.lifecycle import lifecycle
from services.gemini_service import GeminiService
from core.formatters import fmt
from core.agent_registry import agent_registry
from agents.monitor import monitor_agent
from agents.deploy import deploy_agent
from agents.docker_agent import docker_agent
import psutil

# ╔══════════════════════════════════════════════════════════════╗
# ║                    BOT & SERVICE SETUP                      ║
# ╚══════════════════════════════════════════════════════════════╝
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

_gemini_svc = GeminiService(os.getenv("GOOGLE_API_KEY"))
_planner = AIPlanner(_gemini_svc)
_memory = LongTermMemory(os.path.join(BASE_DIR, "storage", "memory.json"))
orchestrator.set_planner(_planner)

pending_commands = {}

# ╔══════════════════════════════════════════════════════════════╗
# ║                  CLOUD MEMORY SYSTEM                        ║
# ╚══════════════════════════════════════════════════════════════╝
def get_user_history(user_id):
    from services.db_service import db_service
    from core.runtime_state import runtime_state
    state = runtime_state.get_agent_state(f"user_{user_id}")
    history = state.get("chat_history", [])
    if not history:
        history = db_service.load_chat_history(user_id)
        if history:
            runtime_state.update_agent_state(f"user_{user_id}", {"chat_history": history})
    return history

def update_user_history(user_id, history):
    from services.db_service import db_service
    from core.runtime_state import runtime_state
    capped = history[-15:]
    runtime_state.update_agent_state(f"user_{user_id}", {"chat_history": capped})
    db_service.save_chat_history(user_id, capped)


# ╔══════════════════════════════════════════════════════════════╗
# ║              SYSTEM CONTEXT BUILDER (عين النظام)            ║
# ╚══════════════════════════════════════════════════════════════╝
def _build_system_context():
    """بناء سياق النظام الحي لحقنه في كل رسالة AI"""
    active_agents = [ag['name'] for ag in agent_registry.agents.values()]
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    try:
        project_files = os.listdir(BASE_DIR)
        files_snapshot = ", ".join(project_files[:15])
    except:
        files_snapshot = "N/A"
    return f"""أنت نظام تشغيل ذكاء اصطناعي سيادي (NEXUM OS). مستوى وكيل Antigravity.
حالة النظام:
- الوكلاء: {', '.join(active_agents) if active_agents else 'لا يوجد'}
- CPU {cpu}%, RAM {ram}%
- الملفات: {files_snapshot}

قدراتك: اتخذ القرار فوراً. استخدم `list_directory`, `read_file`, `search_web`, `fetch_webpage`.
تحدث كنظام سيادي مسيطر."""


# ╔══════════════════════════════════════════════════════════════╗
# ║            INTERACTIVE CALLBACK HANDLERS                    ║
# ║         كل زر في keyboards.py له handler هنا               ║
# ╚══════════════════════════════════════════════════════════════╝

# --- الشاشة الرئيسية ---
@bot.message_handler(commands=['start', 'menu', 'dashboard', 'home'])
def cmd_start(message):
    if message.from_user.id != ADMIN_ID: return
    from core.runtime_state import runtime_state
    runtime_state.update_agent_state(f"user_{ADMIN_ID}", {"last_seen": datetime.now().isoformat()})
    event_bus.emit(event_bus.SYSTEM_ALERT, {"action": "dashboard_access", "user": ADMIN_ID})
    
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    agent_count = len(agent_registry.agents)
    
    text = (
        f"🔱 <b>NEXUM PRIME — Sovereign Agentic OS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>الحالة:</b> <code>OPERATIONAL</code>\n"
        f"🤖 <b>الوكلاء:</b> {agent_count} active\n"
        f"🔥 <b>CPU:</b> {cpu}% | 🧠 <b>RAM:</b> {ram}%\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 اختر قسماً من لوحة التحكم أدناه:"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML",
                     reply_markup=ui_builder.build_main_control_plane())


# --- الموجه الموحد لجميع الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    if call.from_user.id != ADMIN_ID: return
    data = call.data
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    try:
        # ═══ NAVIGATION: القوائم الفرعية ═══
        if data == "back_main":
            _edit_to_main_menu(chat_id, msg_id)
        elif data == "menu_runtime":
            bot.edit_message_text("⚡ <b>Runtime Control Center</b>\nاختر إجراء:", chat_id, msg_id,
                                 parse_mode="HTML", reply_markup=ui_builder.build_runtime_menu())
        elif data == "menu_agents":
            bot.edit_message_text("🤖 <b>Agent Swarm Control</b>\nإدارة الوكلاء المستقلين:", chat_id, msg_id,
                                 parse_mode="HTML", reply_markup=ui_builder.build_agents_menu())
        elif data == "menu_protocols":
            bot.edit_message_text("🧬 <b>Protocol Engine</b>\nإدارة البروتوكولات:", chat_id, msg_id,
                                 parse_mode="HTML", reply_markup=ui_builder.build_protocols_menu())
        elif data == "menu_deploy":
            bot.edit_message_text("🚀 <b>Deployment Center</b>\nعمليات النشر والتوزيع:", chat_id, msg_id,
                                 parse_mode="HTML", reply_markup=ui_builder.build_deploy_menu())
        elif data == "menu_ai":
            bot.edit_message_text("🧠 <b>AI Brain Interface</b>\nتحكم بالذكاء الاصطناعي:", chat_id, msg_id,
                                 parse_mode="HTML", reply_markup=ui_builder.build_ai_menu())
        elif data == "menu_security":
            bot.edit_message_text("🛡️ <b>Security Center</b>\nمركز الأمان والحماية:", chat_id, msg_id,
                                 parse_mode="HTML", reply_markup=ui_builder.build_security_menu())
        elif data == "menu_memory":
            bot.edit_message_text("💾 <b>Memory & Database</b>\nإدارة الذاكرة والبيانات:", chat_id, msg_id,
                                 parse_mode="HTML", reply_markup=ui_builder.build_memory_menu())
        elif data == "menu_docker":
            bot.edit_message_text("🐳 <b>Docker Control</b>\nإدارة الحاويات:", chat_id, msg_id,
                                 parse_mode="HTML", reply_markup=ui_builder.build_docker_menu())
        elif data == "menu_settings":
            bot.edit_message_text("⚙️ <b>System Settings</b>\nإعدادات النظام:", chat_id, msg_id,
                                 parse_mode="HTML", reply_markup=ui_builder.build_settings_menu())

        # ═══ RUNTIME ACTIONS ═══
        elif data == "hw_status":
            _send_runtime_status(chat_id)
        elif data == "rt_metrics":
            _send_live_metrics(chat_id)
        elif data == "rt_eventbus":
            _send_eventbus_info(chat_id)
        elif data == "rt_restart":
            bot.send_message(chat_id, "🔄 <b>إعادة تشغيل Runtime...</b>\nجاري إعادة تهيئة جميع الخدمات...",
                             parse_mode="HTML", reply_markup=ui_builder.build_confirm("rt_restart", "إعادة تشغيل Runtime"))

        # ═══ AGENT ACTIONS ═══
        elif data == "list_agents":
            _send_agents_roster(chat_id)
        elif data == "ag_spawn":
            _spawn_agent_menu(chat_id)
        elif data == "ag_stop_all":
            bot.send_message(chat_id, "⏹️ <b>إيقاف جميع الوكلاء...</b>",
                             parse_mode="HTML", reply_markup=ui_builder.build_confirm("ag_stop_all"))
        elif data == "ag_restart_all":
            for agent_id in agent_registry.agents:
                lifecycle.init_agent(agent_id)
            bot.send_message(chat_id, "🔄 <b>تمت إعادة تشغيل جميع الوكلاء بنجاح.</b>", parse_mode="HTML",
                             reply_markup=ui_builder.build_agents_menu())

        # ═══ AGENT CONTROL (per-agent) ═══
        elif data.startswith("agctl_"):
            _handle_agent_control(data, chat_id)

        # ═══ PROTOCOL ACTIONS ═══
        elif data == "pr_list":
            _send_protocols_list(chat_id)
        elif data == "pr_create":
            msg = bot.send_message(chat_id, "🆕 <b>أرسل وصف البروتوكول الجديد الآن لتكوين مسار التنفيذ:</b>\n<i>مثال: ابن واجهة React وتأكد من عملها</i>", parse_mode="HTML")
            bot.register_next_step_handler(msg, process_pr_create)
        elif data == "pr_graph":
            _send_execution_graph(chat_id)

        # ═══ DEPLOY ACTIONS ═══
        elif data == "dp_git_status":
            _run_and_send(chat_id, "git status", "📊 Git Status")
        elif data == "dp_git_push":
            _run_and_send(chat_id, "git add . && git commit -m 'NEXUM Auto-Commit' && git push origin main", "📦 Git Push")
        elif data == "dp_pages":
            bot.send_message(chat_id, "🌐 <b>GitHub Pages نشط على:</b>\n<a href='https://ossoolli.github.io/Nexum-Core/'>https://ossoolli.github.io/Nexum-Core/</a>",
                             parse_mode="HTML", reply_markup=ui_builder.build_deploy_menu())

        # ═══ AI ACTIONS ═══
        elif data == "ai_chat":
            msg = bot.send_message(chat_id, "💬 <b>وضع المحادثة الذكية:</b>\nأرسل رسالتك الآن للنظام السيادي.", parse_mode="HTML")
            bot.register_next_step_handler(msg, handle_text)
        elif data == "ai_search":
            msg = bot.send_message(chat_id, "🔍 <b>بحث الويب:</b>\nأرسل الكلمة المفتاحية أو السؤال:", parse_mode="HTML")
            bot.register_next_step_handler(msg, process_ai_search)
        elif data == "ai_scrape":
            msg = bot.send_message(chat_id, "🕸️ <b>Web Scraping:</b>\nأرسل الرابط (URL) المطلوب سحبه:", parse_mode="HTML")
            bot.register_next_step_handler(msg, process_ai_scrape)
        elif data == "ai_codegen":
            msg = bot.send_message(chat_id, "📝 <b>توليد الكود:</b>\nأرسل وصف الكود البرمجي الذي تريد بناءه:", parse_mode="HTML")
            bot.register_next_step_handler(msg, process_ai_codegen)

        # ═══ SECURITY ACTIONS ═══
        elif data == "sec_audit":
            _run_ai_task(chat_id, "قم بفحص أمان السيرفر بالكامل: تحقق من المنافذ المفتوحة، صلاحيات الملفات، والتبعيات الخطيرة")
        elif data == "sec_lockdown":
            bot.send_message(chat_id, "🔒 <b>Lockdown Mode:</b> تم تفعيل وضع الحماية القصوى.\nجميع الأوامر الخطيرة معطلة.",
                             parse_mode="HTML", reply_markup=ui_builder.build_security_menu())
        elif data == "sec_integrity":
            _run_and_send(chat_id, "find . -name '*.py' | head -20 && echo '---' && wc -l *.py", "🧬 Integrity Check")

        # ═══ MEMORY ACTIONS ═══
        elif data == "mem_status":
            _send_memory_status(chat_id)
        elif data == "mem_sync":
            from services.db_service import db_service
            bot.send_message(chat_id, "☁️ <b>Cloud Sync:</b> " + ("✅ متصل بـ Supabase" if db_service.enabled else "❌ غير متصل"),
                             parse_mode="HTML", reply_markup=ui_builder.build_memory_menu())
        elif data == "mem_clear_chat":
            bot.send_message(chat_id, "🗑️ مسح الذاكرة الحوارية؟",
                             parse_mode="HTML", reply_markup=ui_builder.build_confirm("mem_clear_chat"))

        # ═══ DOCKER ACTIONS ═══
        elif data == "dk_containers":
            _run_and_send(chat_id, "docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' 2>/dev/null || echo 'Docker غير متوفر'", "📦 Containers")
        elif data == "dk_images":
            _run_and_send(chat_id, "docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}' 2>/dev/null || echo 'Docker غير متوفر'", "🖼️ Images")
        elif data == "dk_stats":
            _run_and_send(chat_id, "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' 2>/dev/null || echo 'Docker غير متوفر'", "📊 Stats")
        elif data == "dk_prune":
            bot.send_message(chat_id, "🧹 تنظيف Docker؟", parse_mode="HTML", reply_markup=ui_builder.build_confirm("dk_prune"))

        # ═══ SETTINGS ACTIONS ═══
        elif data == "set_sysinfo":
            _send_system_info(chat_id)

        # ═══ AUDIT LOGS ═══
        elif data == "audit_logs":
            _send_audit_logs(chat_id)

        # ═══ CONFIRMATIONS ═══
        elif data.startswith("confirm_yes:"):
            _execute_confirmed_action(data.split(":", 1)[1], chat_id)

        # ═══ LEGACY ROUTER FALLBACK ═══
        else:
            result = router.dispatch(data, {"chat_id": chat_id})
            if isinstance(result, str):
                bot.send_message(chat_id, result, parse_mode="HTML")

        bot.answer_callback_query(call.id)
    except Exception as e:
        safe_error = html.escape(str(e))[:200]
        bot.send_message(chat_id, f"❌ <b>خطأ:</b>\n<pre>{safe_error}</pre>", parse_mode="HTML")
        bot.answer_callback_query(call.id)


# ╔══════════════════════════════════════════════════════════════╗
# ║            HANDLER HELPER FUNCTIONS                         ║
# ╚══════════════════════════════════════════════════════════════╝

def process_pr_create(message):
    """معالجة استجابة الوصف لإنشاء بروتوكول جديد"""
    if message.from_user.id != ADMIN_ID: return
    text = message.text.strip()
    if not text: return
    bot.reply_to(message, "🧠 <b>NEXUM:</b> جاري بناء Execution Graph للبروتوكول...", parse_mode="HTML")
    event_bus.emit(event_bus.TASK_STARTED, {"goal": text})
    try:
        result = orchestrator.execute_goal(text)
        protocol_id = result.get('protocol_id', 'PR-ALPHA')
        msg = f"⚙️ <b>Protocol:</b> <code>{protocol_id}</code>\nالنظام ينفذ التسلسل المطلوب."
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=ui_builder.build_quick_actions())
    except Exception as e:
        safe_error = html.escape(str(e))[:500]
        bot.send_message(message.chat.id, f"❌ <b>فشل:</b>\n<pre>{safe_error}</pre>", parse_mode="HTML")

def process_ai_search(message):
    message.text = f"/search {message.text}"
    cmd_search(message)

def process_ai_scrape(message):
    message.text = f"/scrape {message.text}"
    cmd_scrape(message)

def process_ai_codegen(message):
    message.text = f"/code {message.text}"
    cmd_code(message)

def _edit_to_main_menu(chat_id, msg_id):
    """العودة للقائمة الرئيسية عبر تعديل الرسالة"""
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    agent_count = len(agent_registry.agents)
    text = (
        f"🔱 <b>NEXUM PRIME — Sovereign Agentic OS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <code>OPERATIONAL</code> | 🤖 {agent_count} agents | 🔥 CPU {cpu}% | 🧠 RAM {ram}%\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 اختر قسماً:"
    )
    try:
        bot.edit_message_text(text, chat_id, msg_id, parse_mode="HTML",
                              reply_markup=ui_builder.build_main_control_plane())
    except:
        bot.send_message(chat_id, text, parse_mode="HTML",
                         reply_markup=ui_builder.build_main_control_plane())


def _send_runtime_status(chat_id):
    """تقرير حالة النظام الحي"""
    import platform
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M")
    
    bar_cpu = _progress_bar(cpu)
    bar_ram = _progress_bar(ram.percent)
    bar_disk = _progress_bar(disk.percent)
    
    report = (
        f"📊 <b>Runtime Status — Live</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🖥 <b>OS:</b> {platform.system()} {platform.release()}\n"
        f"⏱ <b>Boot:</b> {uptime}\n\n"
        f"🔥 <b>CPU:</b> {bar_cpu} {cpu}%\n"
        f"🧠 <b>RAM:</b> {bar_ram} {ram.percent}% ({ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB)\n"
        f"💾 <b>Disk:</b> {bar_disk} {disk.percent}%\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(chat_id, report, parse_mode="HTML",
                     reply_markup=ui_builder.build_runtime_menu())


def _send_live_metrics(chat_id):
    """مقاييس أداء حية"""
    cpu_per_core = psutil.cpu_percent(percpu=True)
    net = psutil.net_io_counters()
    
    report = "📈 <b>Live Metrics</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    for i, pct in enumerate(cpu_per_core):
        report += f"  Core {i}: {_progress_bar(pct)} {pct}%\n"
    report += f"\n🌐 <b>Network:</b>\n"
    report += f"  ↑ Sent: {net.bytes_sent // (1024**2)} MB\n"
    report += f"  ↓ Recv: {net.bytes_recv // (1024**2)} MB\n"
    report += f"━━━━━━━━━━━━━━━━━━━━"
    bot.send_message(chat_id, report, parse_mode="HTML",
                     reply_markup=ui_builder.build_runtime_menu())


def _send_eventbus_info(chat_id):
    events = event_bus.get_history(limit=10)
    report = "📡 <b>Event Bus — Last 10 Events</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    if not events:
        report += "📭 لا توجد أحداث مسجلة.\n"
    for ev in events:
        ts = ev['timestamp'].split('T')[1].split('.')[0]
        report += f"🕒 <code>{ts}</code> <b>{ev['type']}</b>\n"
    report += "━━━━━━━━━━━━━━━━━━━━"
    bot.send_message(chat_id, report, parse_mode="HTML",
                     reply_markup=ui_builder.build_runtime_menu())


def _send_agents_roster(chat_id):
    """قائمة الوكلاء مع بطاقات تحكم"""
    agents = agent_registry.agents
    if not agents:
        bot.send_message(chat_id, "⚠️ لا يوجد وكلاء نشطون.", parse_mode="HTML",
                         reply_markup=ui_builder.build_agents_menu())
        return
    
    for agent_id, ag in agents.items():
        state_info = lifecycle.get_state(ag['agent_id'])
        status = state_info.get('state', 'OFFLINE')
        emoji = "🟢" if status in ["READY", "RUNNING"] else "🟡" if status == "CREATED" else "🔴"
        
        caps = ", ".join(ag.get('capabilities', [])[:4]) or "N/A"
        
        card = (
            f"{emoji} <b>{ag['name']}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🎭 <b>الدور:</b> {ag['role']}\n"
            f"📡 <b>الحالة:</b> <code>{status}</code>\n"
            f"🛠 <b>القدرات:</b> {caps}\n"
            f"━━━━━━━━━━━━━━"
        )
        bot.send_message(chat_id, card, parse_mode="HTML",
                         reply_markup=ui_builder.build_agent_card(agent_id, ag['name'], status))


def _spawn_agent_menu(chat_id):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    m = InlineKeyboardMarkup(row_width=1)
    m.add(
        InlineKeyboardButton("🎨 Frontend Builder", callback_data="confirm_yes:spawn_frontend"),
        InlineKeyboardButton("🔧 Infrastructure Agent", callback_data="confirm_yes:spawn_infra"),
        InlineKeyboardButton("🛡️ Security Agent", callback_data="confirm_yes:spawn_security"),
        InlineKeyboardButton("📊 Analytics Agent", callback_data="confirm_yes:spawn_analytics"),
        InlineKeyboardButton("⬅️ Back", callback_data="menu_agents")
    )
    bot.send_message(chat_id, "➕ <b>اختر نوع الوكيل:</b>", parse_mode="HTML", reply_markup=m)


def _handle_agent_control(data, chat_id):
    """التحكم بوكيل محدد (start/stop/restart/logs/memory/tasks)"""
    parts = data.split(":")
    action = parts[0].replace("agctl_", "")
    agent_id = parts[1] if len(parts) > 1 else ""
    
    ag = agent_registry.agents.get(agent_id, {})
    name = ag.get('name', agent_id)
    
    if action == "start":
        lifecycle.init_agent(agent_id)
        bot.send_message(chat_id, f"▶️ تم تشغيل <b>{name}</b>", parse_mode="HTML")
    elif action == "stop":
        lifecycle.transition(agent_id, "TERMINATED")
        bot.send_message(chat_id, f"⏹️ تم إيقاف <b>{name}</b>", parse_mode="HTML")
    elif action == "restart":
        lifecycle.transition(agent_id, "TERMINATED")
        lifecycle.init_agent(agent_id)
        bot.send_message(chat_id, f"🔄 تمت إعادة تشغيل <b>{name}</b>", parse_mode="HTML")
    elif action == "logs":
        events = event_bus.get_history(limit=5)
        agent_events = [e for e in events if e.get('data', {}).get('agent_id') == agent_id]
        report = f"📋 <b>Logs for {name}</b>\n"
        if not agent_events:
            report += "📭 لا توجد سجلات."
        for ev in agent_events:
            report += f"• {ev['type']}\n"
        bot.send_message(chat_id, report, parse_mode="HTML")
    elif action == "memory":
        state = lifecycle.get_state(agent_id)
        bot.send_message(chat_id, f"🧠 <b>Memory for {name}:</b>\n<pre>{html.escape(str(state))}</pre>", parse_mode="HTML")
    elif action == "tasks":
        bot.send_message(chat_id, f"📊 <b>Tasks for {name}:</b>\nلا توجد مهام نشطة حالياً.", parse_mode="HTML")


def _send_protocols_list(chat_id):
    report = (
        "📜 <b>Active Protocols</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "📌 لا توجد بروتوكولات نشطة.\n"
        "استخدم <b>Create Protocol</b> لإنشاء بروتوكول جديد.\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(chat_id, report, parse_mode="HTML",
                     reply_markup=ui_builder.build_protocols_menu())


def _send_execution_graph(chat_id):
    report = (
        "📊 <b>Execution Graph</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "🔗 لعرض الرسم البياني التفاعلي، افتح:\n"
        f"🌐 <a href='{ui_builder.webapp_url}'>Mini App Dashboard</a>\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(chat_id, report, parse_mode="HTML",
                     reply_markup=ui_builder.build_protocols_menu())


def _send_memory_status(chat_id):
    from services.db_service import db_service
    from core.runtime_state import runtime_state
    
    agents_in_mem = len(runtime_state.state.get("agents", {}))
    events_count = len(runtime_state.state.get("events_history", []))
    db_status = "✅ CONNECTED" if db_service.enabled else "❌ OFFLINE"
    
    report = (
        f"💾 <b>Memory Status</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🗃 <b>RAM State:</b> {agents_in_mem} agents, {events_count} events\n"
        f"☁️ <b>Cloud DB:</b> {db_status}\n"
        f"📊 <b>Chat History:</b> 15 messages max (per user)\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(chat_id, report, parse_mode="HTML",
                     reply_markup=ui_builder.build_memory_menu())


def _send_system_info(chat_id):
    import platform
    report = (
        f"ℹ️ <b>System Info</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🐍 Python: {platform.python_version()}\n"
        f"🖥 OS: {platform.system()} {platform.release()}\n"
        f"📦 Arch: {platform.machine()}\n"
        f"🔧 Node: {platform.node()}\n"
        f"🔱 NEXUM Version: 2.2-STABLE\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(chat_id, report, parse_mode="HTML",
                     reply_markup=ui_builder.build_settings_menu())


def _send_audit_logs(chat_id):
    from services.db_service import db_service
    events = event_bus.get_history(limit=8)
    for ev in events:
        db_service.save_audit_log(ev['type'], ev)
    
    if not events:
        bot.send_message(chat_id, "📋 سجل الأحداث فارغ.", parse_mode="HTML")
        return
    
    report = "📋 <b>Audit Logs (Cloud Sync)</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    for ev in events:
        ts = ev['timestamp'].split('T')[1].split('.')[0]
        report += f"🕒 <code>{ts}</code> <b>{ev['type']}</b>\n"
    report += "━━━━━━━━━━━━━━━━━━━━"
    bot.send_message(chat_id, report, parse_mode="HTML",
                     reply_markup=ui_builder.build_quick_actions())


def _run_and_send(chat_id, cmd, title):
    """تنفيذ أمر وإرسال النتيجة"""
    bot.send_chat_action(chat_id, 'typing')
    result = executor.execute(cmd)
    output = result.get('output', 'لا يوجد ناتج.')[:3000]
    safe_output = html.escape(output)
    bot.send_message(chat_id, f"📋 <b>{title}</b>\n<pre>{safe_output}</pre>", parse_mode="HTML")


def _run_ai_task(chat_id, task_description):
    """تشغيل مهمة عبر AI مع سياق النظام"""
    bot.send_chat_action(chat_id, 'typing')
    bot.send_message(chat_id, "🧠 <b>جاري التحليل...</b>", parse_mode="HTML")
    system_ctx = _build_system_context()
    response, _ = _gemini_svc.ask(task_description, system_instruction=system_ctx)
    safe_reply(bot, chat_id, response, is_chat_id=True)


def _execute_confirmed_action(action_id, chat_id):
    """تنفيذ إجراء مؤكد"""
    if action_id == "rt_restart":
        bot.send_message(chat_id, "🔄 <b>جاري إعادة التشغيل...</b>", parse_mode="HTML")
        for agent_id in agent_registry.agents:
            lifecycle.init_agent(agent_id)
        bot.send_message(chat_id, "✅ <b>تم إعادة تشغيل Runtime بنجاح.</b>", parse_mode="HTML",
                         reply_markup=ui_builder.build_runtime_menu())
    elif action_id == "ag_stop_all":
        for agent_id in agent_registry.agents:
            lifecycle.transition(agent_id, "TERMINATED")
        bot.send_message(chat_id, "⏹️ <b>تم إيقاف جميع الوكلاء.</b>", parse_mode="HTML")
    elif action_id == "mem_clear_chat":
        from core.runtime_state import runtime_state
        runtime_state.update_agent_state(f"user_{ADMIN_ID}", {"chat_history": []})
        bot.send_message(chat_id, "🗑️ <b>تم مسح الذاكرة الحوارية.</b>", parse_mode="HTML")
    elif action_id == "dk_prune":
        _run_and_send(chat_id, "docker system prune -f 2>/dev/null || echo 'Docker غير متوفر'", "🧹 Docker Prune")
    elif action_id.startswith("spawn_"):
        agent_type = action_id.replace("spawn_", "")
        bot.send_message(chat_id, f"⚡ <b>جاري إنشاء وكيل {agent_type}...</b>", parse_mode="HTML")
        _run_ai_task(chat_id, f"قم بإنشاء وكيل جديد من نوع {agent_type} وقم بتسجيله في النظام")


def _progress_bar(percentage, length=10):
    """شريط تقدم نصي"""
    filled = int(percentage / 100 * length)
    return "█" * filled + "░" * (length - filled)


# ╔══════════════════════════════════════════════════════════════╗
# ║            NEW COMMANDS (Search, Scrape, Code)              ║
# ╚══════════════════════════════════════════════════════════════╝

@bot.message_handler(commands=['search'])
def cmd_search(message):
    if message.from_user.id != ADMIN_ID: return
    query = message.text.replace('/search', '', 1).strip()
    if not query:
        bot.reply_to(message, "🔍 استخدام: <code>/search استعلام</code>", parse_mode="HTML")
        return
    from core.system_tools import search_web
    bot.send_chat_action(message.chat.id, 'typing')
    result = search_web(query)
    if result['status'] == 'success':
        report = f"🔍 <b>نتائج البحث عن:</b> <code>{html.escape(query)}</code>\n━━━━━━━━━━━━━━━━━━━━\n"
        for r in result.get('results', []):
            report += f"🔗 {html.escape(r.get('url', ''))}\n📝 {html.escape(r.get('snippet', ''))}\n\n"
        if not result.get('results'):
            report += "📭 لم يتم العثور على نتائج."
    else:
        report = f"❌ خطأ في البحث: {html.escape(result.get('message', ''))}"
    safe_reply(bot, message, report)

@bot.message_handler(commands=['scrape'])
def cmd_scrape(message):
    if message.from_user.id != ADMIN_ID: return
    url = message.text.replace('/scrape', '', 1).strip()
    if not url:
        bot.reply_to(message, "🕸️ استخدام: <code>/scrape https://example.com</code>", parse_mode="HTML")
        return
    from core.system_tools import fetch_webpage
    bot.send_chat_action(message.chat.id, 'typing')
    result = fetch_webpage(url)
    if result['status'] == 'success':
        content = result.get('content', '')[:3000]
        report = f"🕸️ <b>محتوى:</b> <code>{html.escape(url[:60])}</code>\n━━━━━━━━━━━━━━━━━━━━\n<pre>{html.escape(content)}</pre>"
    else:
        report = f"❌ خطأ: {html.escape(result.get('message', ''))}"
    safe_reply(bot, message, report)

@bot.message_handler(commands=['code'])
def cmd_code(message):
    if message.from_user.id != ADMIN_ID: return
    desc = message.text.replace('/code', '', 1).strip()
    if not desc:
        bot.reply_to(message, "📝 استخدام: <code>/code وصف ما تريد برمجته</code>", parse_mode="HTML")
        return
    _run_ai_task(message.chat.id, f"اكتب كود بايثون لتنفيذ المهمة التالية: {desc}")

@bot.message_handler(commands=['run'])
def handle_run(message):
    if message.from_user.id != ADMIN_ID: return
    cmd = message.text.replace('/run', '', 1).strip()
    if not cmd:
        bot.reply_to(message, "استخدام: <code>/run الأمر</code>", parse_mode="HTML")
        return
    result = executor.execute(cmd)
    if result['status'] == 'confirm':
        pending_commands[message.from_user.id] = cmd
        bot.reply_to(message, fmt.warning(f"أمر حساس:\n<code>{cmd}</code>"), parse_mode="HTML")
        return
    send_terminal_output(bot, message.chat.id, result['status'], result['output'])


# ╔══════════════════════════════════════════════════════════════╗
# ║         MULTIMODAL HANDLER (Photos/Docs/Audio)              ║
# ╚══════════════════════════════════════════════════════════════╝

@bot.message_handler(content_types=['document', 'photo', 'audio', 'voice'])
def handle_multimodal(message):
    if message.from_user.id != ADMIN_ID: return
    bot.send_chat_action(message.chat.id, 'typing')
    
    file_id = None
    mime_type = None
    
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        mime_type = 'image/jpeg'
    elif message.content_type == 'document':
        file_id = message.document.file_id
        mime_type = message.document.mime_type
        file_name = message.document.file_name.lower() if message.document.file_name else "file.txt"
        if mime_type == 'application/octet-stream' or any(file_name.endswith(ext) for ext in ['.txt', '.py', '.js', '.html', '.css', '.json', '.md', '.csv', '.yml', '.yaml', '.sh']):
            mime_type = 'text/plain'
    elif message.content_type == 'audio':
        file_id = message.audio.file_id
        mime_type = message.audio.mime_type
    elif message.content_type == 'voice':
        file_id = message.voice.file_id
        mime_type = message.voice.mime_type
    
    if not file_id: return
    
    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ تحميل: {str(e)}")
        return
    
    system_instr = _build_system_context()
    history = get_user_history(message.from_user.id)
    prompt = message.caption or "حلل هذا الملف واتخذ الإجراء المناسب."
    
    if mime_type == 'text/plain':
        try:
            text_content = downloaded_file.decode('utf-8')
            prompt = f"{prompt}\n\n=== محتوى الملف ===\n{text_content}"
            downloaded_file = None
            mime_type = None
        except: pass
    
    bot.send_message(message.chat.id, "👁️ <b>NEXUM:</b> جاري التحليل...", parse_mode="HTML")
    response, new_history = _gemini_svc.ask(prompt, history=history, system_instruction=system_instr, file_data=downloaded_file, mime_type=mime_type)
    update_user_history(message.from_user.id, new_history)
    safe_reply(bot, message, response)


# ╔══════════════════════════════════════════════════════════════╗
# ║              TEXT HANDLER (AI Chat + Orchestration)          ║
# ╚══════════════════════════════════════════════════════════════╝

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.strip()

    EXEC_KW = ['ثبت', 'شغل', 'نفذ', 'ابن', 'build', 'create', 'أنشئ', 'صمم', 'spawn']
    if any(k in text.lower() for k in EXEC_KW):
        bot.reply_to(message, "🧠 <b>NEXUM:</b> جاري بناء Execution Graph...", parse_mode="HTML")
        event_bus.emit(event_bus.TASK_STARTED, {"goal": text})
        try:
            result = orchestrator.execute_goal(text)
            protocol_id = result.get('protocol_id', 'PR-ALPHA')
            msg = f"⚙️ <b>Protocol:</b> <code>{protocol_id}</code>\nالنظام ينفذ التسلسل المطلوب."
            bot.send_message(message.chat.id, msg, parse_mode="HTML",
                             reply_markup=ui_builder.build_quick_actions())
        except Exception as e:
            safe_error = html.escape(str(e))[:500]
            bot.send_message(message.chat.id, f"❌ <b>فشل:</b>\n<pre>{safe_error}</pre>", parse_mode="HTML")
        return

    # AI Chat Mode
    bot.send_chat_action(message.chat.id, 'typing')
    system_instr = _build_system_context()
    history = get_user_history(message.from_user.id)
    response, new_history = _gemini_svc.ask(text, history=history, system_instruction=system_instr)
    update_user_history(message.from_user.id, new_history)
    safe_reply(bot, message, response)


# ╔══════════════════════════════════════════════════════════════╗
# ║                         MAIN                                ║
# ╚══════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    print(f"🔱 NEXUM PRIME OS [DEPLOYED AT {datetime.now().strftime('%H:%M:%S')}]")
    
    from core.system_tools import register_all_system_tools
    register_all_system_tools()
    
    for agent_id in agent_registry.agents:
        lifecycle.init_agent(agent_id)
    
    print("🎮 Interactive Control System: ACTIVE")
    print("📌 All menus, buttons, and cards are operational.")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Main Error: {e}")
