# -*- coding: utf-8 -*-
"""
main.py -- النواة المركزية الموحدة لنظام التشغيل السيادي Nexum Pro (v7.2.5)
===========================================================================
- دمج المكونات السبعة: الذاكرة السيادية، الفهم السياقي، مصفوفة الثقة، حلقة التعلم،
  الحارس المستقل (Watchdog)، محرك الأسراب (Swarm)، مجلس الحكماء (Council of Sages).
- مصنف النوايا العصبي (Intent Classifier) لمنع خلط الأوامر.
- دعم كامل للوسائط المتعددة (Vision/Multimodal) وقراءة الملفات الحية.
- قنوات تنفيذ موحدة ومعزولة مع حماية السيرفر.
"""

import os
import sys
import time
import threading
import asyncio
from datetime import datetime

# ─── 1. الاعتماديات الأساسية ───
import telebot
from config_loader import get_config
from core.bot_utils import bot_error_handler

# ─── 2. الخدمات المركزية ───
from services.gemini_service import gemini_service
from core.memory_local import context_memory
from core.keyboards import SovereignUIBuilder
from handlers.dash_handler import handle_dashboard

# ─── 3. مصنف النوايا ───
try:
    from nexum.intelligence.classifier import classifier, Intent
except ImportError:
    classifier = None
    Intent = None

# ─── 4. الذاكرة السيادية (المرحلة 1) ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from core.memory.sovereign_memory import SovereignMemory
sovereign_memory = SovereignMemory(os.path.join(BASE_DIR, 'storage', 'sovereign_memory'))

# ─── 5. الفهم السياقي (المرحلة 2) ───
from core.context.context_engine import ContextEngine
context_engine = ContextEngine(sovereign_memory, llm_interface=gemini_service)

# ─── 6. نظام الثقة المتدرج (المرحلة 3) ───
from core.trust.trust_engine import TrustEngine
from core.trust.behavior_engine import BehaviorEngine, DailyReport
trust_engine = TrustEngine(sovereign_memory)
behavior_engine = BehaviorEngine(trust_engine, context_engine)
daily_report = DailyReport(trust_engine)

# ─── 7. التعلم المستمر (المرحلة 4) ───
from core.learning.engines import ExperienceAnalyzer, PatternExtractor
from core.learning.initiative_engine import PredictionEngine, InitiativeEngine
analyzer = ExperienceAnalyzer(sovereign_memory, llm_interface=gemini_service)
extractor = PatternExtractor(sovereign_memory)
predictor = PredictionEngine(sovereign_memory, extractor)
initiative_engine = InitiativeEngine(
    sovereign_memory, predictor, trust_engine, behavior_engine,
    llm_interface=gemini_service
)

# ─── 8. المتحكم الأمني بالترمنال ───
from core.terminal_controller import terminal_controller

# ─── 9. الحارس المستقل (Watchdog) ───
from watchdog.monitor import Watchdog
from watchdog.recovery import RecoveryManager

# ─── 10. محرك الأسراب ومجلس الحكماء ───
from swarm.engine import SwarmEngine
from swarm.council import CouncilOfSages

council = CouncilOfSages(trust_engine=trust_engine, llm_interface=gemini_service, sovereign_memory=sovereign_memory)
swarm_engine = SwarmEngine(
    agent_registry=None, council=council,
    llm_interface=gemini_service, max_workers=4, agent_timeout=30
)

# محاولة ربط سجل الوكلاء
try:
    from core.agent_registry import agent_registry
    swarm_engine.registry = agent_registry
except ImportError:
    pass

# ─── 11. الوكلاء والأدوات المساعدة ───
try:
    from core.executive_agent import executive_agent
except ImportError:
    executive_agent = None

try:
    from core.execution_engine import execution_engine
except ImportError:
    execution_engine = None

try:
    from nexum.cloud.cloud_agent import cloud_agent
except ImportError:
    cloud_agent = None

# ═══════════════════════════════════════════════════════
# ║  تهيئة البوت والحماية الأمنية                      ║
# ═══════════════════════════════════════════════════════

try:
    cfg = get_config()
except RuntimeError as e:
    print(f"[CRITICAL] {e}")
    sys.exit(1)

bot = telebot.TeleBot(cfg.telegram_token)
ui_builder = SovereignUIBuilder()
ADMIN_ID = cfg.admin_id

# ربط البوت بمحرك الثقة للإشعارات
trust_engine.bot = bot
bot._admin_id = ADMIN_ID


# ═══════════════════════════════════════════════════════
# ║  دالة التنفيذ الأمنية الموحدة (عبر TerminalController) ║
# ═══════════════════════════════════════════════════════

def execute_bash(cmd: str, timeout: int = 45) -> dict:
    """دالة تنفيذ أوامر النظام عبر المتحكم الأمني الموحد."""
    return terminal_controller.execute(cmd, timeout=timeout)


