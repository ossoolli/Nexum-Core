import os
import sys
import html as html_module
import telebot
from telebot import types
from dotenv import load_dotenv

# === Dynamic Path Setup ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

# === Core Imports ===
from core.llm_factory import llm
from core.executor import executor
from core.safe_sender import send_terminal_output, safe_reply
from core.planner import AIPlanner
from core.memory_local import LongTermMemory
from agents.monitor import monitor_agent
from agents.deploy import deploy_agent
from services.gemini_service import GeminiService

# === Bot Setup ===
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# === AI Services ===
_gemini_svc = GeminiService(os.getenv("GOOGLE_API_KEY"))
_planner = AIPlanner(_gemini_svc)
_memory = LongTermMemory(os.path.join(BASE_DIR, "storage", "memory.json"))

# === State ===
pending_commands = {}


# ===== المترجم والمنسق السيادي =====
class NexumInterpreter:
    def process_request(self, user_id, text):
        clean_text = text.lower().strip()

        if any(w in clean_text for w in ["حالة النظام", "status", "النبض", "pulse"]):
            return monitor_agent.get_pulse_report()

        if any(w in clean_text for w in ["ارفع الكود", "deploy", "push", "جيت هب", "github"]):
            return deploy_agent.deploy_updates(f"🔱 NEXUM Deployment: {text[:20]}")

        if any(w in clean_text for w in ["إصلاح", "fix", "debug", "برمجة عميقة"]):
            return llm.ask_specialist(f"مهمة تطوير وإصلاح كود معقد: {text}")

        return llm.ask_gemini(user_id, text)


interpreter = NexumInterpreter()


# ===== لوحة التحكم =====
def get_dashboard_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📊 حالة النظام", callback_data="status"),
        types.InlineKeyboardButton("🛠️ إصلاح شامل", callback_data="fix_all")
    )
    markup.add(types.InlineKeyboardButton("⭐ ترقية الحساب (Stars)", callback_data="upgrade"))
    return markup


# ===== Command Handlers =====

@bot.message_handler(commands=['start', 'dashboard'])
def send_dashboard(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "🔱 <b>NEXUM CORE OS</b>\n\nالأوامر المتاحة:\n"
        "/run <code>أمر</code> — تنفيذ مباشر\n"
        "/planx <code>هدف</code> — تخطيط وتنفيذ ذكي\n"
        "/docker — حالة الحاويات\n"
        "/status — نبض السيرفر",
        parse_mode="HTML"
    )


@bot.message_handler(commands=['status'])
def handle_status(message):
    if message.from_user.id != ADMIN_ID:
        return
    report = monitor_agent.get_pulse_report()
    try:
        bot.reply_to(message, report, parse_mode="HTML")
    except Exception:
        bot.reply_to(message, report.replace('<', '').replace('>', ''))


@bot.message_handler(commands=['run'])
def handle_run(message):
    if message.from_user.id != ADMIN_ID:
        return
    cmd = message.text.replace('/run', '', 1).strip()
    if not cmd:
        bot.reply_to(message, "الاستخدام: <code>/run الأمر</code>", parse_mode="HTML")
        return

    result = executor.execute(cmd)

    if result['status'] == 'confirm':
        pending_commands[message.from_user.id] = cmd
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ نفّذ", callback_data="confirm_run"),
            types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_run")
        )
        bot.reply_to(
            message,
            f"⚠️ أمر حساس:\n<code>{html_module.escape(cmd)}</code>",
            reply_markup=markup, parse_mode="HTML"
        )
        return

    out = html_module.escape(str(result.get('output', '')))
    icon = "✅" if result['status'] == 'success' else "❌"
    try:
        bot.reply_to(message, f"{icon}\n<pre>{out[:3500]}</pre>", parse_mode="HTML")
    except Exception:
        bot.reply_to(message, f"{icon}\n{str(result.get('output', ''))[:3500]}")


@bot.message_handler(commands=['planx', 'plan'])
def handle_planx(message):
    if message.from_user.id != ADMIN_ID:
        return
    goal = message.text.split(' ', 1)[1].strip() if ' ' in message.text else ''
    if not goal:
        bot.reply_to(message, "الاستخدام: <code>/planx هدف</code>", parse_mode="HTML")
        return
    _run_plan(message, goal)


@bot.message_handler(commands=['docker'])
def handle_docker(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) == 1:
        report = deploy_agent.docker_status()
    elif len(args) >= 3 and args[1] == 'logs':
        report = deploy_agent.docker_logs(args[2])
    else:
        report = "الاستخدام:\n<code>/docker</code>\n<code>/docker logs اسم_الحاوية</code>"
    try:
        bot.reply_to(message, report, parse_mode="HTML")
    except Exception:
        bot.reply_to(message, report.replace('<', '').replace('>', ''))


