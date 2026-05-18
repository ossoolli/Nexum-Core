import os
import sys
import telebot
from telebot import types
from dotenv import load_dotenv

sys.path.append('/home/madarmutaz/Mutaz-dev')
from core.llm_factory import llm
from agents.monitor import monitor_agent
from agents.deploy import deploy_agent

load_dotenv(dotenv_path="/home/madarmutaz/Mutaz-dev/.env")
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

class NexumInterpreter:
    """المترجم والمنسق السيادي للنظام"""
    def process_request(self, user_id, text):
        clean_text = text.lower().strip()
        
        # 1. توجيه مباشر لوكيل المراقبة والنبض الفني
        if any(word in clean_text for word in ["حالة النظام", "status", "النبض", "pulse"]):
            return monitor_agent.get_pulse_report()
            
        # 2. توجيه مباشر لوكيل النشر لـ GitHub
        if any(word in clean_text for word in ["ارفع الكود", "deploy", "push", "جيت هب", "github"]):
            return deploy_agent.deploy_updates(f"🔱 NEXUM Deployment: {text[:20]}")
            
        # 3. التحويل التلقائي للمستشار OpenAI عند رصد كلمات إصلاح كود معقدة
        if any(word in clean_text for word in ["إصلاح", "fix", "debug", "برمجة عميقة"]):
            return llm.ask_specialist(f"مهمة تطوير وإصلاح كود معقد للمايسترو: {text}")
            
        # 4. الحوار الاستراتيجي العام عبر عقل جوجل والذاكرة السياقية
        return llm.ask_gemini(user_id, text)

interpreter = NexumInterpreter()

def get_dashboard_markup():
    markup = types.InlineKeyboardMarkup()
    btn_status = types.InlineKeyboardButton("📊 حالة النظام", callback_data="status")
    btn_fix = types.InlineKeyboardButton("🛠️ إصلاح شامل", callback_data="fix_all")
    btn_upgrade = types.InlineKeyboardButton("⭐ ترقية الحساب (Stars)", callback_data="upgrade")
    markup.add(btn_status, btn_fix)
    markup.add(btn_upgrade)
    return markup

@bot.message_handler(commands=['start', 'dashboard'])
def send_dashboard(message):
    if message.from_user.id!= ADMIN_ID: return
    bot.send_message(
        message.chat.id, 
        "🔱 <b>لوحة تحكم NEXUM CORE OS</b>\nالذاكرة: نشطة\nجاهز لتلقي وتنفيذ بروتوكولات الأتمتة والتحكم بالسيرفر.", 
        reply_markup=get_dashboard_markup(), 
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.from_user.id!= ADMIN_ID: return
    bot.answer_callback_query(call.id, "جاري التنسيق مع الوكلاء...")

    if call.data == "status":
        response = interpreter.process_request(call.from_user.id, "حالة النظام")
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=get_dashboard_markup(), parse_mode="HTML")
    elif call.data == "fix_all":
        response = interpreter.process_request(call.from_user.id, "ارفع الكود")
        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=get_dashboard_markup(), parse_mode="HTML")
    elif call.data == "upgrade":
        # تفعيل الدفع بالنجوم لترقية الحساب السيادي (500 نجمة XTR) [3, 4]
        prices 
        bot.send_invoice(
            call.message.chat.id,
            title="Sovereign Subscription Upgrade",
            description="ترقية حسابك لتفعيل وكلاء الذكاء الاصطناعي الفوقيين وبناء الويب الفوري داخل بيئات العمل المعزولة.",
            invoice_payload="sovereign_upgrade_payload",
            provider_token="", # تترك فارغة لعملة XTR
            currency="XTR",
            prices=prices
        )

@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_payment_success(message):
    payment = message.successful_payment
    bot.send_message(
        message.chat.id, 
        f"✅ <b>تمت المصادقة المالية بنجاح!</b>\nالمبلغ: {payment.total_amount} ⭐\nمعرف العملية: <code>{payment.telegram_payment_charge_id}</code>"
    )

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def handle_text(message):
    status_msg = bot.reply_to(message, "⏳ جاري المعالجة سيادياً...")
    try:
        response = interpreter.process_request(message.from_user.id, message.text)
        bot.edit_message_text(response, message.chat.id, status_msg.message_id, parse_mode="HTML")
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ في النظام: {str(e)}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    print("🔱 NEXUM CORE is Online and Listening...")
    bot.infinity_polling()

