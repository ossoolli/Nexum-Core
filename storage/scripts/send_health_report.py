# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import telebot
from dotenv import load_dotenv

# Ensure project path is imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

# Load environment
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

def run_health_check():
    python_exe = sys.executable
    cmd = [python_exe, os.path.join(PROJECT_ROOT, "storage", "scripts", "monitor_nexum.py")]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    log_channel_id = os.getenv("LOG_CHANNEL_ID") or "-1003969021809"
    
    if not token:
        print("TELEGRAM_TOKEN not found in .env file.")
        sys.exit(1)
        
    report = run_health_check()
    print("Health check report generated:")
    print(report)
    
    bot = telebot.TeleBot(token)
    try:
        # Try sending as Markdown first
        bot.send_message(log_channel_id, report, parse_mode="Markdown")
        print("Successfully dispatched report to channel in Markdown format.")
    except Exception as e:
        print(f"Failed to send as Markdown: {e}. Retrying as plain text...")
        try:
            bot.send_message(log_channel_id, report)
            print("Successfully dispatched report to channel in plain text format.")
        except Exception as e2:
            print(f"Failed to send: {e2}")
            sys.exit(2)

if __name__ == "__main__":
    main()
