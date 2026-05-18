import os
import sys
import telebot
from dotenv import load_dotenv

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

# === Bot Setup ===
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# === AI Services ===
_gemini_svc = GeminiService(os.getenv("GOOGLE_API_KEY"))
_planner = AIPlanner(_gemini_svc)
_memory = LongTermMemory(os.path.join(BASE_DIR, "storage", "memory.json"))

# === ربط العقل المدبر بمحرك التنفيذ ===
orchestrator.set_planner(_planner)

pending_commands = {}


# === إدارة الذاكرة الحوارية ===
def get_user_history(user_id):
    from core.runtime_state import runtime_state
    state = runtime_state.get_agent_state(f"user_{user_id}")
    return state.get("chat_history", [])

def update_user_history(user_id, history):
    from core.runtime_state import runtime_state
    # الاحتفاظ بآخر 10 رسائل فقط لتوفير التوكينز
    runtime_state.update_agent_state(f"user_{user_id}", {"chat_history": history[-10:]})

# === تسجيل Handlers في الـ Callback Router ===
def _handle_hw_status(cb_data, ctx):
    import psutil, platform
    from datetime import datetime
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    uptime = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"📊 <b>تقرير حالة النظام (Real-time)</b>\n"
    report += f"━━━━━━━━━━━━━━━━━━━━\n"
    report += f"🖥 <b>نظام التشغيل:</b> {platform.system()} {platform.release()}\n"
    report += f"🔥 <b>المعالج (CPU):</b> {cpu}%\n"
    report += f"🧠 <b>الرام (RAM):</b> {ram}%\n"
    report += f"💾 <b>القرص (Disk):</b> {disk}%\n"
    report += f"⏱ <b>وقت الإقلاع:</b> {uptime}\n"
    report += f"━━━━━━━━━━━━━━━━━━━━"
    return report

def _handle_list_agents(cb_data, ctx):
    from core.agent_registry import agent_registry
    agents = agent_registry.agents
    if not agents:
        return "⚠️ لا يوجد وكلاء نشطون حالياً في النظام."
    
    report = f"🤖 <b>قائمة الوكلاء النشطين (Roster)</b>\n\n"
    for _, ag in agents.items():
        state_info = lifecycle.get_state(ag['agent_id'])
        status = state_info.get('state', 'OFFLINE')
        emoji = "🟢" if status in ["READY", "RUNNING"] else "🔴"
        report += f"{emoji} <b>{ag['name']}</b>\n"
        report += f"└ 🎭 <b>الدور:</b> {ag['role']}\n"
        report += f"└ 📡 <b>الحالة:</b> {status}\n\n"
    return report

def _handle_audit_logs(cb_data, ctx):
    from core.event_bus import event_bus
    history = event_bus.get_history(limit=5)
    if not history:
        return "📋 سجل الأحداث فارغ حالياً."
    
    report = "📋 <b>أحدث سجلات التدقيق (Audit Logs):</b>\n\n"
    for ev in history:
        ts = ev['timestamp'].split('T')[1].split('.')[0]
        report += f"🕒 <code>[{ts}]</code> <b>{ev['type']}</b>\n"
    return report

def _handle_github_deploy(cb_data, ctx):
    from agents.deploy import deploy_agent
    return deploy_agent.deploy_updates("🔱 NEXUM Auto-Deploy")

# تسجيل المسارات الجديدة
router.register("hw_status", _handle_hw_status)
router.register("list_agents", _handle_list_agents)
router.register("audit_logs", _handle_audit_logs)
router.register("github_deploy", _handle_github_deploy)

# ===== القائمة الرئيسية =====
@bot.message_handler(commands=['start', 'menu', 'dashboard'])
def cmd_start(message):
    if message.from_user.id != ADMIN_ID: return
    
    # تحديث الحالة في الـ Runtime State
    from core.runtime_state import runtime_state
    runtime_state.update_agent_state(f"user_{ADMIN_ID}", {"last_seen": datetime.now().isoformat()})
    
    event_bus.emit(event_bus.SYSTEM_ALERT, {"action": "dashboard_access", "user": ADMIN_ID})
    
    text = (
        f"🔱 <b>مرحباً بك في NEXUM PRIME META-OS</b>\n"
        f"لقد تم تفعيل نظام التشغيل السيادي. جميع الأنظمة تحت سيطرتك الآن.\n\n"
        f"⚡ <b>الحالة:</b> <code>System Online</code>\n"
        f"🛠 <b>الأدوات المتاحة:</b> Sandbox, Terminal, Planner, Multi-Agent DAG\n"
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=ui_builder.build_main_control_plane()
    )