# ===== God Mode Handler =====
pending_commands = {}  # انتظار تأكيد الأوامر الخطرة

@bot.message_handler(commands=['run'])
def run_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    cmd = message.text.replace('/run ', '', 1).strip()
    if not cmd:
        bot.reply_to(message, "الاستخدام: <code>/run <الأمر></code>", parse_mode="HTML")
        return

    result = executor.execute(cmd)

    if result['status'] == 'blocked':
        bot.reply_to(message, result['output'])

    elif result['status'] == 'confirm':
        # احفظ الأمر وانتظر تأكيد
        pending_commands[message.from_user.id] = cmd
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ نعم، نفّذ", callback_data="confirm_run"),
            types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_run")
        )
        bot.reply_to(
            message,
            f"⚠️ <b>أمر خطر، تأكيد مطلوب:</b>\n`<code><code>\n{cmd}\n</code></code><code>",
            reply_markup=markup, parse_mode="HTML"
        )

    else:
        response = f"</code><code><code>\n{result['output']}\n</code></code><code>"
        bot.reply_to(message, response, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data in ["confirm_run", "cancel_run"])
def handle_confirm(call):
    if call.from_user.id != ADMIN_ID:
        return
    if call.data == "confirm_run":
        cmd = pending_commands.pop(call.from_user.id, None)
        if cmd:
            result = executor.execute(cmd, force=True)
            bot.send_message(
                call.message.chat.id,
                f"✅ تم التنفيذ:\n</code><code><code>\n{result['output']}\n</code></code><code>",
                parse_mode="HTML"
            )
    else:
        pending_commands.pop(call.from_user.id, None)
        bot.answer_callback_query(call.id, "تم الإلغاء.")

# ===== AI Planner Integration =====
import sys
sys.path.append('/home/madarmutaz/Mutaz-dev')
from core.planner import AIPlanner
from core.memory_local import LongTermMemory
from services.gemini_service import GeminiService

_gemini_svc = GeminiService()
_planner    = AIPlanner(_gemini_svc)
_memory     = LongTermMemory('/home/madarmutaz/Mutaz-dev/storage/memory.json')

@bot.message_handler(commands=['plan'])
def handle_plan(message):
    if message.from_user.id != ADMIN_ID:
        return

    goal = message.text.replace('/plan ', '', 1).strip()
    if not goal:
        bot.reply_to(message, "الاستخدام: </code>/plan <الهدف><code>\nمثال: </code>/plan ثبّت Docker وشغّله<code>")
        return

    status_msg = bot.reply_to(message, "🧠 <b>جاري التخطيط الذكي...</b>", parse_mode="HTML")

    # حفظ الطلب في الذاكرة
    _memory.save_context(message.from_user.id, goal, role='user')

    plan = _planner.create_plan(goal)
    if "error" in plan:
        bot.edit_message_text(
            f"❌ فشل التخطيط: {plan['error']}",
            message.chat.id, status_msg.message_id
        )
        return

    steps = plan.get('steps', [])
    plan_name = plan.get('plan_name', 'خطة تنفيذية')

    bot.edit_message_text(
        f"📋 <b>{plan_name}</b>\n🔢 عدد الخطوات: {len(steps)}",
        message.chat.id, status_msg.message_id,
        parse_mode="HTML"
    )

    # تنفيذ كل خطوة
    for i, step in enumerate(steps, 1):
        cmd  = step.get('command', '')
        desc = step.get('description', '')

        bot.send_message(message.chat.id, f"⏳ <b>{i}/{len(steps)}</b> {desc}", parse_mode="HTML")

        result = executor.execute(cmd)

        if result['status'] == 'confirm':
            # أمر خطر - اطلب تأكيداً
            pending_commands[message.from_user.id] = cmd
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ نفّذ", callback_data="confirm_run"),
                types.InlineKeyboardButton("❌ تخطَّ", callback_data="cancel_run")
            )
            bot.send_message(
                message.chat.id,
                f"⚠️ أمر حساس:\n</code>{cmd}<code>",
                reply_markup=markup, parse_mode="HTML"
            )
            continue

        elif result['status'] == 'failed':
            # التصحيح الذاتي
            bot.send_message(message.chat.id, "⚠️ تعثّر — أبحث عن حل بديل...")
            correction = _planner.create_correction_plan(goal, cmd, result['output'])
            if "fixed_command" in correction:
                fixed = correction['fixed_command']
                bot.send_message(
                    message.chat.id,
                    f"🔧 {correction.get('reason','تصحيح تلقائي')}\n</code>{fixed}<code>",
                    parse_mode="HTML"
                )
                result = executor.execute(fixed, force=True)

        icon = "✅" if result['status'] == 'success' else "❌"
        bot.send_message(
            message.chat.id,
            f"{icon} <pre>{result['output'][:3000]}</pre>",
            parse_mode="HTML"
        )

    # حفظ النتيجة في الذاكرة
    _memory.save_context(message.from_user.id, f"تم تنفيذ: {plan_name}", role='assistant')
    bot.send_message(message.chat.id, f"🔱 <b>اكتملت الخطة:</b> {plan_name}", parse_mode="HTML")