# ===== Callback Handlers =====

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.from_user.id != ADMIN_ID:
        return
    bot.answer_callback_query(call.id, "جاري التنسيق مع الوكلاء...")

    if call.data == "status":
        response = interpreter.process_request(call.from_user.id, "حالة النظام")
        bot.edit_message_text(
            response, call.message.chat.id, call.message.message_id,
            reply_markup=get_dashboard_markup(), parse_mode="HTML"
        )
    elif call.data == "fix_all":
        response = interpreter.process_request(call.from_user.id, "ارفع الكود")
        bot.edit_message_text(
            response, call.message.chat.id, call.message.message_id,
            reply_markup=get_dashboard_markup(), parse_mode="HTML"
        )
    elif call.data == "upgrade":
        prices = [types.LabeledPrice(label="Sovereign Upgrade", amount=500)]
        bot.send_invoice(
            call.message.chat.id,
            title="Sovereign Subscription Upgrade",
            description="ترقية حسابك لتفعيل وكلاء الذكاء الاصطناعي الفوقيين.",
            invoice_payload="sovereign_upgrade_payload",
            provider_token="",
            currency="XTR",
            prices=prices
        )
    elif call.data == "confirm_run":
        cmd = pending_commands.pop(call.from_user.id, None)
        if cmd:
            result = executor.execute(cmd, force=True)
            out = html_module.escape(str(result.get('output', '')))
            bot.send_message(
                call.message.chat.id,
                f"✅ تم التنفيذ:\n<pre>{out[:3500]}</pre>",
                parse_mode="HTML"
            )
    elif call.data == "cancel_run":
        pending_commands.pop(call.from_user.id, None)
        bot.answer_callback_query(call.id, "تم الإلغاء.")


# ===== Payment Handlers =====

@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def handle_payment_success(message):
    payment = message.successful_payment
    bot.send_message(
        message.chat.id,
        f"✅ <b>تمت المصادقة المالية بنجاح!</b>\n"
        f"المبلغ: {payment.total_amount} ⭐\n"
        f"معرف العملية: <code>{payment.telegram_payment_charge_id}</code>",
        parse_mode="HTML"
    )


# ===== Smart Text Handler (catch-all) =====

EXEC_KEYWORDS = [
    'ثبت', 'install', 'تثبيت', 'شغل', 'run', 'ارفع', 'deploy', 'احذف',
    'remove', 'أنشئ', 'create', 'أوقف', 'stop', 'أعد تشغيل', 'restart',
    'حدّث', 'update', 'upgrade', 'نفذ', 'execute', 'ابنِ', 'build'
]


@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def handle_smart(message):
    text = message.text.strip()
    text_lower = text.lower()
    is_exec = any(kw in text_lower for kw in EXEC_KEYWORDS)

    if is_exec:
        _run_plan(message, text)
    else:
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            response = _gemini_svc.ask(text)
            bot.reply_to(message, response)
        except Exception as e:
            bot.reply_to(message, f"❌ {str(e)}")


# ===== Plan Executor =====

def _run_plan(message, goal):
    status_msg = bot.reply_to(message, "🧠 جاري التخطيط...")
    _memory.save_context(message.from_user.id, goal, role='user')
    plan = _planner.create_plan(goal)

    if "error" in plan:
        bot.edit_message_text(
            f"❌ {plan['error']}", message.chat.id, status_msg.message_id
        )
        return

    steps = plan.get('steps', [])
    plan_name = plan.get('plan_name', 'خطة تنفيذية')
    total = len(steps)

    bot.edit_message_text(
        f"📋 <b>{html_module.escape(plan_name)}</b>\n🔢 الخطوات: {total}",
        message.chat.id, status_msg.message_id, parse_mode="HTML"
    )

    for i, step in enumerate(steps, 1):
        cmd = step.get('command', '')
        desc = step.get('description', '')
        bot.send_message(
            message.chat.id,
            f"⏳ <b>{i}/{total}</b> — {html_module.escape(desc)}",
            parse_mode="HTML"
        )
        result = executor.execute(cmd)

        if result['status'] == 'confirm':
            pending_commands[message.from_user.id] = cmd
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ نفّذ", callback_data="confirm_run"),
                types.InlineKeyboardButton("❌ تخطَّ", callback_data="cancel_run")
            )
            bot.send_message(
                message.chat.id,
                f"⚠️ <code>{html_module.escape(cmd)}</code>",
                reply_markup=markup, parse_mode="HTML"
            )
            continue

        if result['status'] == 'failed':
            bot.send_message(message.chat.id, "⚠️ تعثّر — أبحث عن حل...")
            correction = _planner.create_correction_plan(goal, cmd, result['output'])
            if "fixed_command" in correction:
                result = executor.execute(correction['fixed_command'], force=True)

        send_terminal_output(
            bot, message.chat.id,
            result['status'], result['output'],
            f"الخطوة {i}: {desc}"
        )

    _memory.save_context(message.from_user.id, f"تم: {plan_name}", role='assistant')
    bot.send_message(
        message.chat.id,
        f"🔱 <b>اكتملت:</b> {html_module.escape(plan_name)}",
        parse_mode="HTML"
    )


# ===== Entry Point =====
if __name__ == "__main__":
    print("🔱 NEXUM CORE is Online and Listening...")
    bot.infinity_polling()
