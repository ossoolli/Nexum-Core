import os
from google import genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
))

class LLMFactory:
    def __init__(self):
        # تفعيل المحرك السيادي الموحد لعام 2026 باستخدام google-genai Client 
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash"  # النموذج المعتمد والمثالي لسرعة الاستجابة 
        
        # كاش الذاكرة السياقية التاريخية للمايسترو معتز
        self.sessions = {}
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_chat_session(self, user_id):
        if user_id not in self.sessions:
            # تفعيل نظام الجلسات والتعرف الرقمي التلقائي
            self.sessions[user_id] = self.client.chats.create(model=self.model_id)
        return self.sessions[user_id]

    def ask_gemini(self, user_id, prompt):
        try:
            chat = self.get_chat_session(user_id)
            response = chat.send_message(prompt)
            return response.text.strip()
        except Exception as e:
            return f"⚠️ عائق تقني في عقل جوجل: {str(e)}"

    def ask_specialist(self, prompt):
        try:
            res = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ عائق تقني في استدعاء الخبير: {str(e)}"

llm = LLMFactory()
