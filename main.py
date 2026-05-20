"""
ðŸ”± NEXUM CORE OS â€” Ø§Ù„Ø¨ÙˆØ§Ø¨Ø© Ø§Ù„Ø³ÙŠØ§Ø¯ÙŠØ© Ø§Ù„Ø±Ø¦ÙŠØ³ÙŠØ©
==============================================
ÙŠØ¬Ù…Ø¹ Ø¨ÙŠÙ†: Ø§Ù„Ø£ÙˆØ§Ù…Ø± Ø§Ù„Ù…Ø¨Ø§Ø´Ø±Ø©ØŒ Ø§Ù„ØªÙ†ÙÙŠØ° Ø§Ù„Ø°Ø§ØªÙŠØŒ ØªØ­Ù„ÙŠÙ„ Ø§Ù„Ù…Ù„ÙØ§ØªØŒ Ø§Ù„Ø¨Ø« Ø§Ù„Ø­ÙŠ.
"""
import os
import sys

# Ø¶Ù…Ø§Ù† Ù…Ø³Ø§Ø± Ø§Ù„Ø¹Ù…Ù„ Ø§Ù„ØµØ­ÙŠØ­
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

# â”€â”€â”€ Ø§Ù„Ù…ØªØºÙŠØ±Ø§Øª Ø§Ù„Ø£Ø³Ø§Ø³ÙŠØ© â”€â”€â”€
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID", "").strip("'\"")

# â”€â”€â”€ ØªÙ‡ÙŠØ¦Ø© Ø§Ù„Ù…Ø­Ø±ÙƒØ§Øª â”€â”€â”€
from services.gemini_service import GeminiService
from core.memory_local import LongTermMemory
from core.executor import executor

_gemini_svc = GeminiService(os.getenv("GOOGLE_API_KEY"))
_memory = LongTermMemory(os.path.join(BASE_DIR, 'storage', 'memory.json'))

# â”€â”€â”€ ØªÙ‡ÙŠØ¦Ø© Ø§Ù„Ù€ Orchestrator â”€â”€â”€
from core.orchestrator import orchestrator
from core.planner import AIPlanner

_planner = AIPlanner(_gemini_svc)
orchestrator.set_planner(_planner)
orchestrator.set_bot(bot, ADMIN_ID, LOG_CHANNEL_ID)

# â”€â”€â”€ ØªÙ‡ÙŠØ¦Ø© Ø§Ù„ÙˆÙƒÙ„Ø§Ø¡ â”€â”€â”€
from agents.monitor import monitor_agent
from agents.deploy import deploy_agent

# â”€â”€â”€ Ø§Ù„ÙˆÙƒÙ„Ø§Ø¡ Ø§Ù„Ø¬Ø¯Ø¯ (v5.0) â”€â”€â”€
from agents.webforge_agent import webforge as _webforge
from agents.bot_builder_agent import bot_builder as _bot_builder
from agents.agent_smith import agent_smith as _agent_smith
from agents.channel_manager import channel_manager as _channel_manager
from core.bot_fleet import bot_fleet as _bot_fleet
from core.bot_network import bot_network as _bot_network
from core.preview_server import preview_server as _preview_server

# â”€â”€â”€ Ø§Ù„Ø£ÙˆØ§Ù…Ø± Ø§Ù„Ù…Ø¹Ù„Ù‚Ø© (Ù„Ù„ØªØ£ÙƒÙŠØ¯ Ø§Ù„Ø£Ù…Ù†ÙŠ) â”€â”€â”€
pending_commands = {}

# â”€â”€â”€ Ø°Ø§ÙƒØ±Ø© Ø¢Ø®Ø± ØªØ­Ù„ÙŠÙ„ (Ù„Ù„Ø¨Ø« Ø§Ù„Ø³Ø±ÙŠØ¹) â”€â”€â”€
_last_analysis = {}  # {user_id: "Ø¢Ø®Ø± ØªØ­Ù„ÙŠÙ„ Ù…Ù„Ù/ØµÙˆØ±Ø©"}


# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘         Ø§Ù„Ø¨Ø« Ø§Ù„Ù…Ø¨Ø§Ø´Ø± Ù„Ù„Ù‚Ù†Ø§Ø©              â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def broadcast(msg, parse_mode="Markdown"):
    """Ø¥Ø±Ø³Ø§Ù„ Ø±Ø³Ø§Ù„Ø© Ù„Ù„Ù‚Ù†Ø§Ø© Ø§Ù„Ø­ÙŠØ©"""
    if LOG_CHANNEL_ID:
        try:
            bot.send_message(LOG_CHANNEL_ID, msg, parse_mode=parse_mode)
        except Exception as e:
            print(f"[Broadcast Error] {e}")


# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘         Ø§Ù„Ù…ØªØ±Ø¬Ù… Ø§Ù„Ø°ÙƒÙŠ (Interpreter)      â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class NexumInterpreter:
    """ÙŠØ­Ù„Ù„ Ù†ÙˆØ¹ Ø§Ù„Ø·Ù„Ø¨ ÙˆÙŠÙˆØ¬Ù‡Ù‡ Ù„Ù„Ø£Ø¯Ø§Ø© Ø£Ùˆ Ø§Ù„ÙˆÙƒÙŠÙ„ Ø§Ù„Ù…Ù†Ø§Ø³Ø¨"""

    # ÙƒÙ„Ù…Ø§Øª ØªØ¯Ù„ Ø¹Ù„Ù‰ Ø¨Ù†Ø§Ø¡ Ù…ÙˆØ§Ù‚Ø¹ (WebForge)
    WEBFORGE_KEYWORDS = [
        'Ø§Ù†Ø´Ø¦ Ù…ÙˆÙ‚Ø¹', 'Ø§Ø¨Ù†ÙŠ Ù…ÙˆÙ‚Ø¹', 'ØµÙØ­Ø© Ù‡Ø¨ÙˆØ·', 'landing page',
        'Ù„ÙˆØ­Ø© ØªØ­ÙƒÙ…', 'dashboard', 'ØªØ·Ø¨ÙŠÙ‚ ÙˆÙŠØ¨', 'web app', 'fastapi'
    ]

    # ÙƒÙ„Ù…Ø§Øª ØªØ¯Ù„ Ø¹Ù„Ù‰ Ø¨Ù†Ø§Ø¡ ÙˆÙƒÙŠÙ„
    AGENT_BUILD_KEYWORDS = [
        'Ø§Ø¨Ù†ÙŠ ÙˆÙƒÙŠÙ„', 'Ø§Ù†Ø´Ø¦ ÙˆÙƒÙŠÙ„', 'ØµÙ…Ù… ÙˆÙƒÙŠÙ„', 'build agent',
        'create agent', 'ÙˆÙƒÙŠÙ„ ÙŠØ±Ø§Ù‚Ø¨', 'ÙˆÙƒÙŠÙ„ ÙŠÙ‚ÙˆÙ…'
    ]

    # ÙƒÙ„Ù…Ø§Øª ØªØ¯Ù„ Ø¹Ù„Ù‰ Ø¨Ù†Ø§Ø¡ Ø¨ÙˆØª
    BOT_BUILD_KEYWORDS = [
        'Ø§Ø¨Ù†ÙŠ Ø¨ÙˆØª', 'Ø§Ù†Ø´Ø¦ Ø¨ÙˆØª', 'Ø¨ÙˆØª Ø¬Ø¯ÙŠØ¯', 'build bot',
        'Ø¨ÙˆØª ØªÙ„Ø¬Ø±Ø§Ù…', 'telegram bot', 'Ø§ØµÙ†Ø¹ Ø¨ÙˆØª'
    ]

    # ÙƒÙ„Ù…Ø§Øª ØªØ¯Ù„ Ø¹Ù„Ù‰ Ø¥Ø¯Ø§Ø±Ø© Ø£Ø³Ø·ÙˆÙ„ Ø§Ù„Ø¨ÙˆØªØ§Øª
    BOT_FLEET_KEYWORDS = [
        'Ù‚Ø§Ø¦Ù…Ø© Ø§Ù„Ø¨ÙˆØªØ§Øª', 'list bots', 'Ø¨ÙˆØªØ§ØªÙŠ', 'Ø£ÙˆÙ‚Ù Ø¨ÙˆØª',
        'Ø­Ø§Ù„Ø© Ø§Ù„Ø¨ÙˆØªØ§Øª', 'Ø£Ø³Ø·ÙˆÙ„ Ø§Ù„Ø¨ÙˆØªØ§Øª'
    ]

    # ÙƒÙ„Ù…Ø§Øª ØªØ¯Ù„ Ø¹Ù„Ù‰ Ø¥Ø¯Ø§Ø±Ø© Ø§Ù„Ù‚Ù†ÙˆØ§Øª
    CHANNEL_KEYWORDS = [
        'Ø§Ù†Ø´Ø± ÙÙŠ ÙƒÙ„', 'Ø¬Ø¯ÙˆÙÙ„ Ù…Ù†Ø´ÙˆØ±', 'Ø¥Ø¯Ø§Ø±Ø© Ø§Ù„Ù‚Ù†Ø§Ø©',
        'Ø¨Ø« Ù„Ù„Ù‚Ù†ÙˆØ§Øª', 'Ù‚Ù†ÙˆØ§ØªÙŠ', 'cross post'
    ]

    # ÙƒÙ„Ù…Ø§Øª ØªØ¯Ù„ Ø¹Ù„Ù‰ Ø§Ù„Ø¨Ø« Ù„Ù„Ù‚Ù†Ø§Ø© Ø§Ù„Ø±Ø¦ÙŠØ³ÙŠØ©
    BROADCAST_KEYWORDS = ['Ø§Ø±Ø³Ù„ Ù„Ù„Ù‚Ù†Ø§Ø©', 'Ø§Ø±Ø³Ù„ Ø§Ù„Ù‰ Ø§Ù„Ù‚Ù†Ø§Ø©', 'Ø§Ù†Ø´Ø± Ù ÙŠ Ø§Ù„Ù‚Ù†Ø§Ø©']

    # ÙƒÙ„Ù…Ø§Øª ØªØ¯Ù„ Ø¹Ù„Ù‰ Ø·Ù„Ø¨ Ù…Ø±Ø§Ù‚Ø¨Ø©
    MONITOR_KEYWORDS = ['Ø­Ø§Ù„Ø© Ø§Ù„Ù†Ø¸Ø§Ù…', 'status', 'Ø§Ù„Ù†Ø¨Ø¶', 'pulse', 'Ù…ÙˆØ§Ø±Ø¯']

    # كلمات تدل على طلب نشر Git
    DEPLOY_KEYWORDS = ['ارفع', 'نشر', 'git']

    # كلمات تدل على التنفيذ وإنشاء الملفات
    EXECUTE_KEYWORDS = ['انشئ ملف', 'اكتب', 'انشئ فولدر', 'نفذ', 'شغل']

    def classify(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in self.EXECUTE_KEYWORDS): return "execute"
        if any(w in text_lower for w in self.WEBFORGE_KEYWORDS): return "webforge"
        if any(w in text_lower for w in self.AGENT_BUILD_KEYWORDS): return "agent_build"
        if any(w in text_lower for w in self.BOT_BUILD_KEYWORDS): return "bot_build"
        if any(w in text_lower for w in self.BOT_FLEET_KEYWORDS): return "bot_fleet"
        if any(w in text_lower for w in self.CHANNEL_KEYWORDS): return "channel"
        if any(w in text_lower for w in self.BROADCAST_KEYWORDS): return "broadcast"
        if any(w in text_lower for w in self.MONITOR_KEYWORDS): return "monitor"
        if any(w in text_lower for w in self.DEPLOY_KEYWORDS): return "deploy"
        return "chat"