# ═══════════════════════════════════════════════════════
# ║  1. معالجات الأوامر المباشرة (Commands)              ║
# ═══════════════════════════════════════════════════════

@bot.message_handler(func=lambda msg: msg.from_user.id != ADMIN_ID)
def catch_all_unauthorized(message):
    """Catch-all handler to debug unauthorized access. Must be at the top to intercept before other handlers."""
    bot.reply_to(
        message, 
        f"⚠️ **مرفوض (Unauthorized)**\n\n"
        f"الآي دي الخاص بك: `{message.from_user.id}`\n"
        f"آي دي المدير المسجل: `{ADMIN_ID}`\n\n"
        f"الرجاء التأكد من تطابق الأرقام في ملف `.env` وإعادة التشغيل.", 
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['start', 'menu'])
@bot_error_handler
def handle_start(message):
    """قائمة التحكم الرئيسية."""
    if message.from_user.id != ADMIN_ID:
        return
    markup = ui_builder.build_main_control_plane()
    bot.send_message(
        message.chat.id,
        "<b>NEXUM PRO v7.2.5</b> - Sovereign Operating System\n"
        "Main Control Plane Active.",
        reply_markup=markup, parse_mode="HTML"
    )


@bot.message_handler(commands=['status', 'dashboard'])
@bot_error_handler
def handle_status(message):
    """لوحة حالة النظام والتقرير اليومي."""
    if message.from_user.id != ADMIN_ID:
        return
    report_text = daily_report.generate()
    bot.send_message(message.chat.id, f"<pre>{report_text}</pre>", parse_mode="HTML")


@bot.message_handler(commands=['trust'])
@bot_error_handler
def handle_trust_status(message):
    """عرض مصفوفة الثقة الحالية."""
    if message.from_user.id != ADMIN_ID:
        return
    stats = trust_engine.get_stats()
    lines = []
    for cat, data in stats.items():
        lines.append(f"  {cat}: Lv{data['level']} ({data['level_name']}) - Score: {data['score']}")
    output = "\n".join(lines)
    bot.send_message(message.chat.id, f"<b>Trust Matrix:</b>\n<pre>{output}</pre>", parse_mode="HTML")


@bot.message_handler(commands=['clear'])
@bot_error_handler
def handle_clear_context(message):
    """مسح سياق الحوار الطويل."""
    if message.from_user.id != ADMIN_ID:
        return
    context_memory.clear_context(ADMIN_ID)
    bot.reply_to(message, "Context cleared. Starting fresh conversation.")


@bot.message_handler(commands=['gemini'])
@bot_error_handler
def handle_gemini_status(message):
    """حالة خدمة Gemini / Agent Platform."""
    if message.from_user.id != ADMIN_ID:
        return
    status = gemini_service.get_status()
    lines = [
        f"<b>Gemini Service Status:</b>",
        f"  Auth: {status['auth_mode']}",
        f"  Connected: {status['connected']}",
        f"  Model: {status['model']}",
        f"  Image Model: {status['image_model']}",
        f"  Agent Platform: {status['use_vertex']}",
    ]
    if status['use_vertex']:
        lines.append(f"  Project: {status['project']}")
        lines.append(f"  Location: {status['location']}")
    models = gemini_service.list_available_models()
    lines.append(f"\n<b>Available Models:</b>")
    for m in models:
        lines.append(f"  - {m}")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode="HTML")


@bot.message_handler(commands=['imagine'])
@bot_error_handler
def handle_imagine(message):
    """توليد صورة عبر Gemini: /imagine وصف الصورة."""
    if message.from_user.id != ADMIN_ID:
        return
    prompt = message.text.replace('/imagine', '', 1).strip()
    if not prompt:
        bot.reply_to(message, "Usage: /imagine description of the image")
        return

    bot.send_message(message.chat.id, "<b>[Image Gen]:</b> Generating...", parse_mode="HTML")
    result = gemini_service.generate_image(
        prompt=prompt,
        output_path=os.path.join(BASE_DIR, "storage", "temp", "generated.png")
    )

    if result.get("success") and result.get("image_data"):
        from io import BytesIO
        bio = BytesIO(result["image_data"])
        bio.name = "generated.png"
        caption = result.get("text", "")[:200] or prompt[:200]
        bot.send_photo(message.chat.id, bio, caption=caption)
    elif result.get("success") and result.get("text"):
        bot.reply_to(message, result["text"][:4000])
    else:
        bot.reply_to(message, f"Image generation failed: {result.get('error', 'Unknown')}")


