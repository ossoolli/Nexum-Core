import os
import requests, base64, json

class GeminiService:
    def __init__(self, api_key=None, model="gemini-3.1-flash-lite"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}'

    def ask(self, prompt, history=None, system_instruction=None):
        """
        يرسل استفساراً مع دعم كامل لتاريخ المحادثة (History) لإعطاء الوكيل ذاكرة قصيرة المدى.
        """
        contents = history or []
        contents.append({'role': 'user', 'parts': [{'text': prompt}]})
        
        payload = {'contents': contents}
        if system_instruction:
            payload['system_instruction'] = {'parts': [{'text': system_instruction}]}

        try:
            response = requests.post(self.url, json=payload, timeout=30)
            res_json = response.json()

            if 'candidates' in res_json and res_json['candidates'][0].get('content'):
                text_response = res_json['candidates'][0]['content']['parts'][0]['text']
                # إضافة الرد للتاريخ ليعود للمستخدم
                contents.append({'role': 'model', 'parts': [{'text': text_response}]})
                return text_response, contents
            
            print(f"⚠️ Google API Error ({self.model}):")
            print(json.dumps(res_json, indent=2))
            
            error_msg = res_json.get('error', {}).get('message', 'Unknown Error')
            return f"❌ خطأ تقني: {error_msg}", contents

        except Exception as e:
            return f"❌ فشل الاتصال: {str(e)}", history or []
