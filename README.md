# 🔱 NEXUM PRIME | Sovereign Agentic Operating System

> **نظام تشغيل سيادي للوكلاء المستقلين.** NEXUM PRIME ليس مجرد بوت — بل هو بيئة تنفيذ ذكية حيث يقوم وكلاء AI بتخطيط، بناء، ونشر أنظمة برمجية بشكل مستقل تماماً عبر واجهة تفاعلية بالكامل.

[![Deploy](https://img.shields.io/badge/Live-GitHub%20Pages-blue?style=for-the-badge&logo=github)](https://ossoolli.github.io/Nexum-Core/)
[![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue?style=for-the-badge&logo=telegram)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](LICENSE)

---

## 🌌 الرؤية

```
Command Bot  →  Interactive Sovereign Control System
```

NEXUM تحوّل من بوت تليجرام تقليدي إلى **نظام تشغيل سيادي تفاعلي** يعمل بالكامل عبر النقر، البطاقات، والقوائم الديناميكية بدلاً من الأوامر النصية.

---

## 🏗️ المعمارية (9-Layer Architecture)

```
Telegram (Control Plane)
    ↓
Interactive Click-first UX Layer
    ↓
FastAPI (Runtime Gateway)
    ↓
Event Bus (Nervous System)
    ↓
Runtime State (Source of Truth)
    ↓
Agents (Autonomous Workers)
    ↓
Orchestrator (Executive Brain)
    ↓
Mini App (Visual Operating System)
    ↓
Protocol Engine (Self-Evolving Infrastructure)
```

### المحركات الأساسية

| # | المحرك | الوصف |
|---|--------|-------|
| 1 | 🧠 **Orchestrator & DAG** | تنفيذ المهام بنظام الرسم البياني الموجه مع إعادة المحاولة |
| 2 | 🌐 **Distributed Event Bus** | النظام العصبي — Redis Pub/Sub للبث اللحظي |
| 3 | 🔄 **Agent Lifecycle** | آلة حالة: `CREATED → READY → RUNNING → TERMINATED` |
| 4 | 🔐 **Permission Manager** | نظام صلاحيات RBAC |
| 5 | 📊 **Runtime State** | مصدر الحقيقة الموحد في الذاكرة + السحابة |
| 6 | 🔀 **Callback Router** | موجه تفاعلي لجميع الأزرار والقوائم |
| 7 | 🧠 **AI Planner** | مخطط ذكي يولّد Execution Graphs تلقائياً |
| 8 | 🛠️ **System Tools** | أدوات: Terminal, Files, Web Search, Scraping |
| 9 | ☁️ **Cloud Memory** | ذاكرة دائمة عبر Supabase PostgreSQL |

---

## 🎮 لوحة التحكم التفاعلية (Click-first UX)

النظام يعمل بالكامل عبر **النقر** — لا حاجة للكتابة:

```
/start → القائمة الرئيسية
  ├── ⚡ Runtime       → حالة النظام، مقاييس حية، Event Bus
  ├── 🤖 Agents        → بطاقة تحكم لكل وكيل (Start/Stop/Restart/Logs/Memory)
  ├── 🧬 Protocols     → البروتوكولات + Execution Graph
  ├── 🚀 Deployments   → Git Status / Push / GitHub Pages / Cloud Run
  ├── 🧠 AI Brain      → Chat / Web Search / Scrape / Code Generation
  ├── 🛡️ Security      → Lockdown / Audit / Integrity Check
  ├── 💾 Memory        → DB Status / Cloud Sync / Clear History
  ├── 🐳 Docker        → Containers / Images / Stats / Prune
  └── ⚙️ Settings      → System Info / AI Model / Restart Bot
```

### مميزات الـ UX

- **Inline Keyboards** في كل شاشة — 9 قوائم فرعية متداخلة
- **Agent Cards** — بطاقة تحكم لكل وكيل مع أزرار مباشرة
- **Confirmation Dialogs** — تأكيد قبل الإجراءات الخطيرة
- **Visual Progress Bars** — أشرطة تقدم نصية للـ CPU/RAM/Disk
- **Quick Actions Panel** — إجراءات سريعة بنقرة واحدة
- **Smart Error Handling** — أخطاء مغلفة بـ HTML آمن

---

## 📱 Mini App Dashboard

تطبيق ويب مصغر داخل تليجرام بتصميم فاخر:

- **Dark Futuristic UI** مع Glassmorphism وتدرجات Neon
- **Live Terminal Feed** — سجل أحداث حي بنمط التيرمينال
- **Swarm Control** — إدارة الوكلاء مع مؤشرات حية
- **Cloud Intelligence** — لوحة حالة الذاكرة السحابية
- **Quick Protocols** — بروتوكولات جاهزة بنقرة واحدة
- **WebSocket Live** — اتصال حي مع السيرفر

🔗 **رابط المعاينة:** [https://ossoolli.github.io/Nexum-Core/](https://ossoolli.github.io/Nexum-Core/)

---

## 🧠 القدرات الذكية

### الإدراك متعدد الحواس (Multimodal)
- 📷 **الصور** — تحليل ومعالجة
- 📄 **PDF & المستندات** — قراءة وتلخيص
- 🎵 **الصوت** — استقبال ومعالجة
- 📝 **الكود** — فحص وتعديل أي ملف برمجي

### البحث والويب (Web Intelligence)
- 🔍 **`/search`** — بحث حي في الإنترنت عبر DuckDuckGo
- 🕸️ **`/scrape`** — شفط وقراءة محتوى أي رابط
- 📝 **`/code`** — توليد كود بالذكاء الاصطناعي

### الاستقلالية (Sovereign Autonomy)
- اتخاذ القرارات دون توقف
- Exponential Backoff ضد أخطاء 503
- وعي لحظي بحالة السيرفر (CPU/RAM/Files)
- ذاكرة سحابية دائمة (Supabase)

---

## 🚀 التثبيت والتشغيل

### 1. المتطلبات
- Python 3.10+
- حساب Telegram Bot ([@BotFather](https://t.me/BotFather))
- مفتاح Google Gemini API
- PostgreSQL / Supabase (اختياري — للذاكرة السحابية)

### 2. إعدادات البيئة (`.env`)
```env
TELEGRAM_TOKEN=your_bot_token
ADMIN_ID=your_telegram_user_id
GOOGLE_API_KEY=your_gemini_api_key
WEBAPP_URL=https://ossoolli.github.io/Nexum-Core/

# اختياري — للذاكرة السحابية
DB_CONNECTION=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_key
```

### 3. التثبيت
```bash
git clone https://github.com/ossoolli/Nexum-Core.git
cd Nexum-Core

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. الإقلاع
```bash
# المحرك الأساسي (Bot + AI)
python main.py

# خادم الواجهة المرئية (اختياري)
python webapp/api_server.py
```

---

## 📁 هيكل المشروع

```
Nexum-Core/
├── main.py                    # القلب النابض — Interactive Control System
├── requirements.txt           # التبعيات
├── .env                       # المتغيرات البيئية
├── core/
│   ├── keyboards.py           # 9 قوائم تفاعلية + بطاقات وكلاء
│   ├── callback_router.py     # موجه الأحداث
│   ├── orchestrator.py        # المنسق التنفيذي (DAG)
│   ├── planner.py             # المخطط الذكي (AI Planner)
│   ├── lifecycle.py           # مدير دورة حياة الوكلاء
│   ├── event_bus.py           # ناقل الأحداث
│   ├── runtime_state.py       # حالة النظام اللحظية
│   ├── system_tools.py        # أدوات: Terminal, Files, Web, Search
│   ├── safe_sender.py         # طبقة أمان الرسائل
│   ├── executor.py            # منفذ الأوامر
│   └── agent_registry.py      # سجل الوكلاء
├── services/
│   ├── gemini_service.py      # Gemini AI مع Retry Logic
│   └── db_service.py          # ذاكرة سحابية (PostgreSQL/Supabase)
├── agents/
│   ├── monitor.py             # وكيل المراقبة
│   ├── deploy.py              # وكيل النشر
│   └── docker_agent.py        # وكيل الحاويات
├── webapp/
│   ├── api_server.py          # FastAPI + WebSocket + SSE
│   └── index.html             # Mini App Dashboard
└── storage/
    └── memory.json            # ذاكرة محلية
```

---

## 🛣️ خارطة الطريق

- [x] نظام وكلاء مستقل (Autonomous Agents)
- [x] واجهة تفاعلية Click-first (9 قوائم)
- [x] إدراك متعدد الحواس (Multimodal)
- [x] بحث وسكرابينج من الويب
- [x] ذاكرة سحابية دائمة (Supabase)
- [x] Mini App Dashboard (Glassmorphism)
- [x] Exponential Backoff للـ API
- [ ] Runtime Visual Graph (Cytoscape.js / React Flow)
- [ ] Real-time Notifications System
- [ ] Command Palette (CMD+K style)
- [ ] Multi-View System (System/Agent/Protocol/Security)

---

## 👨‍💻 المطور

تم تطوير هذا المشروع بواسطة **معتز اسماعيل تيلخ (Mutaz Tailakh)**.

[![GitHub](https://img.shields.io/badge/GitHub-ossoolli-black?style=flat-square&logo=github)](https://github.com/ossoolli)

---

*🔱 NEXUM PRIME — Sovereign Agentic OS v2.2-STABLE*