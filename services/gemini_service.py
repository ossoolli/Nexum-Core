import os
import requests, base64, json

class GeminiService:
    def __init__(self, api_key=None, model="gemini-1.5-flash"): # نستخدم 1.5-flash لدعمه الممتاز للصور والملفات
        if api_key:
            raw_key = api_key
        else:
            from nexum.config import config
            raw_key = config.google_api_key if config else os.getenv("GOOGLE_API_KEY", "")
        self.api_key = raw_key.strip() 
        self.model = model
        self.url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}'

    def ask(self, prompt, history=None, system_instruction=None, file_data=None, mime_type=None):
        if not self.api_key:
            return "❌ خطأ: مفتاح GOOGLE_API_KEY غير موجود.", history or []

        contents = []
        if history:
            for item in history:
                contents.append(item)

        parts = []
        
        # إضافة المدخلات التقنية (صورة أو ملف) إذا وجدت
        if file_data:
            encoded_file = base64.b64encode(file_data).decode('utf-8')
            parts.append({
                "inline_data": {
                    "mime_type": mime_type or "image/jpeg",
                    "data": encoded_file
                }
            })
            
        parts.append({'text': prompt or "Analyze this input and act according to NEXUM OS protocols."})
        contents.append({'role': 'user', 'parts': parts})        
        
        payload = {'contents': contents}
        if system_instruction:
            payload['system_instruction'] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            response = requests.post(self.url, json=payload, timeout=60)
            res_json = response.json()

            if 'candidates' in res_json and res_json['candidates'][0].get('content'):
                text_response = res_json['candidates'][0]['content']['parts'][0]['text']
                return text_response, contents
            
            error_msg = res_json.get('error', {}).get('message', 'Unknown API Error')
            return f"❌ خطأ تقني في العقل المدبر: {error_msg}", contents

        except Exception as e:
            return f"❌ فشل الاتصال العصبي: {str(e)}", history or []

gemini_service = GeminiService()
