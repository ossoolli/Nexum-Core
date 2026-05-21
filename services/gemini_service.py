import os
import requests, base64, json

class GeminiService:
    def __init__(self, api_key=None, model="gemini-1.5-flash"):
        if api_key:
            raw_key = api_key
        else:
            try:
                from nexum.config import config
                raw_key = config.google_api_key if config else os.getenv("GOOGLE_API_KEY", "")
            except ImportError:
                raw_key = os.getenv("GOOGLE_API_KEY", "")
        
        self.api_key = raw_key.strip() if raw_key else ""
        self.model = model
        self.url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}'

    def ask(self, prompt, history=None, system_instruction=None, file_data=None, mime_type=None):
        if not self.api_key:
            return "❌ خطأ: مفتاح GOOGLE_API_KEY غير موجود في الإعدادات.", history or []

        contents = []
        if history:
            # تنظيف التاريخ لضمان التوافق مع API
            # 🔱 NEXUM CORE OS v3.5.0 — The Sovereign Architect
            for item in history:
                if 'role' in item and 'parts' in item:
                    contents.append(item)

        parts = []
        
        # إضافة الملف التقني (صورة أو مستند)
        if file_data:
            try:
                encoded_file = base64.b64encode(file_data).decode('utf-8')
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type or "image/jpeg",
                        "data": encoded_file
                    }
                })
            except Exception as e:
                print(f"⚠️ Error encoding file: {e}")
            
        parts.append({'text': prompt or "Analyze the provided input."})
        contents.append({'role': 'user', 'parts': parts})        
        
        payload = {'contents': contents}
        if system_instruction:
            payload['systemInstruction'] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            response = requests.post(self.url, json=payload, timeout=60)
            res_json = response.json()

            if 'candidates' in res_json and res_json['candidates'][0].get('content'):
                text_response = res_json['candidates'][0]['content']['parts'][0]['text']
                return text_response, contents
            
            error_data = res_json.get('error', {})
            error_msg = error_data.get('message', 'Unknown API Error')
            error_status = error_data.get('status', 'ERROR')
            
            return f"❌ خطأ تقني ({error_status}): {error_msg}", contents

        except Exception as e:
            return f"❌ فشل الاتصال العصبي: {str(e)}", history or []

gemini_service = GeminiService()