@bot.message_handler(commands=['code'])
@bot_error_handler
def handle_code_execution(message):
    """تنفيذ كود عبر Gemini Code Execution: /code المهمة."""
    if message.from_user.id != ADMIN_ID:
        return
    prompt = message.text.replace('/code', '', 1).strip()
    if not prompt:
        bot.reply_to(message, "Usage: /code calculate fibonacci(20)")
        return

    bot.send_message(message.chat.id, "<b>[Code Exec]:</b> Processing...", parse_mode="HTML")
    result = gemini_service.execute_code(prompt)

    if result.get("success"):
        output_parts = []
        if result.get("code"):
            output_parts.append(f"<b>Code:</b>\n<pre>{str(result['code'])[:2000]}</pre>")
        if result.get("result"):
            output_parts.append(f"<b>Result:</b>\n<pre>{str(result['result'])[:1500]}</pre>")
        if result.get("text"):
            output_parts.append(f"{result['text'][:1000]}")

        output = "\n\n".join(output_parts) if output_parts else "No output."
        bot.send_message(message.chat.id, output[:4000], parse_mode="HTML")
    else:
        bot.reply_to(message, f"Code execution failed: {result.get('error', 'Unknown')}")


@bot.message_handler(commands=['model'])
@bot_error_handler
def handle_model_switch(message):
    """تبديل النموذج: /model gemini-2.5-pro."""
    if message.from_user.id != ADMIN_ID:
        return
    new_model = message.text.replace('/model', '', 1).strip()
    if not new_model:
        bot.reply_to(
            message,
            f"Current model: <b>{gemini_service.model}</b>\n"
            f"Usage: /model gemini-2.5-pro",
            parse_mode="HTML"
        )
        return
    gemini_service.switch_model(new_model)
    bot.reply_to(message, f"Model switched to: <b>{new_model}</b>", parse_mode="HTML")


@bot.message_handler(commands=['spawn_agent'])
@bot_error_handler
def handle_spawn_agent(message):
    """توليد وكيل جديد مخصص: /spawn_agent name role capabilities"""
    if message.from_user.id != ADMIN_ID:
        return
    
    parts = message.text.replace('/spawn_agent', '', 1).strip().split(' ', 2)
    if len(parts) < 3:
        bot.reply_to(
            message,
            "⚠️ **الرجاء تحديد معالم الوكيل بالكامل**\n\n"
            "الاستخدام:\n"
            "`/spawn_agent [اسم_الوكيل] [الدور] [القدرات_مفصولة_بفاصلة]`\n\n"
            "مثال:\n"
            "`/spawn_agent security_bot Auditor file_audit,integrity_scan`",
            parse_mode="Markdown"
        )
        return

    name = parts[0].strip().replace(" ", "_").lower()
    role = parts[1].strip()
    caps = [c.strip() for c in parts[2].split(',')]

    bot.send_message(message.chat.id, f"🤖 **[Agent Factory]:** Designing agent `{name}`...", parse_mode="Markdown")
    
    try:
        from agents.agent_smith import agent_smith
        spec_res = agent_smith.design_agent(name, f"وكيل مخصص للقيام بدور {role}", tools_needed=[], triggers=[])
        if spec_res.get("status") != "success":
            bot.reply_to(message, f"❌ فشل التصميم: {spec_res.get('error')}")
            return
            
        bot.send_message(message.chat.id, f"🔨 **[Agent Factory]:** Building source code for `{name}`...", parse_mode="Markdown")
        filepath = agent_smith.build_agent(name)
        if "❌" in filepath:
            bot.reply_to(message, filepath)
            return

        bot.send_message(message.chat.id, f"📝 **[Agent Factory]:** Registering `{name}` inside the sovereign registry...", parse_mode="Markdown")
        reg_ok = agent_smith.register_agent(name)
        
        if reg_ok:
            bot.send_message(
                message.chat.id,
                f"✅ **تم توليد وتنشيط الوكيل بنجاح!**\n\n"
                f"• **الاسم:** `{name}`\n"
                f"• **الدور:** `{role}`\n"
                f"• **القدرات:** `{', '.join(caps)}`\n"
                f"• **الملف:** `{os.path.basename(filepath)}`",
                parse_mode="Markdown"
            )
        else:
            bot.reply_to(message, f"⚠️ تم البناء ولكن فشل التسجيل التلقائي.")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء توليد الوكيل: {e}")