interpreter = NexumInterpreter()

# â•”â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•—
# â•‘         Ù‚ÙˆØ§Ù„Ø¨ Ø§Ù„Ø±Ø³Ø§Ø¦Ù„ Ø§Ù„Ù…ÙˆØ­Ø¯Ø©             â•‘
OPERATION_TEMPLATE = "ðŸ“‹ *{name}*\n\n{body}\n\nâ”â”â”â”â”â”â”â”â”â”â”â”â”â”\nØ§Ù„Ø­Ø§Ù„Ø©: {icon} {status}"

# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘         Ø¯ÙˆØ§Ø¦Ø± Ø§Ù„Ù€ Markup ÙˆØ§Ù„ØªØ¨ÙˆÙŠØ¨Ø§Øª         â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def get_main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("ðŸŒ Ø§Ù„Ù…ÙˆØ§Ù‚Ø¹", callback_data="menu:webforge"),
        types.InlineKeyboardButton("ðŸ¤– Ø§Ù„ÙˆÙƒÙ„Ø§Ø¡",  callback_data="menu:agents")
    )
    markup.add(
        types.InlineKeyboardButton("ðŸ¤– Ø§Ù„Ø¨ÙˆØªØ§Øª",  callback_data="menu:bots"),
        types.InlineKeyboardButton("ðŸ“¢ Ø§Ù„Ù‚Ù†ÙˆØ§Øª",  callback_data="menu:channels")
    )
    markup.add(
        types.InlineKeyboardButton("ðŸ“Š Ø§Ù„Ù…Ø±Ø§Ù‚Ø¨Ø©",  callback_data="menu:monitor"),
        types.InlineKeyboardButton("ðŸ“‹ Ø§Ù„Ø³Ø¬Ù„Ø§Øª",  callback_data="menu:logs")
    )
    markup.add(
        types.InlineKeyboardButton("âš™ï¸ Ø§Ù„Ø¥Ø¹Ø¯Ø§Ø¯Ø§Øª", callback_data="menu:settings"),
        types.InlineKeyboardButton("ðŸ›¡ï¸ Ø§Ù„Ø£Ù…Ø§Ù†",   callback_data="menu:security")
    )
    markup.add(
        types.InlineKeyboardButton("âž• Ù…Ù‡Ù…Ø© Ø¬Ø¯ÙŠØ¯Ø©", callback_data="task:new"),
        types.InlineKeyboardButton("ðŸ”„ Ø­Ø§Ù„Ø© Ø§Ù„Ù†Ø¸Ø§Ù…", callback_data="system:status")
    )
    return markup

