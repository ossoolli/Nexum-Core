# 🔱 NEXUM CORE OS v2.0
> **The Sovereign Operating System for Telegram** — Full control over your servers and containers with AI-powered intelligence.

---

## 🌟 الميزات الرئيسية (Key Features)

### 🎛️ لوحة تحكم تفاعلية (Interactive UI/UX)
- **نظام أزرار شامل**: تحكم كامل في السيرفر عبر أزرار Inline مرتبة ومنظمة.
- **منسق رسائل ذكي**: تقارير حالة النظام بترميز HTML جميل وأشرطة تقدم (Progress Bars) مرئية.

### 🌐 تطبيق تلجرام المصغر (Telegram Mini App)
- **Dashboard WebView**: واجهة ويب عصرية تُفتح داخل تلجرام مباشرة.
- **Real-time Monitoring**: مراقبة حية لـ CPU، RAM، والقرص.
- **Embedded Terminal**: تنفيذ الأوامر مباشرة من واجهة الويب.

### 🐳 إدارة Docker المتقدمة
- **Container Control**: تشغيل، إيقاف، وإعادة تشغيل الحاويات بضغطة زر.
- **Log Streaming**: سحب سجلات الحاويات وقراءتها فوراً.
- **Resource Stats**: مراقبة استهلاك كل حاوية للموارد.

### 🤖 ذكاء اصطناعي متعدد المحركات
- **Gemini 2.5 Flash**: للمحادثات السريعة والذكية.
- **GPT-4o Expert**: للتحليل البرمجي العميق وحل المشكلات المعقدة.
- **AI Planner**: تحويل الأهداف النصية إلى خطوات تنفيذية DevOps تلقائية.

---

## 🚀 التشغيل (Deployment)

### 1️⃣ المتطلبات
- Python 3.10+
- Docker (اختياري، لإدارة الحاويات)
- Telegram Bot Token

### 2️⃣ التثبيت
```bash
# تثبيت المكتبات المطلوبة
pip install -r requirements.txt
```

### 3️⃣ الإعداد (.env)
قم بضبط المفاتيح التالية في ملف `.env`:
- `TELEGRAM_TOKEN`: توكن البوت من BotFather.
- `ADMIN_ID`: معرف التلجرام الخاص بك (للحماية).
- `GOOGLE_API_KEY`: مفتاح Gemini.
- `OPENAI_API_KEY`: مفتاح OpenAI.

### 4️⃣ التشغيل
```bash
# تشغيل البوت الأساسي
python main.py

# تشغيل خادم لوحة التحكم (WebApp API)
python webapp/api_server.py
```

---

## 🛠️ هيكلية المشروع (Project Structure)
- `core/`: النواة (الأمان، المنفذ، المخطط، الأزرار).
- `agents/`: الوكلاء المتخصصون (المراقبة، النشر، Docker).
- `webapp/`: ملفات تطبيق الويب المصغر.
- `services/`: خدمات الاتصال بالذكاء الاصطناعي.

---

## 🛡️ الأمان (Security)
نظام **NEXUM** مزود بفلتر أمان يمنع الأوامر التخريبية ويطلب تأكيداً يدوياً قبل تنفيذ العمليات الحساسة (مثل `rm -rf`).

---
✨ *تم تطويره بواسطة AI لخدمة المايسترو.*