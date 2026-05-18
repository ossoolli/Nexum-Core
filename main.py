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
from agents.monitor import monitor_agent
from agents.deploy import deploy_agent
from agents.docker_agent import docker_agent
from services.gemini_service import GeminiService
from core.keyboards import (
    main_menu, monitor_menu, deploy_menu, docker_menu, ai_menu, settings_menu, 
    finance_menu, back_button, MENU_MAP, confirm_action
)
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
        fmt.welcome_message(), 
        parse_mode="HTML", 
        reply_markup=main_menu()
    )


# ===== Callback Handlers (الملاحة العامة) =====
@bot.callback_query_handler(func=lambda call: call.data in MENU_MAP or call.data == "back_main")
def handle_menu_navigation(call):
    if call.from_user.id != ADMIN_ID: return
    
    if call.data == "back_main":
        bot.edit_message_text(
            fmt.header("القائمة الرئيسية", "اختر القسم المطلوب"),
            call.message.chat.id, call.message.message_id,
            reply_markup=main_menu(), parse_mode="HTML"
        )
        return

    text, markup_func = MENU_MAP[call.data]
    bot.edit_message_text(
        text,
        call.message.chat.id, call.message.message_id,
        reply_markup=markup_func(), parse_mode="HTML"
    )

# ===== وظائف الأزرار (الشاشات الفرعية) =====
@bot.callback_query_handler(func=lambda call: call.data.startswith("mon_"))
def handle_monitor_cbs(call):
    if call.from_user.id != ADMIN_ID: return
    bot.answer_callback_query(call.id, "جاري فحص حالة النظام...")
    data = monitor_agent.get_system_data()
    action = call.data
    
    if action == "mon_full":
        report = fmt.system_report(
            data['cpu'], data['ram'], data['disk'], data['net'], 
            data['uptime'], data['hostname']
        )
    elif action == "mon_cpu":
        details = monitor_agent.get_cpu_details()
        report = fmt.cpu_report(details['percent'], details['count'], details['freq'], details['per_cpu'])
    elif action == "mon_ram":
        report = fmt.ram_report(data['ram'])
    elif action == "mon_disk":
        report = fmt.disk_report(data['disk'])
    elif action == "mon_network":
        report = fmt.network_report(data['net'])
    else:
        report = "المؤشر قيد التطوير."

    bot.edit_message_text(
        report, call.message.chat.id, call.message.message_id,
        reply_markup=monitor_menu(), parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("dock_"))
def handle_docker_cbs(call):
    if call.from_user.id != ADMIN_ID: return
    bot.answer_callback_query(call.id, "نظام Docker...")
    action = call.data
    
    if action == "dock_ps":
        containers = docker_agent.get_containers_list()
        if not containers:
            report = fmt.info("لا توجد حاويات تعمل حالياً.")
        else:
            cards = [fmt.docker_container_card(c['name'], c['status'], c['ports'], c['image']) for c in containers]
            report = fmt.header("حاويات Docker") + "\n\n" + "\n\n".join(cards)
    elif action == "dock_stats":
        stats = docker_agent.get_stats()
        report = fmt.header("استهلاك الحاويات") + fmt.code_block(stats)
    else:
        report = fmt.info("سيتم إضافة هذه الميزة قريباً في واجهة تلجرام.")

    bot.edit_message_text(
        report, call.message.chat.id, call.message.message_id,
        reply_markup=docker_menu(), parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("dep_"))
def handle_deploy_cbs(call):
    if call.from_user.id != ADMIN_ID: return
    bot.answer_callback_query(call.id, "جاري فحص المستودع...")
    
    if call.data == "dep_status":
        out = deploy_agent.git_status()
        bot.edit_message_text(
            fmt.deploy_report("Git Status", out), 
            call.message.chat.id, call.message.message_id, 
            reply_markup=deploy_menu(), parse_mode="HTML"
        )
    elif call.data == "dep_pull":
        out = deploy_agent.git_pull()
        bot.edit_message_text(
            fmt.deploy_report("Git Pull", out),
            call.message.chat.id, call.message.message_id,
            reply_markup=deploy_menu(), parse_mode="HTML"
        )
    elif call.data == "dep_full":
        out = deploy_agent.deploy_updates("🔱 NEXUM Auto-Deploy from Inline")
        bot.send_message(call.message.chat.id, out, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == "open_webapp")
def handle_webapp(call):
    # In reality, this requires binding a domain/ngrok URL. Mocking for now.
    url = "https://your-public-url.com" 
    report = fmt.info("لفتح لوحة التحكم عبر WebApp، يلزم ربط رابط حقيقي بالبوت.")
    bot.send_message(call.message.chat.id, report, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data in ["confirm_run", "cancel_action", "cancel_run"])
def handle_commands_confirm(call):
    if call.from_user.id != ADMIN_ID: return
    if call.data == "cancel_run" or call.data == "cancel_action":
        pending_commands.pop(call.from_user.id, None)
        bot.edit_message_text("❌ تم الإلغاء.", call.message.chat.id, call.message.message_id)
        return
        
    cmd = pending_commands.pop(call.from_user.id, None)
    if cmd:
        res = executor.execute(cmd, force=True)
        bot.edit_message_text(
            fmt.deploy_report("أمر التيرمينال", res['output'], res['status']),
            call.message.chat.id, call.message.message_id, parse_mode="HTML"
        )


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
        bot.reply_to(
            message, 
            fmt.warning(f"أمر حساس يحتاج لتأكيد:\n<code>{cmd}</code>"), 
            reply_markup=confirm_action("run"), parse_mode="HTML"
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