def get_webforge_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("ðŸ  ØµÙØ­Ø© Ù‡Ø¨ÙˆØ·",   callback_data="wf:landing"),
        types.InlineKeyboardButton("ðŸ“Š Ù„ÙˆØ­Ø© ØªØ­ÙƒÙ…",    callback_data="wf:dashboard")
    )
    markup.add(
        types.InlineKeyboardButton("âš¡ FastAPI App",   callback_data="wf:api"),
        types.InlineKeyboardButton("ðŸ“ Ù…Ø´Ø§Ø±ÙŠØ¹ÙŠ",      callback_data="wf:list")
    )
    markup.add(types.InlineKeyboardButton("â—€ï¸ Ø±Ø¬ÙˆØ¹", callback_data="menu:main"))
    return markup

def get_agents_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("ðŸŽ¨ ØµÙ…Ù‘Ù… ÙˆÙƒÙŠÙ„",    callback_data="ag:design"),
        types.InlineKeyboardButton("ðŸ“‹ ÙˆÙƒÙ„Ø§Ø¦ÙŠ",       callback_data="ag:list")
    )
    markup.add(
        types.InlineKeyboardButton("â–¶ï¸ ØªØ´ØºÙŠÙ„",        callback_data="ag:run_menu"),
        types.InlineKeyboardButton("â¸ Ø¥ÙŠÙ‚Ø§Ù",         callback_data="ag:pause_menu")
    )
    markup.add(types.InlineKeyboardButton("â—€ï¸ Ø±Ø¬ÙˆØ¹", callback_data="menu:main"))
    return markup

def get_bots_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("âž• Ø¨ÙˆØª Ø¬Ø¯ÙŠØ¯",     callback_data="bt:new"),
        types.InlineKeyboardButton("ðŸ“‹ Ø¨ÙˆØªØ§ØªÙŠ",       callback_data="bt:list")
    )
    markup.add(
        types.InlineKeyboardButton("ðŸ“¡ Ø§Ù„Ø¨Ø« Ù„Ù„ÙƒÙ„",    callback_data="bt:broadcast"),
        types.InlineKeyboardButton("ðŸ”— Ø§Ù„Ø´Ø¨ÙƒØ©",       callback_data="menu:network")
    )
    markup.add(types.InlineKeyboardButton("â—€ï¸ Ø±Ø¬ÙˆØ¹", callback_data="menu:main"))
    return markup

def get_channels_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("âž• Ø±Ø¨Ø· Ù‚Ù†Ø§Ø©",     callback_data="ch:register"),
        types.InlineKeyboardButton("ðŸ“‹ Ù‚Ù†ÙˆØ§ØªÙŠ",       callback_data="ch:list")
    )
    markup.add(
        types.InlineKeyboardButton("ðŸ“ Ù…Ù†Ø´ÙˆØ± Ø§Ù„Ø¢Ù†",   callback_data="ch:post_now"),
        types.InlineKeyboardButton("ðŸ—“ Ø¬Ø¯ÙˆÙÙ„",       callback_data="ch:schedule")
    )
    markup.add(types.InlineKeyboardButton("â—€ï¸ Ø±Ø¬ÙˆØ¹", callback_data="menu:main"))
    return markup

def get_settings_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("âœï¸ Ø§Ø³Ù… Ø§Ù„Ø¨ÙˆØª",           callback_data="st:bf:name"),
        types.InlineKeyboardButton("ðŸ“ Ø§Ù„ÙˆØµÙ (Bio)",         callback_data="st:bf:desc"),
        types.InlineKeyboardButton("ðŸ”‘ API Keys",            callback_data="st:nx:keys"),
        types.InlineKeyboardButton("ðŸŒ Ø§Ù„Ù„ØºØ©",               callback_data="st:nx:lang"),
        types.InlineKeyboardButton("â—€ï¸ Ø±Ø¬ÙˆØ¹",                callback_data="menu:main")
    )
    return markup

def get_monitor_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("ðŸ’» CPU/RAM",      callback_data="mon:system"),
        types.InlineKeyboardButton("ðŸ“ Ø§Ù„Ø³Ø¬Ù„Ø§Øª",     callback_data="mon:logs")
    )
    markup.add(
        types.InlineKeyboardButton("ðŸ”„ ØªØ­Ø¯ÙŠØ«",        callback_data="mon:refresh"),
        types.InlineKeyboardButton("â—€ï¸ Ø±Ø¬ÙˆØ¹",        callback_data="menu:main")
    )
    return markup

