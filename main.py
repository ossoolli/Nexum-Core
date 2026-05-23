# -*- coding: utf-8 -*-
import os
import telebot
from nexum.config import config
from core.executive_agent import executive_agent

ADMIN_ID = config.admin_id
BOT_TOKEN = "8910270011:AAESyFAu4N_sbWFzGu_ds23W6cu4ETKuZR8"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and (msg.text.startswith('$ ') or msg.text.startswith('cmd ')))
def remote_terminal_executor(msg):
    try:
        cmd = msg.text.split(' ', 1)[1]
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=45)
        output = result.stdout if result.stdout else result.stderr
        bot.send_message(msg.chat.id, f"💻 <b>[Terminal Output]:</b>\n<pre>{output if output else 'Executed.'}</pre>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ <b>[Shell_Error]:</b>\n<code>{str(e)}</code>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == 'invoke_swarm')
def interactive_swarm_trigger(call):
    msg = bot.send_message(call.message.chat.id, "📥 <b>[Swarm_Ready]:</b> اكتب مأموريتك المخصصة لمجلس الحكماء:", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_custom_swarm_mission)

def process_custom_swarm_mission(msg):
    user_prompt = msg.text
    status_msg = bot.send_message(msg.chat.id, "⚙️ <b>[Swarm_Processing]:</b> جاري تشغيل مأموريتك المخصصة...", parse_mode="HTML")
    report = executive_agent.execute_mission(user_prompt)
    bot.send_message(msg.chat.id, report, parse_mode="HTML")

@bot.message_handler(commands=['status', 'dashboard'])
def handle_status_commands(msg):
    import subprocess
    res = subprocess.run("pm2 status", shell=True, capture_output=True, text=True)
    bot.send_message(msg.chat.id, f"📊 <b>[PM2 Status]:</b>\n<pre>{res.stdout}</pre>", parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID)
def master_ceo_orchestrator(msg):
    raw_text = msg.text
    status_msg = bot.send_message(msg.chat.id, "👔 <b>[Executive_Agent]:</b> جاري المعالجة الحصينة...", parse_mode="HTML")
    report = executive_agent.execute_mission(raw_text)
    bot.send_message(msg.chat.id, report, parse_mode="HTML")

if __name__ == '__main__':
    bot.infinity_polling()
