import os
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")

    def query(self, prompt, model="google/gemini-2.5-flash"):
        """محرك استعلامات OpenRouter / Gemini"""
        import requests
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"❌ فشل الاتصال: {str(e)}"

# للاستخدام المباشر
llm_engine = LLMEngine()
