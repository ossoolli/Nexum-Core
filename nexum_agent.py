import os
import sys
from google import genai
from google.genai import types

# ─── 1. تعريف الأدوات المادية (System Tools) ───

def execute_bash(cmd: str) -> str:
    """Executes a bash/terminal command on the server and returns the output."""
    import subprocess
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd="/home/madarmutaz/Nexum-Core"
        )
        return result.stdout or result.stderr or "Command executed with no output."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def read_file(file_path: str) -> str:
    """Reads and returns the full text content of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f: return f.read()
    except Exception as e: return f"❌ Error: {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """Writes or overwrites text content into a file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f: f.write(content)
        return f"✅ File successfully updated."
    except Exception as e: return f"❌ Error: {str(e)}"

# ─── 2. بناء العميل وبدء جلسة الوكيل المستقل ───

api_key = os.getenv("GOOGLE_API_KEY", "").strip()
if not api_key:
    print("❌ خطأ سيادي: GOOGLE_API_KEY غير معرف في بيئة النظام الحالي.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# إنشاء جلسة درشة ممتدة تعمل كـ Agent مدمج يدير أدواته ذاتياً بالكامل
print("🔱 [NEXUM] Connecting Sovereign Agent to Gemini-2.0-Flash...")
nexum_chat = client.chats.create(
    model="gemini-3.1-flash-lite",
    config=types.GenerateContentConfig(
        system_instruction=(
            "You are Nexum Core Sovereign OS. Your priority is speed and execution.\n"
            "You have direct access to the server. Execute tools immediately without asking permissions."
        ),
        tools=[execute_bash, read_file, write_file]
    )
)

print("✅ [NEXUM SYSTEM RUNTIME]: Agent Platform is Online and ready.")

# مثال تشغيلي مبدئي لإثبات سلطة الوكيل الذاتية دون حلقات برمجية يدوية:
response = nexum_chat.send_message("تأكد من محتوى ملف mutazai.txt واكتب بداخله 'Agent verified successfully'")
print(f"\n🤖 [AGENT RESPONSE]:\n{response.text}")
