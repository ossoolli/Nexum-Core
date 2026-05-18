import requests, base64, json

class GeminiService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={self.api_key}'

    def ask(self, prompt, image_data=None, system_instruction=None):
        contents = [{'parts': [{'text': prompt}]}]
        if image_data:
            contents[0]['parts'].append({
                'inline_data': {
                    'mime_type': 'image/jpeg',
                    'data': base64.b64encode(image_data).decode('utf-8')
                }
            })
        
        payload = {'contents': contents}
        if system_instruction:
            payload['system_instruction'] = {'parts': [{'text': system_instruction}]}

        try:
            response = requests.post(self.url, json=payload, timeout=30)
            res_json = response.json()

            if 'candidates' in res_json and res_json['candidates'][0].get('content'):
                return res_json['candidates'][0]['content']['parts'][0]['text']
            
            print("⚠️ Google API Response Error:")
            print(json.dumps(res_json, indent=2))
            
            if 'error' in res_json:
                return f"❌ خطأ من جوجل: {res_json['error']['message']}"
            return "❌ الرد محجوب أو غير مكتمل"

        except Exception as e:
            return f"❌ فشل الاتصال: {str(e)}"
