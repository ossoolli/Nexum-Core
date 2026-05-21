import os
import requests, base64, json

class GeminiService:
    def __init__(self, api_key=None, model="gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}'

    def ask(self, prompt, history=None, system_instruction=None, file_data=None, mime_type=None):
        """
        يرسل استفساراً مع دعم كامل لتاريخ المحادثة (History) والملفات المتعددة الوسائط (Multimodal).
        """
        contents = history or []
        
        parts = []
        if prompt:
            parts.append({'text': prompt})
        else:
            parts.append({'text': "الرجاء تحليل هذا الملف."})
            
        if file_data and mime_type:
            parts.append({
                'inline_data': {
                    'mime_type': mime_type,
                    'data': base64.b64encode(file_data).decode('utf-8')
                }
            })
            
        contents.append({'role': 'user', 'parts': parts})        
        payload = {'contents': contents}
        if system_instruction:
            payload['system_instruction'] = {'parts': [{'text': system_instruction}]}

        import time
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = requests.post(self.url, json=payload, timeout=30)
                res_json = response.json()

                if response.status_code == 503:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue

                if 'candidates' in res_json and res_json['candidates'][0].get('content'):
                    text_response = res_json['candidates'][0]['content']['parts'][0]['text']
                    contents.append({'role': 'model', 'parts': [{'text': text_response}]})
                    return text_response, contents
                
                # التقاط رسالة الخطأ بدقة
                error_msg = res_json.get('error', {}).get('message', 'Unknown Error')
                return f"❌ خطأ تقني: {error_msg}", contents

            except Exception as e:
                if attempt == max_retries - 1:
                    return f"❌ فشل الاتصال بعد {max_retries} محاولات: {str(e)}", history or []
                time.sleep(retry_delay)
                retry_delay *= 2
        
        return "❌ النظام مشغول حالياً، يرجى المحاولة لاحقاً.", history or []

# Singleton
gemini_service = GeminiService()