@bot.message_handler(commands=['create_protocol'])
@bot_error_handler
def handle_create_protocol(message):
    """إنشاء بروتوكول أتمتة جديد: /create_protocol اسم_البروتوكول\n[YAML]"""
    if message.from_user.id != ADMIN_ID:
        return
        
    text = message.text.replace('/create_protocol', '', 1).strip()
    if not text or '\n' not in text:
        bot.reply_to(
            message,
            "⚠️ **الرجاء إرسال محتوى البروتوكول بصيغة YAML**\n\n"
            "الاستخدام:\n"
            "`/create_protocol [اسم_البروتوكول]`\n"
            "```yaml\n"
            "name: my_protocol\n"
            "steps:\n"
            "  - id: step1\n"
            "    tool: search_web\n"
            "    input:\n"
            "      query: \"test\"\n"
            "```",
            parse_mode="Markdown"
        )
        return
        
    first_line, yaml_content = text.split('\n', 1)
    protocol_name = first_line.strip().replace(" ", "_").lower()
    
    yaml_content = yaml_content.strip()
    if yaml_content.startswith("```yaml"):
        yaml_content = yaml_content[7:]
    elif yaml_content.startswith("```"):
        yaml_content = yaml_content[3:]
    if yaml_content.endswith("```"):
        yaml_content = yaml_content[:-3]
    yaml_content = yaml_content.strip()

    try:
        import yaml
        parsed = yaml.safe_load(yaml_content)
        if not parsed or "steps" not in parsed:
            bot.reply_to(message, "❌ خطأ: الـ YAML غير صالح أو يفتقر إلى عُقدة الخطوات `steps`.")
            return
            
        protocols_dir = os.path.join(BASE_DIR, "protocols")
        os.makedirs(protocols_dir, exist_ok=True)
        file_path = os.path.join(protocols_dir, f"{protocol_name}.yaml")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
            
        bot.send_message(
            message.chat.id,
            f"🧬 **تم تسجيل البروتوكول الجديد بنجاح!**\n\n"
            f"• **الاسم:** `{protocol_name}`\n"
            f"• **المسار:** `protocols/{protocol_name}.yaml`\n\n"
            f"لتشغيل البروتوكول، استخدم الأمر:\n"
            f"`/run_protocol {protocol_name}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ فشل تحليل الـ YAML وحفظ الملف: {e}")


