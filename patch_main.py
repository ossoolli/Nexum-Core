import os

filepath = 'main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "def handle_callbacks(call):" in line:
        new_lines.pop() # إزالة السطر الخاص بالـ decorator السابق
        skip = True
    elif skip and "def handle_universal(message):" in line:
        skip = False
        
    if not skip:
        if "def handle_universal(message):" in line:
            new_lines.append("@bot.message_handler(content_types=['photo', 'document', 'text'])\n")
            
        if "bot.infinity_polling()" in line:
            new_lines.append("    from core.router import setup_router\n")
            new_lines.append("    setup_router(bot)\n")
            
            # إضافة كود تحديث BotFather
            new_lines.append("    # بدء مزامنة BotFather بشكل غير متزامن\n")
            new_lines.append("    import asyncio\n")
            new_lines.append("    from core.botfather_manager import BotFatherManager\n")
            new_lines.append("    botfather = BotFatherManager('توكن البوت هنا أو جلبه من os.getenv')\n")
            new_lines.append("    botfather.api_base = f'https://api.telegram.org/bot{os.getenv(\"TELEGRAM_TOKEN\")}'\n")
            new_lines.append("    # يمكنك إضافة رابط الـ WebApp هنا إذا كان السيرفر متاحاً\n")
            new_lines.append("    asyncio.run(botfather.sync_all_settings('https://mini-app-url.com'))\n\n")
            
        new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("تم تعديل main.py بنجاح! يمكنك الآن تشغيله بشكل طبيعي.")
