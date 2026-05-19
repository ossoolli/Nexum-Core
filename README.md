# 🔱 NEXUM CORE OS | Sovereign Agentic Operating System

> **نظام تشغيل سيادي ذكي يعمل على سيرفر خاص.** NEXUM ليس مجرد بوت — بل نواة تنفيذ مستقلة تُخطط، تُحلل، تُنفذ، وتبُث النتائج في الوقت الحقيقي عبر Telegram.

[![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue?style=for-the-badge&logo=telegram)](https://core.telegram.org/bots/api)
[![Version](https://img.shields.io/badge/Version-5.0--SOVEREIGN-gold?style=for-the-badge)](#)
[![AI](https://img.shields.io/badge/AI-Gemini%20+%20Claude-purple?style=for-the-badge&logo=google)](#)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](LICENSE)

---

## 📑 الفهرس

- [الرؤية](#-الرؤية)
- [المعمارية](#%EF%B8%8F-المعمارية)
- [القدرات](#-القدرات)
- [الأوامر](#-الأوامر-والتفاعل)
- [التثبيت](#-التثبيت-والتشغيل)
- [الإعدادات](#%EF%B8%8F-إعدادات-البيئة)
- [هيكل المشروع](#-هيكل-المشروع)
- [استكشاف الأخطاء](#-استكشاف-الأخطاء)
- [خارطة الطريق](#%EF%B8%8F-خارطة-الطريق)
- [المطوّر](#-المطوّر)

---

## 🌌 الرؤية

```
Simple Bot  →  Intelligent Agent  →  Sovereign Operating System
```

بدأ NEXUM كبوت Telegram بسيط، ثم تطوّر ليصبح **نظام تشغيل سيادي** يمتلك:
- 🧠 **عقلاً ذكياً** (Gemini + Claude + OpenRouter)
- 👁️ **رؤية حاسوبية** (تحليل صور وملفات PDF)
- 🛠️ **أيادٍ تنفيذية** (تشغيل أوامر على السيرفر)
- 📡 **صوتاً حياً** (بث مباشر لقناة Telegram)
- 🧬 **ذاكرة دائمة** (سياق محادثة + مؤشرات اقتصادية)
- ⏰ **وعياً زمنياً** (تقارير دورية تلقائية)

---

## 🏗️ المعمارية

```
┌─────────────────────────────────────┐
│         Telegram Interface          │
│   (Text / Photos / Documents)       │
└──────────────┬──────────────────────┘
               ↓
┌──────────────────────────────────────┐
│        NexumInterpreter              │
│  (التصنيف الذكي للطلبات)              │
│  broadcast | monitor | deploy |      │
│  execute   | chat                    │
└──────┬───────┬───────┬───────┬──────┘
       ↓       ↓       ↓       ↓
   ┌───────┐ ┌─────┐ ┌──────┐ ┌────────┐
   │Monitor│ │Deploy│ │Gemini│ │Orchest-│
   │Agent  │ │Agent │ │  AI  │ │rator   │
   └───────┘ └─────┘ └──────┘ └───┬────┘
                                   ↓
                          ┌────────────────┐
                          │  AI Planner    │
                          │ (خطة تنفيذية)  │
                          └───────┬────────┘
                                  ↓
                          ┌────────────────┐
                          │Execution Graph │
                          │   (DAG)        │
                          └───────┬────────┘
                                  ↓
                          ┌────────────────┐
                          │ Tool Registry  │
                          │  + MCP Layer   │
                          └───────┬────────┘
                                  ↓
              ┌───────┬───────┬───────┬──────┐
              │Terminal│ Files │Search │Sandbox│
              └───────┴───────┴───────┴──────┘
```

### المحركات الأساسية

| # | المحرك | الملف | الوصف |
|---|--------|-------|-------|
| 1 | 🔱 **البوابة الموحدة** | `main.py` | نقطة الدخول: أوامر، صور، ملفات، دردشة |
| 2 | 🧠 **المنسق** | `core/orchestrator.py` | تنفيذ الأهداف عبر DAG + بث النتائج |
| 3 | 📋 **المخطط** | `core/planner.py` | تحويل النص لخطة تنفيذية عبر AI |
| 4 | 📊 **الرسم البياني** | `core/execution_graph.py` | DAG يدعم التبعيات والتنفيذ المتوازي |
| 5 | 🛠️ **سجل الأدوات** | `core/tool_registry.py` | Function Calling + MCP Protocol |
| 6 | 🌐 **ناقل الأحداث** | `core/event_bus_distributed.py` | Redis Pub/Sub للتشغيل الموزع |
| 7 | 🔄 **دورة الحياة** | `core/lifecycle.py` | حالات الوكيل: `CREATED→RUNNING→TERMINATED` |
| 8 | 🔐 **الأمان** | `core/security.py` | فلترة أوامر خطرة + تأكيد قبل التنفيذ |
| 9 | 🤖 **Gemini AI** | `services/gemini_service.py` | Multimodal + Retry Logic |
| 10 | 🧬 **OpenRouter** | `core/llm_engine.py` | Claude / GPT-4o / Llama |

---

## 🧠 القدرات

### 1. الإدراك متعدد الحواس (Multimodal)
| النوع | الإجراء |
|-------|---------|
| 📷 **صور** | تحليل تلقائي فوري عبر Gemini Vision |
| 📄 **PDF** | قراءة واستخراج أهم النقاط |
| 📝 **مستندات نصية** | فحص وتحليل المحتوى |
| 🗣️ **نص حر** | دردشة ذكية مع ذاكرة سياقية |

### 2. التنفيذ المستقل (Autonomous Execution)
- **AI Planner** يحول الأوامر النصية لخطط تنفيذية
- **Orchestrator** ينفذ الخطط عبر أدوات النظام
- **أدوات مدمجة:** Terminal، كتابة ملفات، قراءة ملفات، بحث ويب، استخراج صفحات
- **Sandbox** لتنفيذ كود غير موثوق داخل Docker

### 3. البث الحي (Live Broadcasting)
- بث تلقائي لقناة Telegram عند كل عملية
- تقارير صحة دورية (CPU / RAM / Disk)
- مشاركة تحليلات الملفات للقناة بأمر واحد

### 4. الذاكرة الدائمة (Persistent Memory)
- **ذاكرة سياقية** — يتذكر آخر 50 رسالة لكل مستخدم
- **ذاكرة نظام** — مؤشرات اقتصادية وبيانات مخزنة
- **ذاكرة سحابية** — Supabase PostgreSQL (اختياري)

### 5. الأمان (Security Layer)
- حظر أوامر خطيرة (`rm -rf /`, `mkfs`, `reboot`)
- مسار تأكيد للأوامر الحساسة
- حصر الوصول على `ADMIN_ID` فقط
- HTML-escape لكل المخرجات

---

## 💻 الأوامر والتفاعل

### أوامر مباشرة
| الأمر | الوصف |
|-------|-------|
| `/start` · `/dashboard` | لوحة التحكم الرئيسية مع أزرار تفاعلية |
| `/run <أمر>` | تنفيذ أمر Shell مع فحص أمني |

### التفاعل الذكي (بدون أوامر)
| ما تكتبه | ما يحدث |
|----------|---------|
| `مرحبا` | رد ترحيبي قصير وودود |
| `حالة النظام` | تقرير CPU / RAM / Disk / Network / Uptime |
| `ابحث عن سعر الذهب` | تنفيذ عبر Orchestrator + Tool Registry |
| `انشئ تطبيق ويب` | تخطيط وتنفيذ تلقائي في `registry/apps/` |
| `ارفع الكود` | Git add → commit → push تلقائياً |
| `ارسل للقناة` | بث آخر تحليل للقناة الحية |
| صورة 📷 | تحليل فوري بـ Gemini Vision |
| ملف PDF 📄 | تحليل واستخراج النقاط المهمة |

### أزرار لوحة التحكم
| الزر | الوظيفة |
|------|---------|
| 📊 حالة النظام | تقرير صحة السيرفر |
| 🚀 نشر GitHub | رفع التحديثات لـ GitHub |
| 📡 بث تجريبي | إرسال رسالة اختبار للقناة |

---

## 🚀 التثبيت والتشغيل

### المتطلبات
- Python 3.10+
- حساب Telegram Bot ([@BotFather](https://t.me/BotFather))
- مفتاح Google Gemini API
- Redis *(اختياري — للـ Event Bus الموزّع)*

### التثبيت
```bash
git clone https://github.com/ossoolli/Nexum-Core.git
cd Nexum-Core

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### التشغيل اليدوي
```bash
python main.py
```

### التشغيل عبر PM2 (الموصى به للإنتاج)
```bash
pm2 start ecosystem.config.js
pm2 status
```

هذا يشغّل **3 عمليات** مُدارة:
| العملية | الوظيفة |
|---------|---------|
| `nexum-core` | البوت الرئيسي |
| `nexum-runtime-api` | واجهة الويب (FastAPI) |
| `nexum-chronos` | تقارير دورية تلقائية |

### النشر عبر Docker
```bash
docker build -t nexum-core .
docker run -d --env-file .env --name nexum nexum-core
```

---

## ⚙️ إعدادات البيئة

أنشئ ملف `.env` في جذر المشروع:

| المتغير | الوصف | إلزامي |
|---------|------|--------|
| `TELEGRAM_TOKEN` | رمز البوت من BotFather | ✅ |
| `ADMIN_ID` | معرّف Telegram الخاص بك | ✅ |
| `GOOGLE_API_KEY` | مفتاح Gemini API | ✅ |
| `LOG_CHANNEL_ID` | معرّف قناة البث الحي | ⬜ |
| `OPENROUTER_API_KEY` | مفتاح OpenRouter (Claude/GPT) | ⬜ |
| `OPENAI_API_KEY` | مفتاح OpenAI المباشر | ⬜ |
| `DB_CONNECTION` | PostgreSQL DSN | ⬜ |
| `MASTER_KEY` | مفتاح التشفير الداخلي | ⬜ |

```env
TELEGRAM_TOKEN=123456:ABC-DEF...
ADMIN_ID=987654321
GOOGLE_API_KEY=AIza...
LOG_CHANNEL_ID=-100xxxxxxxxxx
```

---

## 📁 هيكل المشروع

```
Nexum-Core/
├── main.py                        # 🔱 البوابة الموحدة (260+ سطر)
├── ecosystem.config.js            # ⚙️ إعدادات PM2 (3 عمليات)
├── requirements.txt               # 📦 المكتبات
├── Dockerfile                     # 🐳 حاوية Docker
├── README.md                      # 📖 هذا الملف
│
├── core/                          # 🧠 النواة
│   ├── orchestrator.py            #    المنسق المركزي + بث حي
│   ├── planner.py                 #    المخطط الذكي (AI → JSON → DAG)
│   ├── execution_graph.py         #    محرك DAG بالتبعيات
│   ├── tool_registry.py           #    سجل الأدوات + MCP Protocol
│   ├── system_tools.py            #    7 أدوات نظام مسجلة
│   ├── executor.py                #    منفذ أوامر Shell
│   ├── sandbox.py                 #    بيئة عزل Docker/gVisor
│   ├── security.py                #    فلترة أوامر خطرة
│   ├── lifecycle.py               #    إدارة دورة حياة الوكلاء
│   ├── event_bus.py               #    ناقل الأحداث
│   ├── event_bus_distributed.py   #    Redis Pub/Sub
│   ├── llm_factory.py             #    مصنع النماذج (Gemini + OpenAI)
│   ├── llm_engine.py              #    محرك OpenRouter
│   ├── memory.py                  #    ذاكرة JSON سريعة
│   ├── memory_local.py            #    ذاكرة سياقية طويلة المدى
│   ├── git_bot.py                 #    مزامنة Git تلقائية
│   ├── agent_registry.py          #    سجل الوكلاء
│   ├── knowledge_base.py          #    قاعدة معرفية
│   ├── reflection.py              #    نظام التأمل الذاتي
│   ├── protocol_compiler.py       #    مترجم البروتوكولات
│   └── search_engine.py           #    محرك بحث ويب
│
├── agents/                        # 🤖 الوكلاء المستقلون
│   ├── chronos.py                 #    ⏰ تقارير دورية + مراقبة صحية
│   ├── monitor.py                 #    📊 مراقبة CPU/RAM/Disk/Network
│   ├── deploy.py                  #    🚀 نشر Git تلقائي
│   ├── docker_agent.py            #    🐳 إدارة حاويات Docker
│   ├── github_agent.py            #    📂 عمليات GitHub
│   ├── frontend_agent.py          #    🖥️ بناء واجهات
│   ├── qa_tester.py               #    🧪 فحص الجودة
│   ├── security_guard.py          #    🛡️ حراسة أمنية
│   └── agent_factory.py           #    🏭 مصنع توليد الوكلاء
│
├── services/                      # 🌐 الخدمات الخارجية
│   ├── gemini_service.py          #    Gemini API + Multimodal + Retry
│   └── db_service.py              #    PostgreSQL / Supabase
│
├── webapp/                        # 🖥️ واجهة التحكم المرئية
│   ├── api_server.py              #    FastAPI + WebSocket
│   └── index.html                 #    Mini App Dashboard
│
├── registry/apps/                 # 📂 التطبيقات المعزولة
└── storage/                       # 💾 البيانات المحلية
```

---

## 🔧 استكشاف الأخطاء

| المشكلة | الحلّ |
|---------|------|
| البوت لا يستجيب | تأكّد من `TELEGRAM_TOKEN` و `ADMIN_ID` صحيحان |
| `Module not found` | شغّل `pip install -r requirements.txt` داخل `venv` |
| أوامر `/run` تفشل | تأكد أن المسارات مطلقة، النظام يعمل على Linux |
| الذاكرة لا تحفظ | تأكد من وجود مجلد `storage/` |
| `503` من Gemini | Exponential Backoff مدمج — انتظر ثوانٍ |
| البث لا يصل للقناة | تأكد أن البوت مضاف كـ Admin في القناة وأن `LOG_CHANNEL_ID` صحيح |
| `ارسل للقناة` لا يرسل التحليل | أرسل ملف/صورة أولاً لحفظ التحليل ثم اكتب `ارسل للقناة` |

---

## 🛣️ خارطة الطريق

### ✅ مكتمل (v5.0)
- [x] نظام تنفيذ مستقل (Orchestrator + DAG + Planner)
- [x] إدراك متعدد الحواس (صور + PDF + مستندات)
- [x] بث مباشر لقناة Telegram
- [x] تقارير صحة دورية (Chronos)
- [x] لوحة تحكم تفاعلية (Inline Keyboards)
- [x] ذاكرة سياقية طويلة المدى
- [x] بحث ويب (DuckDuckGo)
- [x] نظام أمني متعدد الطبقات
- [x] مزامنة Git تلقائية
- [x] PM2 إدارة عمليات (3 عمليات)
- [x] دعم Multi-LLM (Gemini + Claude + GPT)

### 🔜 قادم
- [ ] واجهة ReactFlow لعرض الـ Agent Topology حياً
- [ ] وكيل Sentinel لمراقبة أمن السيرفر
- [ ] متجر تطبيقات داخلي (App Store)
- [ ] Protocol DSL عبر ملفات YAML
- [ ] نظام إشعارات ذكي (تنبيهات حسب الأولوية)
- [ ] Multi-Agent Collaboration (تعاون بين الوكلاء)

---

## 👨‍💻 المطوّر

تم تصميم وبناء هذا المشروع بواسطة **معتز إسماعيل تيلخ (Mutaz Tailakh)**.

[![GitHub](https://img.shields.io/badge/GitHub-ossoolli-black?style=flat-square&logo=github)](https://github.com/ossoolli)

---

*🔱 NEXUM CORE OS v5.0 — Sovereign Agentic Operating System*
