"""
🔱 NEXUM LLM Factory — مصنع النماذج الذكية
=============================================
يوفر واجهة موحدة للتعامل مع Gemini و OpenAI و OpenRouter.
الاعتماديات اختيارية — لن ينهار النظام إذا لم تكن مكتبة مثبتة.
"""
import os
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(base_dir, ".env"), override=True)

# Sanitize environment variables for dynamic pathing
for k, v in list(os.environ.items()):
    if isinstance(v, str) and "/home/madarmutaz/Nexum-Core" in v:
        os.environ[k] = v.replace("/home/madarmutaz/Nexum-Core", base_dir)


class LLMFactory:
    def __init__(self):
        self._gemini_client = None
        self._openai_client = None
        self.model_id = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.sessions = {}

        # محاولة تحميل Gemini SDK (اختياري)
        try:
            from google import genai
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                self._gemini_client = genai.Client(api_key=api_key)
        except ImportError:
            print("[LLM Factory] google-genai not installed — Gemini SDK disabled")

        # محاولة تحميل OpenAI SDK (اختياري)
        try:
            from openai import OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self._openai_client = OpenAI(api_key=openai_key)
        except ImportError:
            print("[LLM Factory] openai not installed — OpenAI disabled")

    def get_chat_session(self, user_id):
        if not self._gemini_client:
            return None
        if user_id not in self.sessions:
            self.sessions[user_id] = self._gemini_client.chats.create(model=self.model_id)
        return self.sessions[user_id]

    def ask_gemini(self, user_id, prompt):
        try:
            chat = self.get_chat_session(user_id)
            if not chat:
                return "⚠️ Gemini SDK غير متوفر. استخدم الطريقة البديلة."
            response = chat.send_message(prompt)
            return response.text.strip()
        except Exception as e:
            return f"⚠️ خطأ في Gemini: {str(e)}"

    def ask_specialist(self, prompt):
        if not self._openai_client:
            return "⚠️ مكتبة OpenAI غير مثبتة."
        try:
            res = self._openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ خطأ في OpenAI: {str(e)}"


llm = LLMFactory()
