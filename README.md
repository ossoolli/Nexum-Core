# 🔱 NEXUM PRIME | Sovereign Agentic Operating System

> **نظام تشغيل سيادي للوكلاء المستقلين.** NEXUM PRIME ليس مجرد بوت — بل بيئة تنفيذ ذكية حيث يخطّط وكلاء AI، يبنون، وينشرون أنظمة برمجية بشكل مستقل عبر واجهة تفاعلية كاملة.

[![Deploy](https://img.shields.io/badge/Live-GitHub%20Pages-blue?style=for-the-badge&logo=github)](https://ossoolli.github.io/Nexum-Core/)
[![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue?style=for-the-badge&logo=telegram)](https://core.telegram.org/bots/api)
[![Version](https://img.shields.io/badge/Version-2.2--STABLE-orange?style=for-the-badge)](#)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](LICENSE)

---

## 📑 الفهرس

- [الرؤية](#-الرؤية)
- [المعمارية](#%EF%B8%8F-المعمارية-9-layer-architecture)
- [لوحة التحكم التفاعلية](#-لوحة-التحكم-التفاعلية-click-first-ux)
- [Mini App Dashboard](#-mini-app-dashboard)
- [القدرات الذكية](#-القدرات-الذكية)
- [مرجع الأوامر](#-مرجع-الأوامر)
- [التثبيت والتشغيل](#-التثبيت-والتشغيل)
- [إعدادات البيئة](#%EF%B8%8F-إعدادات-البيئة)
- [هيكل المشروع](#-هيكل-المشروع)
- [استكشاف الأخطاء](#-استكشاف-الأخطاء-troubleshooting)
- [خارطة الطريق](#%EF%B8%8F-خارطة-الطريق)
- [المطور](#-المطور)

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
| 1 | 🧠 **Orchestrator & DAG** | تنفيذ المهام بنظام الرسم البياني الموجّه مع إعادة المحاولة |
| 2 | 🌐 **Distributed Event Bus** | النظام العصبي — Redis Pub/Sub للبث اللحظي |
| 3 | 🔄 **Agent Lifecycle** | آلة حالة: `CREATED → READY → RUNNING → TERMINATED` |
| 4 | 🔐 **Permission Manager** | نظام صلاحيات RBAC |
| 5 | 📊 **Runtime State** | مصدر الحقيقة الموحّد في الذاكرة + السحابة |
| 6 | 🔀 **Callback Router** | موجّه تفاعلي لجميع الأزرار والقوائم |
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
- **Smart Error Handling** — أخطاء مغلّفة بـ HTML آمن

---

## 📱 Mini App Dashboard

تطبيق ويب مصغّر داخل تليجرام بتصميم فاخر:

- **Dark Futuristic UI** مع Glassmorphism وتدرّجات Neon
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
- 📄 **PDF والمستندات** — قراءة وتلخيص
- 🎵 **الصوت** — استقبال ومعالجة
- 📝 **الكود** — فحص وتعديل أي ملف برمجي
- 📑 **الملفات النصية** — قراءة تلقائية لـ `.py .js .html .css .json .md .csv .yml .sh`

### البحث والويب (Web Intelligence)
- 🔍 **`/search`** — بحث حي في الإنترنت
- 🕸️ **`/scrape`** — شفط وقراءة محتوى أي رابط
- 📝 **`/code`** — توليد كود بالذكاء الاصطناعي

### الاستقلالية (Sovereign Autonomy)
- اتخاذ القرارات دون توقّف
- Exponential Backoff ضدّ أخطاء 503
- وعي لحظي بحالة السيرفر (CPU/RAM/Files)
- ذاكرة سحابية دائمة (Supabase)

### الأمان (Safety Layer)
- فحص أوامر حساسة قبل التنفيذ
- مسار تأكيد عبر `/confirm` و `/cancel`
- حصر الوصول على `ADMIN_ID` فقط
- HTML-escape لكل ناتج معروض

---

## 💻 مرجع الأوامر

| الأمر | الوصف | مثال |
|-------|------|------|
| `/start` · `/menu` · `/dashboard` · `/home` | فتح لوحة التحكم الرئيسية | `/start` |
| `/run <cmd>` | تنفيذ أمر نظام (مع فحص أمان) | `/run ls -la` |
| `/confirm` | تأكيد آخر أمر حسّاس معلّق | `/confirm` |
| `/cancel` | إلغاء آخر أمر معلّق | `/cancel` |
| `/search <query>` | بحث ويب فوري | `/search latest LLM benchmarks` |
| `/scrape <url>` | استخراج محتوى صفحة | `/scrape https://example.com` |
| `/code <description>` | توليد كود بالـ AI | `/code خادم Flask بسيط` |

### التفاعل النصي

- أرسل **رسالة عادية** للدردشة مع الذكاء الاصطناعي مع وعي بحالة النظام
- أرسل **صورة/PDF/صوت/مستند** للتحليل متعدد الحواس
- ابدأ رسالة بكلمات تنفيذ صريحة (`ابن`, `أنشئ`, `نفّذ`, `build`, `create`, `spawn`, `deploy`) لتشغيل الـ Orchestrator

---

## 🚀 التثبيت والتشغيل

### 1. المتطلبات
- Python 3.10+
- حساب Telegram Bot ([@BotFather](https://t.me/BotFather))
- مفتاح Google Gemini API
- PostgreSQL / Supabase *(اختياري — للذاكرة السحابية)*
- Redis *(اختياري — للـ Event Bus الموزّع)*

### 2. التثبيت
```bash
git clone https://github.com/ossoolli/Nexum-Core.git
cd Nexum-Core

python3 -m venv venv
source venv/bin/activate          # Linux/macOS
# .\venv\Scripts\Activate.ps1     # Windows PowerShell

pip install -r requirements.txt
```

### 3. الإقلاع
```bash
# المحرك الأساسي (Bot + AI)
python main.py

# خادم الواجهة المرئية (اختياري)
python webapp/api_server.py
```

### 4. النشر عبر Docker
```bash
docker build -t nexum-prime .
docker run -d --env-file .env --name nexum nexum-prime
```

---

## ⚙️ إعدادات البيئة

أنشئ ملف `.env` في جذر المشروع:

| المتغير | الوصف | إلزامي |
|---------|------|--------|
| `TELEGRAM_TOKEN` | رمز البوت من BotFather | ✅ |
| `ADMIN_ID` | معرّف Telegram الخاص بك (Numeric) | ✅ |
| `GOOGLE_API_KEY` | مفتاح Gemini API | ✅ |
| `WEBAPP_URL` | رابط Mini App Dashboard | ⬜ |
| `DB_CONNECTION` | PostgreSQL DSN للذاكرة السحابية | ⬜ |
| `SUPABASE_URL` | عنوان مشروع Supabase | ⬜ |
| `SUPABASE_KEY` | مفتاح Supabase | ⬜ |
| `REDIS_URL` | عنوان Redis للـ Event Bus | ⬜ |

مثال:
```env
TELEGRAM_TOKEN=123456:ABC-DEF...
ADMIN_ID=987654321
GOOGLE_API_KEY=AIza...
WEBAPP_URL=https://ossoolli.github.io/Nexum-Core/
```

---

## 📁 هيكل المشروع

```
Nexum-Core/
├── main.py                    # القلب النابض — Interactive Control System
├── requirements.txt           # التبعيات
├── Dockerfile                 # حاوية الإنتاج
├── .env                       # المتغيرات البيئية (لا يُرفع)
├── core/
│   ├── keyboards.py           # 9 قوائم تفاعلية + بطاقات وكلاء
│   ├── callback_router.py     # موجّه الأحداث
│   ├── orchestrator.py        # المنسّق التنفيذي (DAG)
│   ├── planner.py             # المخطّط الذكي (AI Planner)
│   ├── lifecycle.py           # مدير دورة حياة الوكلاء
│   ├── event_bus.py           # ناقل الأحداث
│   ├── event_bus_distributed.py  # Redis Pub/Sub
│   ├── runtime_state.py       # حالة النظام اللحظية
│   ├── system_tools.py        # Terminal, Files, Web, Search
│   ├── safe_sender.py         # طبقة أمان الرسائل
│   ├── executor.py            # منفّذ الأوامر (cross-platform)
│   ├── security.py            # فاحص الأوامر الخطرة
│   ├── permission_manager.py  # RBAC
│   ├── protocol_compiler.py   # مُجمّع البروتوكولات الذاتية
│   ├── reflection.py          # طبقة التأمّل الذاتي
│   └── agent_registry.py      # سجل الوكلاء
├── services/
│   ├── gemini_service.py      # Gemini AI مع Retry Logic
│   └── db_service.py          # PostgreSQL/Supabase
├── agents/
│   ├── monitor.py             # وكيل المراقبة
│   ├── deploy.py              # وكيل النشر
│   ├── docker_agent.py        # وكيل الحاويات
│   ├── frontend_agent.py      # وكيل الواجهات
│   ├── github_agent.py        # وكيل GitHub
│   └── agent_factory.py       # مصنع توليد الوكلاء
├── webapp/
│   ├── api_server.py          # FastAPI + WebSocket + SSE
│   └── index.html             # Mini App Dashboard
└── storage/
    └── memory.json            # ذاكرة محلية
```

---

## 🔧 استكشاف الأخطاء (Troubleshooting)

| المشكلة | الحلّ |
|---------|------|
| البوت لا يستجيب | تأكّد أن `TELEGRAM_TOKEN` و `ADMIN_ID` صحيحان وأن معرّفك يطابق `ADMIN_ID` |
| `Module not found` | شغّل `pip install -r requirements.txt` داخل بيئة `venv` |
| أوامر `/run` تفشل على Windows | تم دعمها — يستخدم `cmd.exe` تلقائياً على Windows و `/bin/bash` على Linux |
| `Docker غير متوفر` | تأكّد من تثبيت Docker وأنّ المستخدم لديه صلاحية `docker.sock` |
| الذاكرة السحابية تظهر OFFLINE | تحقّق من `DB_CONNECTION` و `SUPABASE_URL/KEY` في `.env` |
| `503` من Gemini | الـ Exponential Backoff يعالجها — انتظر بضع ثوانٍ وأعد المحاولة |
| النصوص العربية تظهر مشوّهة في المحرر | اضبط المحرر على ترميز UTF-8 — الملفات مُرمّزة بشكل صحيح |

---

## 🛣️ خارطة الطريق

- [x] نظام وكلاء مستقل (Autonomous Agents)
- [x] واجهة تفاعلية Click-first (9 قوائم)
- [x] إدراك متعدد الحواس (Multimodal)
- [x] بحث وسكرابينج من الويب
- [x] ذاكرة سحابية دائمة (Supabase)
- [x] Mini App Dashboard (Glassmorphism)
- [x] Exponential Backoff للـ API
- [x] دعم Cross-platform (Linux/Windows/Docker)
- [x] مسار تأكيد للأوامر الحسّاسة (`/confirm` · `/cancel`)
- [ ] Runtime Visual Graph (Cytoscape.js / React Flow)
- [ ] Real-time Notifications System
- [ ] Command Palette (CMD+K style)
- [ ] Multi-View System (System/Agent/Protocol/Security)

---

## 👨‍💻 المطوّر

تم تطوير هذا المشروع بواسطة **معتز اسماعيل تيلخ (Mutaz Tailakh)**.

[![GitHub](https://img.shields.io/badge/GitHub-ossoolli-black?style=flat-square&logo=github)](https://github.com/ossoolli)

---

*🔱 NEXUM PRIME — Sovereign Agentic OS v2.2-STABLE*