# ===== AI Planner Integration =====
import sys
sys.path.append('/home/madarmutaz/Mutaz-dev')
from core.planner import AIPlanner
from core.memory_local import LongTermMemory
from services.gemini_service import GeminiService

_gemini_svc = GeminiService()
_planner    = AIPlanner(_gemini_svc)
_memory     = LongTermMemory('/home/madarmutaz/Mutaz-dev/storage/memory.json')

@bot.message_handler(commands=['plan'])
def handle_plan(message):
    if message.from_user.id != ADMIN_ID:
        return

    goal = message.text.replace('/plan ', '', 1).strip()
    if not goal:
        bot.reply_to(message, "الاستخدام: </code>/plan <الهدف><code>\nمثال: </code>/plan ثبّت Docker وشغّله<code>")
        return

    status_msg = bot.reply_to(message, "🧠 <b>جاري التخطيط الذكي...</b>", parse_mode="HTML")

    # حفظ الطلب في الذاكرة
    _memory.save_context(message.from_user.id, goal, role='user')

    plan = _planner.create_plan(goal)
    if "error" in plan:
        bot.edit_message_text(
            f"❌ فشل التخطيط: {plan['error']}",
            message.chat.id, status_msg.message_id
        )
        return

    steps = plan.get('steps', [])
    plan_name = plan.get('plan_name', 'خطة تنفيذية')

    bot.edit_message_text(
        f"📋 <b>{plan_name}</b>\n🔢 عدد الخطوات: {len(steps)}",
        message.chat.id, status_msg.message_id,
        parse_mode="HTML"
    )

    # تنفيذ كل خطوة
    for i, step in enumerate(steps, 1):
        cmd  = step.get('command', '')
        desc = step.get('description', '')

        bot.send_message(message.chat.id, f"⏳ <b>{i}/{len(steps)}</b> {desc}", parse_mode="HTML")

        result = executor.execute(cmd)

        if result['status'] == 'confirm':
            # أمر خطر - اطلب تأكيداً
            pending_commands[message.from_user.id] = cmd
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ نفّذ", callback_data="confirm_run"),
                types.InlineKeyboardButton("❌ تخطَّ", callback_data="cancel_run")
            )
            bot.send_message(
                message.chat.id,
                f"⚠️ أمر حساس:\n</code>{cmd}<code>",
                reply_markup=markup, parse_mode="HTML"
            )
            continue

        elif result['status'] == 'failed':
            # التصحيح الذاتي
            bot.send_message(message.chat.id, "⚠️ تعثّر — أبحث عن حل بديل...")
            correction = _planner.create_correction_plan(goal, cmd, result['output'])
            if "fixed_command" in correction:
                fixed = correction['fixed_command']
                bot.send_message(
                    message.chat.id,
                    f"🔧 {correction.get('reason','تصحيح تلقائي')}\n</code>{fixed}`",
                    parse_mode="HTML"
                )
                result = executor.execute(fixed, force=True)

        icon = "✅" if result['status'] == 'success' else "❌"
        bot.send_message(
            message.chat.id,
            f"{icon} <pre>{result['output'][:3000]}</pre>",
            parse_mode="HTML"
        )

    # حفظ النتيجة في الذاكرة
    _memory.save_context(message.from_user.id, f"تم تنفيذ: {plan_name}", role='assistant')
    bot.send_message(message.chat.id, f"🔱 <b>اكتملت الخطة:</b> {plan_name}", parse_mode="HTML")