# ===== Callback Handler الموحد (يمرر للـ Router) =====
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    if call.from_user.id != ADMIN_ID: return
    
    result = router.dispatch(call.data, {"chat_id": call.message.chat.id})
    
    if isinstance(result, str):
        bot.send_message(call.message.chat.id, result, parse_mode="HTML")
    elif isinstance(result, dict) and "error" not in result:
        bot.send_message(call.message.chat.id, str(result), parse_mode="HTML")


# ===== أمر التيرمينال =====
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

# ===== الرسائل النصية =====
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.strip()

    # كلمات مفتاحية للتنفيذ المباشر (Orchestration)
    EXEC_KW = ['ثبت', 'شغل', 'نفذ', 'ابن', 'build', 'create', 'أنشئ', 'صمم', 'spawn']
    if any(k in text.lower() for k in EXEC_KW):
        bot.reply_to(message, "🧠 <b>NEXUM PRIME:</b> جاري تحليل المهمة وبناء الـ Execution Graph...")
        event_bus.emit(event_bus.TASK_STARTED, {"goal": text})
        try:
            # مناداة Planner لتوليد الخطة ثم الأوركستريتور للتنفيذ
            result = orchestrator.execute_goal(text)
            protocol_id = result.get('protocol', {}).get('protocol_id', 'PR-ALPHA')
            msg = f"⚙️ <b>بروتوكول التنفيذ المفعل:</b> <code>{protocol_id}</code>\nالنظام يبدأ الآن بتشغيل الحاويات وتنفيذ التسلسل المطلوب."
            bot.send_message(message.chat.id, msg, parse_mode="HTML")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ <b>فشل في الجدولة:</b> {str(e)}", parse_mode="HTML")
        return

    # تجهيز سياق كامل للنظام مع "عين" على الملفات
    active_agents = [ag['name'] for ag in agent_registry.agents.values()]
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    
    # رؤية هيكل المشروع الحالي
    try:
        project_files = os.listdir(BASE_DIR)
        files_snapshot = ", ".join(project_files[:15]) # أول 15 ملف للمعاينة
    except:
        files_snapshot = "تعذر جلب القائمة"
    
    system_instr = f"""
أنت نظام تشغيل ذكاء اصطناعي سيادي (NEXUM OS). أنت الآن بمستوى ذكاء وكيل Antigravity.
حالة النظام الحقيقية التي "تراها" الآن:
- الوكلاء النشطون: {', '.join(active_agents) if active_agents else 'لا يوجد'}
- الموارد: CPU {cpu}%, RAM {ram}%
- الملفات في الجذر: {files_snapshot}

قدراتك السيادية:
1. اتخاذ القرارات: لا تسأل "هل أفعل؟"، بل حلل الهدف ونفذه فوراً.
2. الاستكشاف: يمكنك استخدام `list_directory` و `read_file` لتعرف ماذا يوجد بداخل السيرفر قبل أن تقرر التعديل.
3. التمرير للأوركستريتور: أنت من يبني الـ Execution Graph الذي يحرك السيرفر.

تحدث بلهجة "النظام المسيطر" الذي يعرف كل ملف وكل عملية في جهازه.
"""
    
    history = get_user_history(message.from_user.id)
    response, new_history = _gemini_svc.ask(text, history=history, system_instruction=system_instr)
    update_user_history(message.from_user.id, new_history)
    
    safe_reply(bot, message, response)


if __name__ == "__main__":
    from datetime import datetime
    print(f"🔱 NEXUM PRIME OS [DEPLOYED AT {datetime.now().strftime('%H:%M:%S')}]")
    
    # تسجيل أدوات النظام
    from core.system_tools import register_all_system_tools
    register_all_system_tools()
    
    # تهيئة الوكلاء
    from core.agent_registry import agent_registry
    for agent_id in agent_registry.agents:
        lifecycle.init_agent(agent_id)
        
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Main Error: {e}")
