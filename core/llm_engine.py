import os
import requests
import json

class OpenRouterEngine:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def ask(self, prompt, model="anthropic/claude-3.5-sonnet"):
        """يرسل الطلب لـ OpenRouter ويجلب الرد الذكي"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://nexum.os", # اختيارياً
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'], None
        except Exception as e:
            return f"❌ خطأ في الاتصال بـ OpenRouter: {str(e)}", None

class OpenAIEngine:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.url = "https://api.openai.com/v1/chat/completions"

    def ask(self, prompt, model="gpt-5.4-nano"):
        """يرسل الطلب لـ OpenAI ويجلب الرد الذكي"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'], None
        except Exception as e:
            return f"❌ خطأ في الاتصال بـ OpenAI: {str(e)}", None

# Singletons
llm_engine = OpenRouterEngine()
openai_engine = OpenAIEngine()
