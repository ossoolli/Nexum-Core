import os
from google import genai
from google.genai import types

class GeminiService:
    def __init__(self, api_key=None, model="gemini-3.1-flash-lite-preview"):
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
        
        # ربط العميل بالمكتبة الرسمية الجديدة (google-genai)
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def ask(self, prompt, history=None, system_instruction=None, file_data=None, mime_type=None):
        if not self.client:
            return "❌ خطأ: مفتاح GOOGLE_API_KEY غير موجود في الإعدادات.", history or []

        contents = []

        # تجميع الرسائل السابقة كسياق
        if history:
            for item in history:
                if 'role' in item and 'parts' in item:
                    role_str = item['role']
                    parts_contents = [p['text'] for p in item['parts'] if 'text' in p]
                    if parts_contents:
                        contents.append(
                            types.Content(
                                role=role_str,
                                parts=[types.Part.from_text(text=t) for t in parts_contents]
                            )
                        )

        # تجهيز الرسالة الحالية مع الملف إذا وجد
        current_parts = []
        if file_data and mime_type:
            try:
                current_parts.append(
                    types.Part.from_bytes(data=file_data, mime_type=mime_type)
                )
            except Exception as e:
                print(f"⚠️ Error attaching file to genai: {e}")
                
        current_parts.append(types.Part.from_text(text=prompt or "Analyze the provided input."))
        
        contents.append(
            types.Content(role='user', parts=current_parts)
        )
        
        # تجهيز إعدادات التوليد بناءً على الأكواد المرفقة منك!
        config_args = {}
        if system_instruction:
            config_args["system_instruction"] = system_instruction
            
        gen_config = types.GenerateContentConfig(**config_args)

        try:
            # استخدام generate_content كما في الوثائق المرفقة
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=gen_config
            )
            
            if response.text:
                # تحديث التاريخ للرد الأخير (مبسط)
                new_history = history.copy() if history else []
                new_history.append({'role': 'user', 'parts': [{'text': prompt}]})
                new_history.append({'role': 'model', 'parts': [{'text': response.text}]})
                return response.text, new_history

            return f"❌ خطأ تقني: لا يوجد نص في الرد.", history or []

        except Exception as e:
            return f"❌ فشل الاتصال العصبي عبر google-genai: {str(e)}", history or []

gemini_service = GeminiService()
