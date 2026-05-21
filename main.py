# -*- coding: utf-8 -*-
"""
🔱 NEXUM CORE OS v7.5.0 — The Sovereign Architect
================================================
إصدار التحول الجراحي الكامل:
- محرك التنفيذ الحي (ExecutionEngine) المعتمد على الخطوات.
- وكيل الملفات (FileAgent) ووكيل الـ Shell الحقيقي.
- بروتوكول التحكم في الـ Sub-Bots.
- البث الحي للعمليات (Streaming Reports).
"""

import os
import sys
import time
import logging
import re
from datetime import datetime

# 1. ─── الطبقة المعمارية (Nexum Package) ───
from nexum.config import config
from nexum.logger import logger
from nexum.security.audit import log_audit, AuditEvent
from nexum.intelligence.classifier import classifier, Intent
from nexum.memory.summarizer import summarizer

# 2. ─── طبقة الخدمات والمهمات (Core Engines) ───
import telebot
from telebot import types
from services.gemini_service import gemini_service
from core.memory_local import context_memory
from core.execution_engine import execution_engine
from core.file_agent import file_agent
from core.inter_bot_protocol import inter_bot_protocol
from core.keyboards import SovereignUIBuilder

# --- تهيئة البوت والواجهة ---
bot = telebot.TeleBot(config.telegram_token)
ui_builder = SovereignUIBuilder()
ADMIN_ID = config.admin_id

# ربط المحرك بالذكاء
execution_engine.set_gemini(gemini_service)

# ╔══════════════════════════════════════════╗
# ║        1. معالجات الأوامر (Commanders)   ║
# ╚══════════════════════════════════════════╝

