# 🔱 NEXUM CORE OS — v7.3.0 (The Sovereign Union)
> **نظام تشغيل وكيل سيادي (Sovereign Agentic OS) — العقل المركزي لإدارة السيرفرات والبناء الذاتي.**

[![Version](https://img.shields.io/badge/Version-7.3.0--SOVEREIGN-gold?style=for-the-badge)](#)
[![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)](https://python.org)
[![AI](https://img.shields.io/badge/AI-Gemini%201.5%20Pro-purple?style=for-the-badge&logo=google)](#)
[![Stability](https://img.shields.io/badge/Stability-Resilient%20Core-blue?style=for-the-badge)](#)

---

## 🌌 الرؤية (The Vision)
NEXUM ليس مجرد بوت تلجرام؛ إنه **نظام تشغيل وكيل (Agentic OS)** مستقل. بدأت الرؤية في v5.0 وبنظام التنفيذ المستقل، وتطورت في v7.1 لتشمل بناء المواقع والوكلاء، ووصلت في **v7.3.0** إلى حالة "الاتحاد السيادي" حيث تلتقي استقرارية البنية التحتية مع عراقة الوظائف التشغيلية.

```
History (v5.0) + Philosophy (v7.1) + Modernity (v7.2.1) = Sovereign Mastery (v7.3.0)
```

---

## 🏗️ الهيكلية الهجينة (The Union Architecture)
يعمل النظام في v7.3.0 بهيكلية "العصب المركزي" (Nervous System) حيث يربط ملف `main.py` بين ثلاث طبقات:

1.  **الطبقة النواتية (`nexum/` Package)**:
    *   `Intelligence`: مصنف النوايا يعتمد على Gemini (بدلاً من الكلمات المفتاحية).
    *   `Security`: درع الحماية (Rate Limiter) وسجل التدقيق (Audit Log).
    *   `Memory`: نظام تلخيص ذكي لإدارة نافذة السياق (Summarizer).
    *   `Kernel`: نظام الإقلاع (Bootstrap) واسترداد الانهيار (Crash Recovery).

2.  **الطبقة التخطيطية (`core/`)**:
    *   `Orchestrator`: تنفيذ المهام عبر رسوم بيانية (DAG).
    *   `Planner`: تحويل الأوامر النصية إلى خطط عمل JSON.
    *   `Router`: موجه مركزي للتحكم بـ Callbacks لوحة التحكم.

3.  **الطبقة التنفيذية (`agents/`)**:
    *   `WebForge`: بناء مواقع ويب كاملة في ثوانٍ.
    *   `AgentSmith`: تصميم وبناء وكلاء أذكياء متخصصين.
    *   `BotBuilder`: توليد بوتات تلجرام بشخصيات فريدة.
    *   `ChannelManager`: إدارة البث والنشر عبر القنوات.

---

## 🛠️ المحركات السيادية (Sovereign Engines)

| المحرك | الملف | الوصف |
| :--- | :--- | :--- |
| 🔱 **المحرّك الرابط** | `main.py` | يجمع كل الأسلاك، يعالج الرسائل، ويوجه الوكلاء. |
| 🧠 **المصنّف الذكي** | `classifier.py` | يفهم نية المستخدم بدقة (بناء، تنفيذ، مراقبة، دردشة). |
| 🌐 **WebForge** | `webforge_agent.py` | يبني Landing Pages و Dashboards و APIs فوراً. |
| 🤖 **AgentSmith** | `agent_smith.py` | يصمم ويبني ويشغل وكلاء مخصصين من وصف نصي. |
| 📡 **البث الحي** | `broadcast()` | يبث إشعارات النظام لقناة التلجرام في الوقت الحقيقي. |
| 🛡️ **درع الاستقرار** | `Crash Recovery` | حلقة مغلقة تضمن استمرار البوت حتى عند انقطاع الشبكة. |

---

## 📱 لوحة التحكم الشاملة (The Dashboard)
عند إرسال `/start` أو `/dashboard` تظهر اللوحة السيادية المكونة من 7 أزرار حيوية:

*   📊 **النبض (Status)**: تقرير فوري لموارد السيرفر (CPU, RAM, Disk).
*   🚀 **نشر GitHub**: رفع التحديثات ومزامنة الكود بضغطة زر.
*   🌐 **المواقع**: قائمة بكافة المشاريع التي بناها WebForge.
*   🤖 **الوكلاء**: إدارة الوكلاء الذين صممهم AgentSmith.
*   🤖 **البوتات**: التحكم بأسطول البوتات الفرعية (BotFleet).
*   📢 **القنوات**: إدارة القنوات وجدولة المنشورات.
*   📡 **قناة البث**: اختبار حلقة الوصل مع قناة العمليات.

---

## 🛠️ التثبيت والتشغيل (Setup)

### 1. إعداد البيئة
```bash
# 1. تهيئة ملف الإعدادات
cp .env.example .env

# 2. تنصيب المتطلبات
pip install -r requirements.txt
```

### 2. التشغيل المستقر
```bash
# التشغيل المباشر
python main.py

# أو عبر PM2 (الموصى به للإنتاج)
pm2 start ecosystem.config.js
```

---

## 📂 هيكل المشروع (Project Map)

```text
Nexum-Core/
├── main.py                 # 🔱 العقل المدبر (v7.3.0)
├── nexum/                  # 📦 الحزمة النواتية الحديثة
│   ├── intelligence/       #    Gemini Classifier & AI logic
│   ├── security/           #    Audit Log & Rate Limiter
│   ├── memory/             #    Context Summarizer
│   └── kernel/             #    Bootstrap & Resilience
├── core/                   # 🧠 المخطط والمنسق (Legacy & Power)
│   ├── orchestrator.py     #    منفذ المهام DAG
│   ├── router.py           #    موجه الـ Callbacks
│   └── executor.py         #    منفذ أوامر Shell
├── agents/                 # 🤖 أسطول الوكلاء
│   ├── webforge_agent.py   #    بناء الويب
│   ├── agent_smith.py      #    بناء الوكلاء
│   └── monitor.py          #    مراقبة النبض
└── registry/               # 📂 مخزن المخرجات (Apps, Bots, Agents)
```

---

## 🛣️ خارطة الطريق (Roadmap)
*   **v7.x**: تعميق التكامل بين الوكلاء (Multi-Agent Swarms).
*   **v8.x**: واجهة ويب Mini App تفاعلية بالكامل داخل Telegram.
*   **v9.x**: الانتقال إلى بنية لامركزية بالكامل (Decentralized Core).

---

## 👨‍💻 المايسترو
تم تطوير وبرمجة هذا النظام بواسطة **معتز إسماعيل تيلخ (Mutaz Tailakh)**.

---
🔱 **NEXUM — The Future is Sovereign.**