# ===== Override handle_plan بنسخة آمنة =====
from core.safe_sender import send_terminal_output, safe_reply

@bot.message_handler(commands=['planx'])
def handle_plan_safe(message):
    """نسخة آمنة من /plan مع إصلاح HTML"""
    if message.from_user.id != ADMIN_ID:
        return

    goal = message.text.replace('/planx ', '', 1).strip()
    if not goal:
        bot.reply_to(message, "الاستخدام: <code>/planx ثبّت Docker</code>", parse_mode="HTML")
        return

    status_msg = bot.reply_to(message, "🧠 جاري التخطيط الذكي...")

    _memory.save_context(message.from_user.id, goal, role='user')
    plan = _planner.create_plan(goal)

    if "error" in plan:
        bot.edit_message_text(
            f"❌ فشل التخطيط: {plan['error']}",
            message.chat.id, status_msg.message_id
        )
        return

    steps    = plan.get('steps', [])
    plan_name = plan.get('plan_name', 'خطة تنفيذية')
    total    = len(steps)

    bot.edit_message_text(
        f"📋 <b>{plan_name}</b>\n🔢 عدد الخطوات: {total}",
        message.chat.id, status_msg.message_id,
        parse_mode="HTML"
    )

    for i, step in enumerate(steps, 1):
        cmd  = step.get('command', '')
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
                f"⚠️ أمر حساس:\n<code>{html_module.escape(cmd)}</code>",
                reply_markup=markup, parse_mode="HTML"
            )
            continue

        if result['status'] == 'failed':
            bot.send_message(message.chat.id, "⚠️ تعثّر — أبحث عن حل بديل...")
            correction = _planner.create_correction_plan(goal, cmd, result['output'])
            if "fixed_command" in correction:
                fixed = correction['fixed_command']
                bot.send_message(
                    message.chat.id,
                    f"🔧 <b>{html_module.escape(correction.get('reason','تصحيح'))}</b>\n<code>{html_module.escape(fixed)}</code>",
                    parse_mode="HTML"
                )
                result = executor.execute(fixed, force=True)

        send_terminal_output(
            bot, message.chat.id,
            result['status'], result['output'],
            f"الخطوة {i}: {desc}"
        )

    _memory.save_context(message.from_user.id, f"تم: {plan_name}", role='assistant')
    bot.send_message(
        message.chat.id,
        f"🔱 <b>اكتملت الخطة:</b> {html_module.escape(plan_name)}",
        parse_mode="HTML"
    )

# ===== Docker Status Command =====
@bot.message_handler(commands=['docker'])
def handle_docker(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) == 1:
        # حالة الحاويات
        report = deploy_agent.docker_status()
    elif args[1] == 'logs' and len(args) >= 3:
        report = deploy_agent.docker_logs(args[2])
    else:
        report = "الاستخدام:\n/docker — حالة الحاويات\n/docker logs <اسم_الحاوية>"
    
    try:
        bot.reply_to(message, report, parse_mode="HTML")
    except Exception:
        bot.reply_to(message, report.replace('<','').replace('>',''))

# ===== تجاوز handle_text القديم بنسخة ذكية =====
bot.message_handlers.clear()  # مسح الـ handlers القديمة

@bot.message_handler(commands=['start', 'dashboard'])
def send_dashboard_new(message):
    if message.from_user.id != ADMIN_ID: return
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
    if message.from_user.id != ADMIN_ID: return
    report = monitor_agent.get_pulse_report()
    try:
        bot.reply_to(message, report, parse_mode="HTML")
    except:
        bot.reply_to(message, report.replace('<','').replace('>',''))

