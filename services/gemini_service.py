import os
import requests, base64, json

class GeminiService:
    def __init__(self, api_key=None, model="gemini-pro"): # تغيير إلى الطراز الكلاسيكي المستقر
        raw_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        self.api_key = raw_key.strip() 
        self.model = model
        # استخدام v1 لزيادة التوافق والاستقرار
        self.url = f'https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}'

    def ask(self, prompt, history=None, system_instruction=None, file_data=None, mime_type=None):
        if not self.api_key:
            return "❌ خطأ: مفتاح GOOGLE_API_KEY غير موجود.", history or []

        contents = []
        # تحويل التاريخ للتنسيق الكلاسيكي
        if history:
            for item in history:
                contents.append(item)

        parts = [{'text': prompt or "Hello"}]
        contents.append({'role': 'user', 'parts': parts})        
        
        payload = {'contents': contents}
        # Note: gemini-pro (v1) doesn't always support system_instruction in the same way as v1beta
        # So we include it in the first message if needed

        try:
            response = requests.post(self.url, json=payload, timeout=30)
            res_json = response.json()

            if 'candidates' in res_json and res_json['candidates'][0].get('content'):
                text_response = res_json['candidates'][0]['content']['parts'][0]['text']
                return text_response, contents
            
            error_msg = res_json.get('error', {}).get('message', 'Unknown Error')
            return f"❌ خطأ تقني: {error_msg}", contents

        except Exception as e:
            return f"❌ فشل الاتصال: {str(e)}", history or []

# Singleton
gemini_service = GeminiService()