@bot.message_handler(commands=['start', 'dashboard'])
def send_welcome(message):
    markup = ui_builder.build_main_control_plane()
    bot.send_message(
        message.chat.id,
        "🔱 <b>NEXUM CORE OS v7.5.0</b>\n"
        "━━━━━━━━━━━━━━\n"
        "🧠 الحالة: 🟢 بكامل الوعي التنفيذي\n"
        "📂 منطقة العمل: <code>/workspace</code>\n"
        "🛡️ النمط: سيادي (Architect Mode)\n"
        "━━━━━━━━━━━━━━\n"
        "استخدم <code>/workspace</code> لعرض الملفات أو <code>/bots</code> لإدارة الوحدات الفرعية.",
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.message_handler(commands=['workspace'])
def show_workspace(message):
    if message.from_user.id != ADMIN_ID: return
    result = file_agent.list_workspace()
    if not result["files"]:
        bot.reply_to(message, "📁 Workspace فارغ حالياً.")
        return
    lines = [f"📁 <b>Workspace</b> — {result['count']} ملف\n━━━━━━━━━━━━━━"]
    for f in result["files"][:20]:
        lines.append(f"• <code>{f['name']}</code> — {f['size_kb']}KB — {f['modified']}")
    bot.reply_to(message, "\n".join(lines), parse_mode="HTML")

@bot.message_handler(commands=['bots'])
def show_bots(message):
    if message.from_user.id != ADMIN_ID: return
    bots = inter_bot_protocol.list_bots()
    if not bots:
        bot.reply_to(message, "🤖 لا يوجد sub-bots مسجّلون حالياً.")
        return
    lines = [f"🤖 <b>Sub-Bots</b> — {len(bots)} بوت\n━━━━━━━━━━━━━━"]
    for b in bots:
        icon = "🟢" if b["status"] == "running" else "🔴"
        lines.append(f"{icon} <b>{b['name']}</b> | PID: {b.get('pid', '—')}")
    bot.reply_to(message, "\n".join(lines), parse_mode="HTML")

# ─── أمر /ls — عرض محتويات مجلد ───
@bot.message_handler(commands=['ls'])
def cmd_ls(message):
    if message.from_user.id != ADMIN_ID: return
    from core.fs_navigator import fs_navigator
    path = message.text.replace('/ls', '').strip() or None
    result = fs_navigator.ls(path)
    if not result['success']:
        bot.reply_to(message, f"❌ {result['error']}")
        return
    lines = [f"📁 <b>{result['relative']}</b> ({result['total_dirs']} مجلد | {result['total_files']} ملف)\n"]
    for d in result['dirs'][:10]:
        lines.append(f"📁 <code>{d['name']}/</code> [{d.get('children_count','?')} عنصر]")
    for f in result['files'][:15]:
        lines.append(f"📄 <code>{f['name']}</code> {f['size_kb']}KB — {f['modified']}")
    if result['total_files'] > 15:
        lines.append(f"<i>... و{result['total_files']-15} ملف آخر</i>")
    bot.reply_to(message, "\n".join(lines), parse_mode="HTML")

# ─── أمر /tree — عرض هيكل هرمي ───
@bot.message_handler(commands=['tree'])
def cmd_tree(message):
    if message.from_user.id != ADMIN_ID: return
    from core.fs_navigator import fs_navigator
    args = message.text.replace('/tree', '').strip().split()
    path = args[0] if args else None
    depth = int(args[1]) if len(args) > 1 and args[1].isdigit() else 2
    result = fs_navigator.tree(path, max_depth=depth)
    if not result['success']:
        bot.reply_to(message, f"❌ {result.get('error')}")
        return
    text = f"<pre>{result['tree'][:3500]}</pre>"
    bot.reply_to(message, text, parse_mode="HTML")

# ─── أمر /cat — قراءة ملف ───
@bot.message_handler(commands=['cat'])
def cmd_cat(message):
    if message.from_user.id != ADMIN_ID: return
    from core.fs_control import fs_control
    args = message.text.replace('/cat', '').strip().split()
    if not args:
        bot.reply_to(message, "الاستخدام: <code>/cat المسار [سطر_بداية] [سطر_نهاية]</code>", parse_mode="HTML")
        return
    path = args[0]
    s = int(args[1]) if len(args) > 1 else None
    e = int(args[2]) if len(args) > 2 else None
    result = fs_control.read_file(path, start_line=s, end_line=e)
    if not result['success']:
        bot.reply_to(message, f"❌ {result['error']}")
        return
    d = result['data']
    header = f"📄 <b>{d['relative']}</b> — {d['total_lines']} سطر | {d['size_kb']}KB\n<i>{d['note']}</i>\n"
    content_preview = d['content'][:3000]
    bot.reply_to(message, header + f"<pre>{content_preview}</pre>", parse_mode="HTML")

# ─── أمر /find — البحث في الملفات ───
@bot.message_handler(commands=['find'])
def cmd_find(message):
    if message.from_user.id != ADMIN_ID: return
    from core.fs_search import fs_search
    query = message.text.replace('/find', '').strip()
    if not query:
        bot.reply_to(message, "الاستخدام: <code>/find نص_البحث</code>", parse_mode="HTML")
        return
    bot.send_chat_action(message.chat.id, 'typing')
    name_results = fs_search.by_name(query)
    content_results = fs_search.by_content(query)
    lines = [f"🔍 <b>نتائج البحث: {query}</b>\n"]
    if name_results['count']:
        lines.append(f"<b>📁 بالاسم ({name_results['count']} نتيجة):</b>")
        for r in name_results['results'][:5]:
            lines.append(f"• <code>{r['relative']}</code>")
    if content_results['matches_found']:
        lines.append(f"\n<b>📄 في المحتوى ({content_results['matches_found']} تطابق):</b>")
        for r in content_results['results'][:8]:
            lines.append(f"• <code>{r['file']}</code> سطر {r['line_number']}")
            lines.append(f"  <i>{r['line_content'][:80]}</i>")
    if not name_results['count'] and not content_results['matches_found']:
        lines.append("لا توجد نتائج.")
    bot.reply_to(message, "\n".join(lines), parse_mode="HTML")

# ─── أمر /stat — معلومات ملف ───
@bot.message_handler(commands=['stat'])
def cmd_stat(message):
    if message.from_user.id != ADMIN_ID: return
    from core.fs_navigator import fs_navigator
    path = message.text.replace('/stat', '').strip()
    if not path:
        bot.reply_to(message, "الاستخدام: <code>/stat المسار</code>", parse_mode="HTML")
        return
    result = fs_navigator.stat(path)
    if not result['success']:
        bot.reply_to(message, f"❌ {result['error']}")
        return
    d = result['data']
    icon = "📁" if d['type'] == 'directory' else "📄"
    lines = [
        f"{icon} <b>{d['name']}</b>",
        f"━━━━━━━━━━━━━━",
        f"📍 المسار: <code>{d['path']}</code>",
        f"💾 الحجم: {d['size_kb']}KB",
        f"📅 آخر تعديل: {d['modified']}",
        f"🔐 الصلاحيات: {d['permissions_octal']}",
        f"{'✅' if d['readable'] else '❌'} قراءة | {'✅' if d['writable'] else '❌'} كتابة",
    ]
    if d['type'] == 'directory':
        lines.append(f"📂 العناصر المباشرة: {d.get('direct_children', '?')}")
        lines.append(f"💾 الحجم الكلي: {d.get('total_size_kb', '?')}KB")
    bot.reply_to(message, "\n".join(lines), parse_mode="HTML")

# ╔══════════════════════════════════════════╗
# ║        2. المعالج الشامل (The Processor) ║
# ╚══════════════════════════════════════════╝

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_universal(message):
    text = message.text or message.caption or ""
    if not text: return

    # تصنيف النية
    intent_result = classifier.classify(text)
    intent = intent_result.intent

    # ─── التنفيذ الحقيقي عبر ExecutionEngine ───
    if intent == Intent.EXECUTE or text.startswith('!'):
        goal = text[1:] if text.startswith('!') else text
        try:
            execution_engine.execute_goal(
                goal=goal,
                bot=bot,
                chat_id=message.chat.id
            )
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ في محرك التنفيذ: {e}")
        return

    # ─── المحادثة والذكاء ───
    _handle_chat(message, text)

def _handle_chat(message, text):
    history = context_memory.get_context(ADMIN_ID)
    system_instruction = "أنت NEXUM OS v7.5.0. لست مجرد شات بوت، أنت نظام تشغيل سيادي قادر على تنفيذ الأوامر وبناء المشاريع. كن حازماً وتقنياً."
    res, _ = gemini_service.ask(text, history=history, system_instruction=system_instruction)
    bot.reply_to(message, res)
    context_memory.save_context(ADMIN_ID, text, role='user')
    context_memory.save_context(ADMIN_ID, res, role='assistant')

if __name__ == "__main__":
    print("🔱 NEXUM CORE OS v7.5.0 is Online.")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
