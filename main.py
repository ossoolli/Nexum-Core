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
from agents.monitor import monitor_agent
from agents.deploy import deploy_agent
from agents.docker_agent import docker_agent
from services.gemini_service import GeminiService
from core.formatters import fmt

# === Bot Setup ===
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# === AI Services ===
_gemini_svc = GeminiService(os.getenv("GOOGLE_API_KEY"))
_planner = AIPlanner(_gemini_svc)
_memory = LongTermMemory(os.path.join(BASE_DIR, "storage", "memory.json"))

pending_commands = {}


# === تسجيل Handlers في الـ Callback Router ===
def _handle_hw_status(cb_data, ctx):
    data = monitor_agent.get_system_data()
    return fmt.system_report(
        data['cpu'], data['ram'], data['disk'], data['net'],
        data['uptime'], data['hostname']
    )

def _handle_list_agents(cb_data, ctx):
    from core.agent_registry import agent_registry
    agents = agent_registry.agents
    if not agents:
        return "لا يوجد وكلاء مسجلين حالياً."
    report = fmt.header("Agents Registry") + "\n\n"
    for _, ag in agents.items():
        state = lifecycle.get_state(ag['agent_id'])
        status = state.get('state', ag.get('status', 'UNKNOWN'))
        report += f"🤖 <b>{ag['name']}</b> ({status})\n⚙️ {ag['role']}\n\n"
    return report

def _handle_github_deploy(cb_data, ctx):
    return deploy_agent.deploy_updates("🔱 NEXUM Auto-Deploy")

def _handle_agent_approve(cb_data, ctx):
    agent_name = ctx.get('param', 'unknown')
    return f"✅ تمت الموافقة للوكيل: {agent_name}"

def _handle_agent_deny(cb_data, ctx):
    agent_name = ctx.get('param', 'unknown')
    return f"❌ تم الرفض للوكيل: {agent_name}"

# تسجيل المسارات
router.register("hw_status", _handle_hw_status)
router.register("list_agents", _handle_list_agents)
router.register("github_deploy", _handle_github_deploy)
router.register("agent:approve", _handle_agent_approve)
router.register("agent:deny", _handle_agent_deny)


# ===== القائمة الرئيسية =====
@bot.message_handler(commands=['start', 'menu', 'dashboard'])
def cmd_start(message):
    if message.from_user.id != ADMIN_ID: return
    event_bus.emit(event_bus.SYSTEM_ALERT, {"action": "start", "user": ADMIN_ID})
    bot.send_message(
        message.chat.id,
        fmt.header("NEXUM PRIME META-OS"),
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
    text = message.text.strip().lower()

    EXEC_KW = ['ثبت', 'شغل', 'نفذ', 'ابن', 'build', 'create', 'أنشئ', 'صمم']
    if any(k in text for k in EXEC_KW):
        bot.reply_to(message, fmt.info("🧠 NEXUM PRIME: جاري توزيع المهام عبر الأوركستريتور..."))
        event_bus.emit(event_bus.TASK_STARTED, {"goal": text})
        try:
            result = orchestrator.execute_goal(text)
            protocol_id = result['protocol']['protocol_id']
            steps = len(result['protocol']['execution_graph'])
            event_bus.emit(event_bus.TASK_COMPLETED, {"protocol_id": protocol_id})
            msg = f"✅ <b>بروتوكول:</b> {protocol_id}\nتم تنفيذ {steps} خطوة عبر الوكلاء."
            bot.send_message(message.chat.id, fmt.success(msg), parse_mode="HTML")
        except Exception as e:
            event_bus.emit(event_bus.TASK_FAILED, {"error": str(e)})
            bot.send_message(message.chat.id, fmt.error(f"❌ خطأ: {str(e)}"), parse_mode="HTML")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    response = _gemini_svc.ask(message.text)
    safe_reply(bot, message, response)


if __name__ == "__main__":
    print("🔱 NEXUM PRIME Sovereign OS — ONLINE")
    # تهيئة دورة حياة الوكلاء الأساسيين
    from core.agent_registry import agent_registry
    for agent_id in agent_registry.agents:
        lifecycle.init_agent(agent_id)
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Error: {e}")
