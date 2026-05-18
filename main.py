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


# ===== القائمة الرئيسية =====
@bot.message_handler(commands=['start', 'menu', 'dashboard'])
def cmd_start(message):
    if message.from_user.id != ADMIN_ID: return
    bot.send_message(
        message.chat.id, 
        fmt.header("NEXUM PRIME META-OS"), 
        parse_mode="HTML",
        reply_markup=ui_builder.build_main_control_plane()
    )


# ===== Callback Handlers (الملاحة السريعة للواجهة الهجينة) =====
@bot.callback_query_handler(func=lambda call: True)
def handle_hybrid_cbs(call):
    if call.from_user.id != ADMIN_ID: return
    action = call.data

    if action == "hw_status":
        bot.answer_callback_query(call.id, "جاري فحص نظام التشغيل...")
        data = monitor_agent.get_system_data()
        report = fmt.system_report(
            data['cpu'], data['ram'], data['disk'], data['net'], 
            data['uptime'], data['hostname']
        )
        bot.send_message(call.message.chat.id, report, parse_mode="HTML")

    elif action == "list_agents":
        from core.agent_registry import agent_registry
        agents = agent_registry.agents
        if not agents:
            bot.send_message(call.message.chat.id, "لا يوجد وكلاء يعملون حالياً.")
            return
        report = fmt.header("Agents Registry") + "\n\n"
        for _, ag in agents.items():
            report += f"🤖 <b>{ag['name']}</b> ({ag['status']})\n⚙️ {ag['role']}\n\n"
        bot.send_message(call.message.chat.id, report, parse_mode="HTML")

    elif action == "github_deploy":
        out = deploy_agent.deploy_updates("🔱 NEXUM Auto-Deploy from Quick Control")
        bot.send_message(call.message.chat.id, out, parse_mode="HTML")
        
    elif action.startswith("agent_approve"):
        # التعامل مع الموافقة المستقبلية للوكلاء
        bot.edit_message_text(f"✅ تمت الموافقة للوكيل: {action.split(':')[1]}", call.message.chat.id, call.message.message_id)

    elif action.startswith("agent_deny"):
        bot.edit_message_text(f"❌ تم الرفض للوكيل: {action.split(':')[1]}", call.message.chat.id, call.message.message_id)


# ===== الرسائل النصية والأوامر المباشرة =====
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
        from core.keyboards import HybridInterfaceBuilder
        # Using a mockup for confirm_action if needed here, or standard inline keyboard
        # For safety, let's keep it simple
        bot.reply_to(
            message, 
            fmt.warning(f"أمر حساس يحتاج لتأكيد:\n<code>{cmd}</code>"), 
            parse_mode="HTML"
        )
        return
    
    send_terminal_output(bot, message.chat.id, result['status'], result['output'])


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.strip().lower()
    
    # لو كان الأمر عبارة عن توجيه ذكي للتنفيذ
    EXEC_KW = ['ثبت', 'شغل', 'نفذ', 'ابن', 'build', 'create', 'أنشئ', 'صمم']
    if any(k in text for k in EXEC_KW):
        bot.reply_to(message, fmt.info("🧠 جاري تفعيل المايسترو (NEXUM PRIME META-AGENT) ليقوم بتوزيع المهام..."))
        try:
            result = orchestrator.execute_goal(text)
            protocol_id = result['protocol']['protocol_id']
            graph_steps = len(result['protocol']['execution_graph'])
            
            msg = (
                f"✅ <b>اكتمل بروتوكول العمل:</b> {protocol_id}\n"
                f"تم بناء مسار من {graph_steps} خطوة ومعالجتها عبر الوكلاء."
            )
            bot.send_message(message.chat.id, fmt.success(msg), parse_mode="HTML")
        except Exception as e:
            bot.send_message(message.chat.id, fmt.error(f"❌ خطأ من الأوركستريتور: {str(e)}"), parse_mode="HTML")
        return

    # التحدث مع الذكاء الاصطناعي كالمعتاد
    bot.send_chat_action(message.chat.id, 'typing')
    response = _gemini_svc.ask(message.text)
    safe_reply(bot, message, response)


if __name__ == "__main__":
    print("🔱 NEXUM CORE UI/UX System IS ONLINE...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Error starting bot: {e}")
