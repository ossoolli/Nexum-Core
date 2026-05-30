import os
import sys
sys.path.insert(0, "/home/madarmutaz/Nexum-Core")
from dotenv import load_dotenv
load_dotenv()
from telebot import TeleBot
from nexum.skills import SovereignSkillsManager
from nexum.cloud.agent_platform_connector import GoogleAgentPlatformConnector as AgentPlatformConnector

# Setup
bot_token = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
bot = TeleBot(bot_token)
manager = SovereignSkillsManager(skills_dir="/home/madarmutaz/Nexum-Core/storage/skills")
connector = AgentPlatformConnector()

# Load summary-config skill
skill = manager.load_skill("summary-config")

# Bot logic (simplified for aggregation)
message_buffer = []

@bot.message_handler(commands=['summarize'])
def summarize(message):
    if not message_buffer:
        bot.reply_to(message, "لا توجد رسائل لتلخيصها.")
        return
    
    # Placeholder for summarization logic using Gemini
    summary = f"Summary: {len(message_buffer)} messages aggregated."
    bot.reply_to(message, summary)
    message_buffer.clear()

@bot.message_handler(func=lambda m: True)
def handle(message):
    message_buffer.append(message.text)
    if len(message_buffer) >= 10:
        # Trigger auto-summary
        summarize(message)

if __name__ == "__main__":
    print("🤖 Telegram Summarizer Bot Online.")
    bot.infinity_polling()
