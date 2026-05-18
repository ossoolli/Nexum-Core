import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# إصلاح دالة handle_plan بالكامل
old_plan = '''    bot.edit_message_text(
        f"📋 **{plan_name}**\\n🔢 عدد الخطوات: {len(steps)}",
        message.chat.id, status_msg.message_id,
        parse_mode="Markdown"
    )'''

new_plan = '''    bot.edit_message_text(
        f"📋 <b>{plan_name}</b>\\n🔢 عدد الخطوات: {len(steps)}",
        message.chat.id, status_msg.message_id,
        parse_mode="HTML"
    )'''

content = content.replace(old_plan, new_plan)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ تم إصلاح handle_plan")