def get_network_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("ðŸ—º Ø®Ø±ÙŠØ·Ø© Ø§Ù„Ø´Ø¨ÙƒØ©",   callback_data="net:map"),
        types.InlineKeyboardButton("âž• Ø±Ø¨Ø· Ø¨ÙˆØª",         callback_data="net:connect_bot")
    )
    markup.add(types.InlineKeyboardButton("â—€ï¸ Ø±Ø¬ÙˆØ¹", callback_data="menu:main"))
    return markup

# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘         Ø§Ù„ØªÙ†Ù‚Ù„ ÙˆØ§Ù„Ù…Ù„Ø§Ø­Ø© (Navigation)      â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

async def navigate_to(call, screen: str):
    """ÙŠÙ†Ù‚Ù„ Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù… Ù„Ù„Ø´Ø§Ø´Ø© Ø§Ù„Ù…Ø·Ù„ÙˆØ¨Ø© Ø¨ØªØ¹Ø¯ÙŠÙ„ Ø§Ù„Ø±Ø³Ø§Ù„Ø©"""
    screens = {
        "main": ("ðŸ”± *NEXUM CORE OS* Ø¬Ø§Ù‡Ø²\n\nØ§Ø®ØªØ± Ù…Ù† Ø§Ù„Ù‚Ø§Ø¦Ù…Ø© Ø£Ùˆ Ø§ÙƒØªØ¨ Ø£Ù…Ø±Ùƒ Ù…Ø¨Ø§Ø´Ø±Ø©Ù‹:", get_main_menu_markup()),
        "webforge": ("ðŸŒ *WebForge* â€” Ø¨Ù†Ø§Ø¡ Ø§Ù„Ù…ÙˆØ§Ù‚Ø¹ ÙˆØ§Ù„ÙˆØ§Ø¬Ù‡Ø§Øª\nÙ…Ø§Ø°Ø§ ØªÙˆØ¯ Ø£Ù† ØªØ¨Ø¯Ø£ Ø§Ù„ÙŠÙˆÙ…ØŸ", get_webforge_markup()),
        "agents": ("ðŸ¤– *Ø¥Ø¯Ø§Ø±Ø© Ø§Ù„ÙˆÙƒÙ„Ø§Ø¡*\nØµÙ…Ù… ÙˆØ´ØºÙ„ ÙˆÙƒÙ„Ø§Ø¦Ùƒ Ø§Ù„Ø£Ø°ÙƒÙŠØ§Ø¡ Ù‡Ù†Ø§.", get_agents_markup()),
        "bots": ("ðŸ¤– *Ø£Ø³Ø·ÙˆÙ„ Ø§Ù„Ø¨ÙˆØªØ§Øª*\nØªØ­ÙƒÙ… Ø¨Ø¬Ù…ÙŠØ¹ Ø¨ÙˆØªØ§ØªÙƒ Ø§Ù„Ù…Ø³ØªÙ‚Ù„Ø© Ù…Ù† Ù…ÙƒØ§Ù† ÙˆØ§Ø­Ø¯.", get_bots_markup()),
        "channels": ("ðŸ“¢ *Ù…Ø¯ÙŠØ± Ø§Ù„Ù‚Ù†ÙˆØ§Øª*\nØ¬Ø¯ÙˆÙ„Ø© ÙˆÙ†Ø´Ø± Ø§Ù„Ù…Ø­ØªÙˆÙ‰ Ø¹Ø¨Ø± Ù‚Ù†ÙˆØ§ØªÙƒ Ø§Ù„Ù…Ø³Ø¬Ù„Ø©.", get_channels_markup()),
        "settings": ("âš™ï¸ *Ø¥Ø¹Ø¯Ø§Ø¯Ø§Øª Ø§Ù„Ù†Ø¸Ø§Ù…*\nØªØ®ØµÙŠØµ Ø§Ù„Ø¨ÙˆØªØŒ Ø±Ø¨Ø· Ø§Ù„Ù…ÙØ§ØªÙŠØ­ØŒ ÙˆØ§Ù„Ù„ØºØ©.", get_settings_markup()),
        "monitor": ("ðŸ“Š *Ø§Ù„Ù…Ø±Ø§Ù‚Ø¨Ø©*\nØ­Ø§Ù„Ø© Ø§Ù„Ø³ÙŠØ±ÙØ± ÙˆÙ…ÙˆØ§Ø±Ø¯ Ø§Ù„Ù†Ø¸Ø§Ù… Ø§Ù„Ø­ÙŠØ©.", get_monitor_markup()),
        "network": ("ðŸ“¡ *Ø´Ø¨ÙƒØ© NEXUM*\nØ´Ø¨ÙƒØ© Ø§Ù„Ø§ØªØµØ§Ù„ Ø¨ÙŠÙ† Ø§Ù„Ø¨ÙˆØªØ§Øª ÙˆØ§Ù„ÙˆÙƒÙ„Ø§Ø¡.", get_network_markup()),
    }
    
    if screen in screens:
        text, markup = screens[screen]
        if screen == "monitor":
            from agents.monitor import monitor_agent
            text = f"ðŸ“Š *Ø­Ø§Ù„Ø© Ø§Ù„Ù†Ø¸Ø§Ù…*\n\n{monitor_agent.get_pulse_report()}"
            
        try:
            bot.edit_message_text(
                text, call.message.chat.id, call.message.message_id,
                parse_mode="Markdown", reply_markup=markup
            )
        except Exception:
            bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘         Ù…Ø¹Ø§Ù„Ø¬Ø§Øª Ø§Ù„ØªÙ„Ø¬Ø±Ø§Ù… (Handlers)      â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID: return
    bot.send_message(
        message.chat.id,
        "ðŸ”± *NEXUM CORE OS* Ø¬Ø§Ù‡Ø²\n\nØ§Ø®ØªØ± Ù…Ù† Ø§Ù„Ù‚Ø§Ø¦Ù…Ø© Ø£Ùˆ Ø§ÙƒØªØ¨ Ø£Ù…Ø±Ùƒ Ù…Ø¨Ø§Ø´Ø±Ø©Ù‹:",
        reply_markup=get_main_menu_markup(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.from_user.id != ADMIN_ID: return
    data = call.data
    
    # â”€â”€â”€ Ø§Ù„Ù…Ù„Ø§Ø­Ø© Ø§Ù„Ø±Ø¦ÙŠØ³ÙŠØ© â”€â”€â”€
    if data.startswith("menu:"):
        screen = data.split(":")[1]
        import asyncio
        asyncio.run(navigate_to(call, screen))
        
    # â”€â”€â”€ Ø§Ù„Ù…Ø±Ø§Ù‚Ø¨Ø© Ø§Ù„Ø³Ø±ÙŠØ¹Ø© â”€â”€â”€
    elif data == "system:status":
        from agents.monitor import monitor_agent
        bot.answer_callback_query(call.id, "Ø¬Ø§Ø±ÙŠ Ø¬Ù„Ø¨ Ø§Ù„Ø¨ÙŠØ§Ù†Ø§Øª...")
        bot.send_message(call.message.chat.id, monitor_agent.get_pulse_report(), parse_mode="HTML")

    # â”€â”€â”€ ØªØ£ÙƒÙŠØ¯ Ø§Ù„Ø­Ø°Ù/Ø§Ù„Ø¥ÙŠÙ‚Ø§Ù (Ù…Ø«Ø§Ù„) â”€â”€â”€
    elif data.startswith("confirm:"):
        _, action, item = data.split(":")
        bot.answer_callback_query(call.id, f"ØªÙ… ØªÙ†ÙÙŠØ° {action} Ø¹Ù„Ù‰ {item}")
        # ØªÙ†ÙÙŠØ° Ø§Ù„ÙØ¹Ù„ Ø§Ù„Ø­Ù‚ÙŠÙ‚ÙŠ Ù‡Ù†Ø§

    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_universal(message):
    if message.from_user.id != ADMIN_ID: return
    
    # Ø§Ù„ØªØ­Ù‚Ù‚ Ù…Ù† ÙˆØ¬ÙˆØ¯ Ø¹Ù…Ù„ÙŠØ© Flow Ø¬Ø§Ø±ÙŠØ©
    from core.multi_step_flow import flow_manager
    flow = flow_manager.get_flow(message.from_user.id)
    if flow:
        # Ù…Ø¹Ø§Ù„Ø¬Ø© Step-by-step
        return # Ø³Ø£ÙƒÙ…Ù„ Ù…Ù†Ø·Ù‚ Ø§Ù„Ù€ Flow Ù„Ø§Ø­Ù‚Ø§Ù‹
        
    text = message.text or message.caption or ""
    category = interpreter.classify(text)

    # ØªÙˆØ¬ÙŠÙ‡ Ø§Ù„Ø·Ù„Ø¨ Ø­Ø³Ø¨ Ø§Ù„ØªØµÙ†ÙŠÙ ÙƒÙ…Ø§ ÙÙŠ Ø§Ù„Ù†Ø³Ø®Ø© Ø§Ù„Ø³Ø§Ø¨Ù‚Ø©
    if category == "monitor":
        bot.reply_to(message, monitor_agent.get_pulse_report(), parse_mode="HTML")
    # ... Ø¨Ù‚ÙŠØ© Ø§Ù„Ù€ handlers Ù…ÙˆØ¬ÙˆØ¯Ø© Ø¨Ø§Ù„ÙØ¹Ù„ ...

if __name__ == "__main__":
    # ØªØ³Ø¬ÙŠÙ„ Ø£Ø¯ÙˆØ§Øª Ø§Ù„Ù†Ø¸Ø§Ù…
    from core.system_tools import register_all_system_tools
    register_all_system_tools()
    
    # ØªØ³Ø¬ÙŠÙ„ Ø¥Ø¹Ø¯Ø§Ø¯Ø§Øª BotFather (Async)
    try:
        from core.botfather_manager import BotFatherManager
        import asyncio
        manager = BotFatherManager(os.getenv("TELEGRAM_TOKEN"))
        asyncio.run(manager.sync_all_settings(webapp_url=f"https://{os.getenv('DOMAIN', 'nexum.dev')}/mini-app"))
    except Exception as e:
        print(f"âš ï¸ BotFather Sync Failed: {e}")

    print("ðŸ”± NEXUM CORE OS v7.0 â€” Premium UI/UX Online.")
    broadcast("ðŸ”± **NEXUM OS v7.0** Ø¨Ø¯Ø£ Ø§Ù„Ø¹Ù…Ù„ Ø¨ÙˆØ§Ø¬Ù‡Ø© Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù… Ø§Ù„Ø¬Ø¯ÙŠØ¯Ø©.")
    bot.infinity_polling()
".join(lines), parse_mode="HTML")
        else:
            bot.reply_to(message, "ðŸ¤– Ù„Ø§ ØªÙˆØ¬Ø¯ Ø¨ÙˆØªØ§Øª ÙÙŠ Ø§Ù„Ø£Ø³Ø·ÙˆÙ„. Ø§ÙƒØªØ¨: <b>Ø§Ø¨Ù†ÙŠ Ø¨ÙˆØª</b>", parse_mode="HTML")
        return

    # â”€â”€â”€ Channel Manager â”€â”€â”€
    if category == "channel":
        channels = _channel_manager.list_channels()
        if channels:
            lines = ["ðŸ“¢ <b>Ù‚Ù†ÙˆØ§ØªÙŠ:</b>"]
            for c in channels:
                lines.append(f"ðŸ“± {c['name']} â€” {c['posts_count']} Ù…Ù†Ø´ÙˆØ±")
            bot.send_message(message.chat.id, "\n".join(lines), parse_mode="HTML")
        else:
            bot.reply_to(message, "ðŸ“¢ Ù„Ø§ ØªÙˆØ¬Ø¯ Ù‚Ù†ÙˆØ§Øª Ù…Ø³Ø¬Ù„Ø©.")
        return

    # â”€â”€â”€ Ø§Ù„ØªÙ†ÙÙŠØ° Ø¹Ø¨Ø± Ø§Ù„Ù€ Orchestrator â”€â”€â”€
    if category == "execute":
        bot.reply_to(message, "ðŸ§  **NEXUM OS**\nØ¬Ø§Ø±ÙŠ Ø§Ù„ØªØ®Ø·ÙŠØ· ÙˆØ§Ù„ØªÙ†ÙÙŠØ°...", parse_mode="Markdown")
        try:
            res = orchestrator.execute_goal(text)
            pid = res.get('protocol_id', 'unknown')
            bot.send_message(message.chat.id, f"âœ… ØªÙ… Ø§Ù„Ø§Ø³ØªÙ„Ø§Ù…: `{pid}`", parse_mode="Markdown")
            _memory.save_context(message.from_user.id, f"[ØªÙ†ÙÙŠØ°: {pid}] {text}", role='user')
        except Exception as e:
            bot.reply_to(message, f"âŒ Ø®Ø·Ø£ ÙÙŠ Ø§Ù„ØªÙ†ÙÙŠØ°: {e}")
        return

    # â”€â”€â”€ Ø§Ù„Ø¯Ø±Ø¯Ø´Ø© Ø§Ù„Ø¹Ø§Ù…Ø© (Chat Mode) â”€â”€â”€
    bot.send_chat_action(message.chat.id, 'typing')
    _memory.save_context(message.from_user.id, text, role='user')
    try:
        # Ø¬Ù„Ø¨ Ø§Ù„Ø³ÙŠØ§Ù‚ Ù…Ù† Ø§Ù„Ø°Ø§ÙƒØ±Ø© Ù„Ø¬Ø¹Ù„ Ø§Ù„Ø±Ø¯ÙˆØ¯ Ø£Ø°ÙƒÙ‰
        context = _memory.get_context(message.from_user.id)
        history_prompt = ""
        if context:
            last_5 = context[-5:]
            history_prompt = "\n".join([f"{c['role']}: {c['content']}" for c in last_5])
            history_prompt = f"Ø³ÙŠØ§Ù‚ Ø§Ù„Ù…Ø­Ø§Ø¯Ø«Ø© Ø§Ù„Ø³Ø§Ø¨Ù‚Ø©:\n{history_prompt}\n\n"

        full_prompt = f"{history_prompt}Ø§Ù„Ø±Ø³Ø§Ù„Ø© Ø§Ù„Ø­Ø§Ù„ÙŠØ©: {text}"
        res, _ = _gemini_svc.ask(
            full_prompt,
            system_instruction=(
                "Ø£Ù†Øª NEXUM OS Ù†Ø¸Ø§Ù… ØªØ´ØºÙŠÙ„ Ø°ÙƒØ§Ø¡ Ø§ØµØ·Ù†Ø§Ø¹ÙŠ Ø³ÙŠØ§Ø¯ÙŠ ÙŠØ¹Ù…Ù„ Ø¹Ù„Ù‰ Ø³ÙŠØ±ÙØ± Ø®Ø§Øµ Ø¨Ø§Ù„Ù…Ø§ÙŠØ³ØªØ±Ùˆ Ù…Ø¹ØªØ². "
                "Ù‚ÙˆØ§Ø¹Ø¯ ØµØ§Ø±Ù…Ø©: "
                "1. Ø¥Ø°Ø§ Ù‚Ø§Ù„ Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù… 'Ù…Ø±Ø­Ø¨Ø§' Ø£Ùˆ ØªØ­ÙŠØ©ØŒ Ø±Ø¯ Ø¨Ø¬Ù…Ù„Ø© ØªØ±Ø­ÙŠØ¨ Ù‚ØµÙŠØ±Ø© ÙˆØ§Ø³Ø£Ù„Ù‡ ÙƒÙŠÙ ØªØ³Ø§Ø¹Ø¯Ù‡. Ù„Ø§ ØªÙƒØªØ¨ Ø£ÙƒØ«Ø± Ù…Ù† 3 Ø£Ø³Ø·Ø±. "
                "2. Ù„Ø§ ØªÙƒØªØ¨ ØªÙ‚Ø§Ø±ÙŠØ± ØªÙ‚Ù†ÙŠØ© Ø·ÙˆÙŠÙ„Ø© Ø¥Ù„Ø§ Ø¥Ø°Ø§ Ø·ÙÙ„Ø¨ Ù…Ù†Ùƒ Ø°Ù„Ùƒ ØµØ±Ø§Ø­Ø©. "
                "3. Ø¥Ø°Ø§ Ø³Ø£Ù„Ùƒ Ø³Ø¤Ø§Ù„Ø§Ù‹ Ù…Ø­Ø¯Ø¯Ø§Ù‹ØŒ Ø£Ø¬Ø¨ Ø¨Ø´ÙƒÙ„ Ù…Ø®ØªØµØ± ÙˆÙ…Ø±ÙƒØ². "
                "4. ØªØ­Ø¯Ø« Ø¨Ø§Ù„Ø¹Ø±Ø¨ÙŠØ© Ø¯Ø§Ø¦Ù…Ø§Ù‹. "
                "5. Ø£Ù†Øª Ù…Ø³Ø§Ø¹Ø¯ Ø°ÙƒÙŠ ÙˆÙˆØ¯ÙˆØ¯ØŒ Ù„Ø³Øª Ù…Ø­Ø§Ø¶Ø±Ø§Ù‹."
            )
        )
        bot.reply_to(message, res)
        _memory.save_context(message.from_user.id, res[:500], role='assistant')
    except Exception as e:
        bot.reply_to(message, f"âŒ Ø®Ø·Ø£: {e}")


# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘            Ù†Ù‚Ø·Ø© Ø§Ù„Ø¨Ø¯Ø§ÙŠØ©                  â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

if __name__ == "__main__":
    # ØªØ³Ø¬ÙŠÙ„ Ø£Ø¯ÙˆØ§Øª Ø§Ù„Ù†Ø¸Ø§Ù…
    from core.system_tools import register_all_system_tools
    register_all_system_tools()

    print("ðŸ”± NEXUM CORE OS v5.0 â€” Online and Sovereign.")
    broadcast("ðŸ”± **NEXUM OS v5.0** Ø¨Ø¯Ø£ Ø§Ù„Ø¹Ù…Ù„ Ø¨Ù†Ø¬Ø§Ø­.\nØ¬Ù…ÙŠØ¹ Ø§Ù„Ø£Ù†Ø¸Ù…Ø© Ù†Ø´Ø·Ø©.")
    bot.infinity_polling()
