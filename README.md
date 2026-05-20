# 🔱 NEXUM CORE OS — v7.2.1 (Agentic)
### Sovereign AI Operating System for Distributed Server Management

---

## 🚀 نظرة عامة (Overview)
Nexum Core هو نظام تشغيل وكيل (Agentic OS) متطور يحول خادمك الشخصي إلى كيان ذكي مستقل. يجمع النظام بين قوة **Gemini Pro** وبنية تحتية مرنة تعتمد على بروتوكولات YAML لإدارة المهام، المواقع، والبوتات.

## 🏗️ الهيكل المعماري الجديد (The New Architecture)
تمت إعادة هندسة النظام في الإصدار v7.2.1 ليعتمد على هيكلية "الحزمة المركزية" لضمان الاستقرار والأمان:

- **`main.py`**: نقطة الانطلاق الرئيسية، مجهزة بنظام **Crash Recovery** لضمان استمرارية الاتصال.
- **`nexum/`**: الحزمة المركزية التي تضم ذكاء النظام:
    - **`config/`**: إدارة الإعدادات عبر Pydantic.
    - **`intelligence/`**: نظام تصنيف النوايا (Gemini Classifier).
    - **`security/`**: تشمل Rate Limiter و Audit Logger.
    - **`memory/`**: إدارة السياق والتلخيص التلقائي للمحادثات.
    - **`protocols/`**: محرك تنفيذ العمليات المؤتمتة عبر YAML.
- **`core/`**: الأدوات المساعدة وخدمات النظام (Orchestrator, Planner).
- **`registry/`**: سجل التطبيقات والبوتات والوكلاء الذين يتم بناؤهم.

## 🛠️ المميزات الرئيسية
- 🧠 **نظام تصنيف النوايا:** فهم دقيق لمراد المستخدم (دردشة، تنفيذ، بناء) بدقة تصل لـ 95%.
- 🛡️ **حماية سيادية:** تقييد معدل الطلبات (Rate Limiting) وسجل تدقيق (Audit Log) لكل حركة.
- ♻️ **استرداد تلقائي:** القدرة على تجاوز الأخطاء التقنية في الاتصال وإعادة التشغيل دون تدخل بشري.
- 📝 **بروتوكولات YAML:** إمكانية تعريف سلاسل مهام معقدة في ملف واحد ليقوم النظام بتنفيذها.

## ⚙️ التثبيت والتشغيل (Setup)
1. قم بتهيئة ملف الإعدادات:
   ```bash
   cp .env.example .env
   ```
   *أضف مفاتيحك (API Keys) في ملف `.env`.*

2. تشغيل النظام:
   ```bash
   python main.py
   ```

3. تشغيل الاختبارات:
   ```bash
   pytest tests/
   ```

## 📜 سجل التغييرات v7.2.1
- [x] إعادة الهيكلة إلى `nexum/` package.
- [x] استبدال Keyword matching بـ Gemini Classifier.
- [x] إضافة نظام Crash Recovery لـ Telegram Polling.
- [x] تفعيل Pydantic Settings لإدارة الـ Environment.
- [x] إضافة نظام Audit و Rate Limiting.

---
**NEXUM — The Future is Sovereign.** 🔱