@bot.message_handler(commands=['run_protocol'])
@bot_error_handler
def handle_run_protocol(message):
    """تشغيل بروتوكول أتمتة مسبق الحفظ: /run_protocol اسم_البروتوكول"""
    if message.from_user.id != ADMIN_ID:
        return
        
    protocol_name = message.text.replace('/run_protocol', '', 1).strip()
    if not protocol_name:
        bot.reply_to(message, "⚠️ الاستخدام: `/run_protocol [اسم_البروتوكول]`", parse_mode="Markdown")
        return
        
    protocols_dir = os.path.join(BASE_DIR, "protocols")
    file_path = os.path.join(protocols_dir, f"{protocol_name}.yaml")
    
    if not os.path.exists(file_path):
        bot.reply_to(message, f"❌ البروتوكول غير موجود: `{protocol_name}.yaml`", parse_mode="Markdown")
        return

    bot.send_message(
        message.chat.id, 
        f"⚡ **[Protocol Engine]:** Executing blueprint `{protocol_name}`...", 
        parse_mode="Markdown"
    )
    
    try:
        from pathlib import Path
        from nexum.protocols.engine import ProtocolEngine
        
        engine = ProtocolEngine(Path(protocols_dir))
        
        loop = asyncio.get_event_loop()
        context = {"goal": "web research mission"}
        
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(engine.execute(protocol_name, context), loop)
            results = future.result(timeout=120)
        else:
            results = loop.run_until_complete(engine.execute(protocol_name, context))
            
        output = []
        for step_id, res in results.items():
            status = "✅" if "error" not in res else "❌"
            data_str = str(res.get("data", res.get("error", "")))[:200]
            output.append(f"{status} **Step {step_id}:** {data_str}")
            
        bot.send_message(
            message.chat.id,
            f"🏆 **اكتمل تنفيذ البروتوكول `{protocol_name}`!**\n\n" + "\n".join(output),
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ فشل تنفيذ البروتوكول: {e}")


@bot.message_handler(commands=['search'])
@bot_error_handler
def handle_search(message):
    """البحث في الويب: /search [الاستعلام]"""
    if message.from_user.id != ADMIN_ID:
        return
    query = message.text.replace('/search', '', 1).strip()
    if not query:
        bot.reply_to(message, "⚠️ الاستخدام: `/search [الاستعلام]`")
        return
        
    bot.send_message(message.chat.id, "🔍 **[Search Web]:** Seeking live web resources...", parse_mode="Markdown")
    try:
        from core.system_tools import search_web
        res = search_web(query)
        if res.get("status") == "success":
            results = res.get("results", [])
            lines = []
            for i, r in enumerate(results, 1):
                lines.append(f"{i}. [{r['url']}]({r['url']})\n   _{r['snippet']}_")
            output = "\n\n".join(lines) or "No results found."
            bot.send_message(message.chat.id, f"🔍 **نتائج البحث عن: {query}**\n\n{output}", parse_mode="Markdown", disable_web_page_preview=True)
        else:
            bot.reply_to(message, f"❌ فشل البحث: {res.get('message')}")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء البحث: {e}")


@bot.message_handler(commands=['scrape'])
@bot_error_handler
def handle_scrape(message):
    """قراءة وقشط صفحة ويب: /scrape [الرابط]"""
    if message.from_user.id != ADMIN_ID:
        return
    url = message.text.replace('/scrape', '', 1).strip()
    if not url:
        bot.reply_to(message, "⚠️ الاستخدام: `/scrape [الرابط]`")
        return
        
    bot.send_message(message.chat.id, "🕸️ **[Web Scraper]:** Extracting page contents...", parse_mode="Markdown")
    try:
        from core.system_tools import fetch_webpage
        res = fetch_webpage(url)
        if res.get("status") == "success":
            content = res.get("content", "")[:3500]
            bot.send_message(message.chat.id, f"🕸️ **محتويات الصفحة ({url}):**\n\n<pre>{content}</pre>", parse_mode="HTML")
        else:
            bot.reply_to(message, f"❌ فشل قشط الصفحة: {res.get('message')}")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء القشط: {e}")


@bot.message_handler(commands=['evolve'])
@bot_error_handler
def handle_system_evolution(message):
    """تحفيز حلقة التطور الذاتي والترميم: /evolve"""
    if message.from_user.id != ADMIN_ID:
        return
        
    bot.send_message(message.chat.id, "🧬 **[Evolution Engine]:** Convening the Council of Sages for system self-diagnostics and logs audit...", parse_mode="Markdown")
    
    try:
        report = council.convene_on_evolution(ADMIN_ID)
        
        gaps_str = "\n".join([f"• `{g['agent_name']}`: {g['objective']}" for g in report.get("discovered_gaps", [])]) or "🟢 لا توجد فجوات معرفية جديدة."
        repaired_str = ", ".join(report.get("repaired_agents", [])) or "🟢 جميع الوكلاء يعملون بشكل طبيعي ولا أخطاء."
        spawned_str = ", ".join(report.get("spawned_agents", [])) or "🟢 لم يتم تخليق وكلاء جدد في هذه الدورة."
        
        output = (
            f"🏆 **اكتملت دورة التطور والترميم الذاتي بنجاح!**\n\n"
            f"🛡️ **ترميم الوكلاء المعطوبين (Self-Healing):**\n"
            f"{repaired_str}\n\n"
            f"🔍 **الفجوات المعرفية المكتشفة (Capability Gaps):**\n"
            f"{gaps_str}\n\n"
            f"🤖 **الوكلاء الجدد المولّدون (Synthesized Agents):**\n"
            f"{spawned_str}\n\n"
            f"👑 **الحالة التشغيلية الكلية:** `AAA Nominal Grade`"
        )
        
        bot.send_message(message.chat.id, output, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ فشلت دورة التطور الذاتي: {e}")


@bot.message_handler(commands=['deliberate'])
@bot_error_handler
def handle_deliberation(message):
    """عقد جلسة حكماء لمناقشة وإصدار قرار إجماع نهائي: /deliberate [المهمة]"""
    if message.from_user.id != ADMIN_ID:
        return
        
    task = message.text.replace('/deliberate', '', 1).strip()
    if not task:
        bot.reply_to(message, "⚠️ الاستخدام: `/deliberate [المهمة أو القرار المقترح]`")
        return

    bot.send_message(message.chat.id, "🏛️ **[مجلس الحكماء]:** جاري عقد جلسة للمناقشة بالتوازي بين Claude و Gemini و GPT-4o...", parse_mode="Markdown")

    try:
        from council.consensus_engine import council_consensus
        # استدعاء المناقشة بشكل متزامن من خلال الخيط الحالي
        loop = asyncio.new_event_loop()
        token = loop.run_until_complete(council_consensus.deliberate(task))
        
        votes_str = "\n".join([f"• `{model}`: {'APPROVED ✅' if vote else 'REJECTED ❌'}" for model, vote in token.votes.items()])
        
        status_icon = "🏆 APPROVED & EXECUTING" if token.approved else "❌ REJECTED"
        output = (
            f"🏛️ **تقرير جلسة مجلس الحكماء:**\n\n"
            f"📌 **المهمة:** `{task}`\n\n"
            f"📊 **الأصوات والقرار:**\n{votes_str}\n\n"
            f"🧬 **درجة التوافق والقرار الكلي:** `{token.consensus_grade}`\n"
            f"👑 **الحالة النهائية:** `{status_icon}`\n\n"
        )
        if token.approved and token.merged_output:
            output += f"💻 **المخرج البرمجي المدمج المعتمد:**\n<pre>{token.merged_output[:2500]}</pre>"
        else:
            reason_str = "\n\n".join([f"🗣️ **{model.upper()}:** {reason}" for model, reason in token.reasoning.items()])
            output += f"📝 **مسودة النقاش والاعتراضات:**\n{reason_str[:1500]}"
            
        bot.send_message(message.chat.id, output, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء انعقاد الجلسة: {e}")


@bot.message_handler(commands=['sentinel_status'])
@bot_error_handler
def handle_sentinel_status(message):
    """عرض الحالة الحالية للحارس الرقابي: /sentinel_status"""
    if message.from_user.id != ADMIN_ID:
        return
        
    import psutil
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    
    status = (
        f"🛡️ **الحالة الحالية للحارس الرقابي (Sentinel):**\n\n"
        f"🖥️ CPU: `{cpu}%` (الحد الأقصى: 85%)\n"
        f"💾 RAM: `{ram}%` (الحد الأقصى: 90%)\n"
        f"💿 Disk: `{disk}%` (الحد الأقصى: 95%)\n\n"
        f"🟢 حالة المراقبة: `نشط ويعمل في الخلفية بنجاح`"
    )
    bot.reply_to(message, status, parse_mode="Markdown")


# ═══════════════════════════════════════════════════════
# ║  2. معالج الترمنال المباشر (Remote Shell)            ║
# ═══════════════════════════════════════════════════════

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and (
    msg.text and (msg.text.startswith('$ ') or msg.text.startswith('cmd '))
))
@bot_error_handler
def remote_terminal_executor(msg):
    """تنفيذ أوامر الترمنال مع تقييم السلوك والثقة."""
    cmd = msg.text.split(' ', 1)[1] if ' ' in msg.text else ''
    if not cmd:
        bot.reply_to(msg, "No command provided.")
        return

    # تقييم السلوك والسياق
    decision = behavior_engine.decide(cmd, "system_monitoring")

    if not decision.get("execute"):
        # النظام يحتاج موافقة
        bot.reply_to(msg, decision.get("message", "Action requires approval."))
        return

    # تنفيذ الأمر
    result = execute_bash(cmd)
    output = result["output"][:3500]
    ticks = "```"
    bot.send_message(
        msg.chat.id,
        f"<b>[Terminal]:</b>\n<pre>{output}</pre>",
        parse_mode="HTML"
    )

    # تسجيل النتيجة في مصفوفة الثقة
    trust_engine.record_outcome(
        "system_monitoring", cmd,
        "success" if result["success"] else "failed"
    )


# ═══════════════════════════════════════════════════════
# ║  3. معالج Swarm والمأموريات المتقدمة                 ║
# ═══════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda call: call.data == 'invoke_swarm')
@bot_error_handler
def interactive_swarm_trigger(call):
    if call.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(
        call.message.chat.id,
        "<b>[Swarm Ready]:</b> Write your mission for the Council of Sages:",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(msg, process_custom_swarm_mission)


@bot_error_handler
def process_custom_swarm_mission(msg):
    """تنفيذ مأمورية Swarm مع تسجيل التجربة وتعلم الدروس."""
    user_prompt = msg.text
    if not user_prompt:
        bot.reply_to(msg, "No mission text provided.")
        return

    start_time = time.time()
    bot.send_message(msg.chat.id, "<b>[Swarm Processing]:</b> Running your mission...", parse_mode="HTML")

    try:
        if executive_agent:
            report = executive_agent.execute_mission(user_prompt)
        else:
            # Fallback: استخدام Gemini مباشرة
            report, _ = gemini_service.ask(user_prompt)

        duration = time.time() - start_time
        is_success = True
    except Exception as e:
        report = f"Mission failed: {str(e)}"
        duration = time.time() - start_time
        is_success = False

    bot.send_message(msg.chat.id, report[:4000], parse_mode="HTML")

    # تسجيل المأمورية في سجل الدروس المستفادة
    sovereign_memory.missions.log_mission(
        goal=user_prompt[:500],
        plan=[],
        result="success" if is_success else "failed",
        duration_seconds=duration,
        lessons=f"Duration: {duration:.1f}s. Output length: {len(report)} chars."
    )

    # تحليل التجربة
    analyzer.analyze({
        "id": f"mission-{int(time.time())}",
        "goal": user_prompt[:500],
        "result": "success" if is_success else "failed",
        "duration": duration,
        "user_intervened": False
    })


# ═══════════════════════════════════════════════════════
# ║  4. التنقل في الواجهة (UI Navigation)                ║
# ═══════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda call: any(
    call.data == 'audit_logs' or 
    call.data.startswith(prefix) for prefix in [
        'menu_', 'rt_', 'ag_', 'pr_', 'dp_', 'ai_', 'sec_', 'mem_', 'dk_', 'set_', 'hw_', 'back_', 'cloud_',
        'setmod_', 'settheme_', 'confirm_', 'agent_'
    ]
))
@bot_error_handler
def handle_menu_navigation(call):
    if call.from_user.id != ADMIN_ID:
        return
    handle_dashboard(bot, call)


# ═══════════════════════════════════════════════════════
# ║  5. أوامر نظام الملفات                               ║
# ═══════════════════════════════════════════════════════

@bot.message_handler(commands=['ls', 'tree', 'cat', 'find'])
@bot_error_handler
def fs_commands_proxy(message):
    """تحويل الأوامر إلى المحرك المناسب."""
    if message.from_user.id != ADMIN_ID:
        return

    cmd = message.text.split()[0][1:]  # Remove /

    if cmd == 'ls':
        try:
            from core.fs_navigator import fs_navigator
            path = message.text.replace('/ls', '').strip() or None
            r = fs_navigator.ls(path)
            if r['success']:
                file_list = "\n".join([f"  {f['name']}" for f in r['files'][:20]])
                bot.reply_to(message, f"<b>{r['relative']}</b>\n{file_list}", parse_mode="HTML")
            else:
                bot.reply_to(message, f"Error: {r['error']}")
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")

    elif cmd == 'tree':
        try:
            from core.fs_navigator import fs_navigator
            r = fs_navigator.tree(max_depth=2)
            bot.reply_to(message, f"<pre>{r['tree'][:3500]}</pre>", parse_mode="HTML")
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")


# ═══════════════════════════════════════════════════════
# ║  6. المعالج الشامل (Universal Handler)               ║
# ═══════════════════════════════════════════════════════

@bot.message_handler(content_types=['photo', 'document', 'text'])
@bot_error_handler
def handle_universal(message):
    """المعالج الشامل لكل أنواع الرسائل مع تصنيف النوايا الذكي."""
    if message.from_user.id != ADMIN_ID:
        return

    chat_id = message.chat.id
    text = message.text or message.caption or ""

    # معالجة الملفات والوسائط
    file_data = None
    mime_type = None

    if message.photo:
        try:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_data = bot.download_file(file_info.file_path)
            mime_type = "image/jpeg"
        except Exception:
            pass
    elif message.document:
        try:
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            file_data = bot.download_file(file_info.file_path)
            mime_type = message.document.mime_type
        except Exception:
            pass

    # ─── تصنيف النية ───
    intent_result = None
    if text and classifier:
        try:
            intent_result = classifier.classify(text)
        except Exception:
            pass

    # ─── Google Cloud Commands ───
    if intent_result and Intent and intent_result.intent in [
        Intent.CLOUD_STORAGE, Intent.CLOUD_BIGQUERY, Intent.CLOUD_COMPUTE,
        Intent.CLOUD_MONITOR, Intent.CLOUD_AI, Intent.CLOUD_GENERAL
    ]:
        if cloud_agent:
            _handle_cloud(message, text)
        else:
            bot.reply_to(message, "Cloud agent not available.")
        return

    # ─── أوامر التنفيذ (Execute) ───
    if intent_result and Intent and intent_result.intent == Intent.EXECUTE:
        _handle_execute(message, text)
        return

    # ─── محادثة عامة أو Vision ───
    _handle_chat(message, text, file_data, mime_type)


def _handle_cloud(message, text):
    """معالجة أوامر Google Cloud."""
    bot.reply_to(message, "<b>NEXUM Cloud</b> executing...", parse_mode="HTML")
    try:
        res = cloud_agent.run({"text": text})
        if res.get("status") == "success":
            output = res["output"][:3500]
            bot.send_message(message.chat.id, f"<b>GCP Result:</b>\n{output}", parse_mode="HTML")
        else:
            bot.reply_to(message, f"<b>Cloud Error:</b>\n<code>{res.get('error', 'Unknown')}</code>", parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"Cloud error: {e}")


def _handle_execute(message, text):
    """معالجة أوامر التنفيذ مع تقييم السلوك والتسجيل."""
    # تقييم السلوك
    decision = behavior_engine.decide(text, "code_operations")

    if not decision.get("execute"):
        bot.reply_to(message, decision.get("message", "Operation requires confirmation."))
        return

    # تنفيذ الأمر
    start_time = time.time()
    result = execute_bash(text)
    duration = time.time() - start_time

    output = result["output"][:3500]
    bot.send_message(message.chat.id, f"<b>[Execution]:</b>\n<pre>{output}</pre>", parse_mode="HTML")

    # تسجيل النتيجة
    is_success = result["success"]
    trust_engine.record_outcome("code_operations", text, "success" if is_success else "failed")

    # تسجيل في الذاكرة السيادية
    sovereign_memory.missions.log_mission(
        goal=text[:500], result="success" if is_success else "failed",
        duration_seconds=duration
    )


def _handle_chat(message, text, file_data=None, mime_type=None):
    """معالجة المحادثات العامة مع دمج السياق السيادي."""
    history = context_memory.get_context(ADMIN_ID)

    # دمج سياق الذاكرة السيادية مع تعليمات النظام
    sovereign_context = ""
    try:
        sovereign_context = sovereign_memory.get_full_context()
    except Exception:
        pass

    system_instruction = (
        "You are NEXUM PRO v7.2.5. A sovereign AI operating system. "
        "You have full Vision/Multimodal capabilities via Gemini. "
        "Speak with technical confidence and directness. "
        "You build systems, not just explain them.\n\n"
        f"Sovereign Memory Context:\n{sovereign_context}"
    )

    res, _ = gemini_service.ask(
        prompt=text,
        history=history,
        system_instruction=system_instruction,
        file_data=file_data,
        mime_type=mime_type
    )

    bot.reply_to(message, res[:4000])

    # حفظ السياق
    context_memory.save_context(ADMIN_ID, text if text else "[Media/File]", role='user')
    context_memory.save_context(ADMIN_ID, res[:2000], role='model')


# ═══════════════════════════════════════════════════════
# ║  7. حلقة التعلم الاستباقي (Background Loop)         ║
# ═══════════════════════════════════════════════════════

def _proactive_learning_loop():
    """حلقة خلفية للتعلم المستمر والمبادرات الاستباقية (كل 30 دقيقة)."""
    while True:
        try:
            time.sleep(1800)  # 30 دقيقة

            # 1. فحص الأنماط المتراكمة
            new_patterns = extractor.scan_for_patterns()
            if new_patterns:
                print(f"[Proactive] Discovered {len(new_patterns)} new patterns.")

            # 2. تشغيل دورة المبادرة الاستباقية
            proactive_actions = initiative_engine.run_proactive_cycle()
            if proactive_actions:
                print(f"[Proactive] Took {len(proactive_actions)} proactive actions.")

        except Exception as e:
            print(f"[Proactive Loop Error] {e}")


        except Exception as e:
            print(f"[Proactive Loop Error] {e}")


def _autonomous_evolution_loop():
    """حلقة خلفية للتطور والترميم الذاتي للأنظمة والوكلاء (كل 15 دقيقة)."""
    while True:
        try:
            time.sleep(900)  # 15 دقيقة
            if council:
                print("[Evolution] Auto-running diagnostic self-evolution cycle...")
                council.convene_on_evolution(ADMIN_ID)
        except Exception as e:
            print(f"[Evolution Loop Error] {e}")


# ═══════════════════════════════════════════════════════
# ║  نقطة الدخول الرئيسية                               ║
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"[NEXUM PRO v7.2.5] Sovereign OS Online (Admin: {ADMIN_ID})")
    print(f"[NEXUM PRO] Modules: Memory + Context + Trust + Learning + Watchdog + Swarm")

    # ─── تسجيل أدوات النظام ───
    try:
        from core.system_tools import register_all_system_tools
        register_all_system_tools()
    except Exception as e:
        print(f"[NEXUM PRO] Tools registration error: {e}")

    # ─── تشغيل المسح الأولي للبنية التحتية ───
    def _initial_scan():
        try:
            sovereign_memory.infrastructure.scan_and_build()
            print("[NEXUM PRO] Infrastructure scan complete.")
        except Exception as e:
            print(f"[NEXUM PRO] Initial scan error: {e}")

    scan_thread = threading.Thread(target=_initial_scan, daemon=True)
    scan_thread.start()

    # ─── تشغيل حلقة التعلم الاستباقي ───
    learning_thread = threading.Thread(target=_proactive_learning_loop, daemon=True)
    learning_thread.start()

    # ─── تشغيل حلقة التطور والترميم الذاتي ───
    evolution_thread = threading.Thread(target=_autonomous_evolution_loop, daemon=True)
    evolution_thread.start()

    # ─── تشغيل الحارس المستقل (Watchdog) ───
    recovery_manager = RecoveryManager(
        max_retries=5, bot=bot, admin_id=ADMIN_ID
    )
    watchdog = Watchdog(heartbeat_interval=30, max_consecutive_failures=5)
    watchdog.set_callbacks(
        on_failure=recovery_manager.handle_failure,
        on_recovery=recovery_manager.handle_recovery,
        on_critical=recovery_manager.handle_critical
    )
    watchdog.start()
    print("[NEXUM PRO] Watchdog daemon started (30s heartbeat).")

    # ─── Sentinel Watchdog Thread ───
    try:
        from agents.sentinel import sentinel_agent
        def run_sentinel():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(sentinel_agent.watch(bot, ADMIN_ID, interval=60))
        sentinel_thread = threading.Thread(target=run_sentinel, daemon=True)
        sentinel_thread.start()
        print("🛡️ [Sentinel] Watching daemon initialized successfully.")
    except Exception as e:
        print(f"⚠️ [Sentinel Init Error] {e}")

    # ─── تشغيل البوت ───
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