@bot.message_handler(commands=['run'])
def handle_run(message):
    if message.from_user.id != ADMIN_ID: return
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
        bot.reply_to(message, f"⚠️ أمر حساس:\n<code>{cmd}</code>",
                    reply_markup=markup, parse_mode="HTML")
        return
    import html as _html
    out = _html.escape(str(result.get('output', '')))
    icon = "✅" if result['status'] == 'success' else "❌"
    try:
        bot.reply_to(message, f"{icon}\n<pre>{out[:3500]}</pre>", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{icon}\n{str(result.get('output',''))[:3500]}")

@bot.message_handler(commands=['planx'])
def handle_planx(message):
    if message.from_user.id != ADMIN_ID: return
    goal = message.text.replace('/planx', '', 1).strip()
    if not goal:
        bot.reply_to(message, "الاستخدام: <code>/planx هدف</code>", parse_mode="HTML")
        return
    _run_plan(message, goal)

@bot.message_handler(commands=['docker'])
def handle_docker_new(message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) == 1:
        report = deploy_agent.docker_status()
    elif len(args) >= 3 and args[1] == 'logs':
        report = deploy_agent.docker_logs(args[2])
    else:
        report = "الاستخدام:\n<code>/docker</code>\n<code>/docker logs اسم_الحاوية</code>"
    try:
        bot.reply_to(message, report, parse_mode="HTML")
    except:
        bot.reply_to(message, report.replace('<','').replace('>',''))

# كلمات تدل على نية تنفيذية
EXEC_KEYWORDS = [
    'ثبت','install','تثبيت','شغل','run','ارفع','deploy','احذف',
    'remove','أنشئ','create','أوقف','stop','أعد تشغيل','restart',
    'حدّث','update','upgrade','نفذ','execute','ابنِ','build'
]

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def handle_smart(message):
    text = message.text.strip()
    text_lower = text.lower()

    # هل هي نية تنفيذية؟
    is_exec = any(kw in text_lower for kw in EXEC_KEYWORDS)

    if is_exec:
        # توجيه للمخطط الذكي مباشرة
        _run_plan(message, text)
    else:
        # شات عادي عبر Gemini
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            response = _gemini_svc.ask(text)
            bot.reply_to(message, response)
        except Exception as e:
            bot.reply_to(message, f"❌ {str(e)}")

def _run_plan(message, goal):
    import html as _html
    status_msg = bot.reply_to(message, "🧠 جاري التخطيط...")
    _memory.save_context(message.from_user.id, goal, role='user')
    plan = _planner.create_plan(goal)

    if "error" in plan:
        bot.edit_message_text(f"❌ {plan['error']}",
                             message.chat.id, status_msg.message_id)
        return

    steps = plan.get('steps', [])
    plan_name = plan.get('plan_name', 'خطة تنفيذية')
    total = len(steps)

    bot.edit_message_text(
        f"📋 <b>{_html.escape(plan_name)}</b>\n🔢 الخطوات: {total}",
        message.chat.id, status_msg.message_id, parse_mode="HTML"
    )

    for i, step in enumerate(steps, 1):
        cmd  = step.get('command', '')
        desc = step.get('description', '')
        bot.send_message(message.chat.id,
                        f"⏳ <b>{i}/{total}</b> — {_html.escape(desc)}",
                        parse_mode="HTML")
        result = executor.execute(cmd)

        if result['status'] == 'confirm':
            pending_commands[message.from_user.id] = cmd
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ نفّذ", callback_data="confirm_run"),
                types.InlineKeyboardButton("❌ تخطَّ", callback_data="cancel_run")
            )
            bot.send_message(message.chat.id,
                           f"⚠️ <code>{_html.escape(cmd)}</code>",
                           reply_markup=markup, parse_mode="HTML")
            continue

        if result['status'] == 'failed':
            bot.send_message(message.chat.id, "⚠️ تعثّر — أبحث عن حل...")
            correction = _planner.create_correction_plan(goal, cmd, result['output'])
            if "fixed_command" in correction:
                fixed = correction['fixed_command']
                result = executor.execute(fixed, force=True)

        out  = _html.escape(str(result.get('output', '')))
        icon = "✅" if result['status'] == 'success' else "❌"
        try:
            bot.send_message(message.chat.id,
                           f"{icon} <pre>{out[:3000]}</pre>",
                           parse_mode="HTML")
        except:
            bot.send_message(message.chat.id,
                           f"{icon} {str(result.get('output',''))[:3000]}")

    _memory.save_context(message.from_user.id, f"تم: {plan_name}", role='assistant')
    bot.send_message(message.chat.id,
                    f"🔱 <b>اكتملت:</b> {_html.escape(plan_name)}",
                    parse_mode="HTML")
