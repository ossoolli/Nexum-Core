# 🔱 NEXUM CORE OS v7.0 | Sovereign Agentic Operating System

> **نظام تشغيل سيادي ذكي متكامل.** NEXUM v7.0 هو تحول جذري من بوت ذكي إلى نظام تشغيل وكلاء مستقل (Sovereign Agentic OS) يقوم بالبناء، الإدارة، والتواصل الذاتي.

[![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue?style=for-the-badge&logo=telegram)](https://core.telegram.org/bots/api)
[![Version](https://img.shields.io/badge/Version-7.0--ULTRA-gold?style=for-the-badge)](#)
[![AI](https://img.shields.io/badge/AI-Gemini%20Flash/Pro%20+%20Claude-purple?style=for-the-badge&logo=google)](#)

---

## 🚀 ما الجديد في الإصدار 7.0؟

تم إعادة بناء النظام ليدعم بنية **الوكلاء المتعددي المهام (Multi-Agent System)** مع القدرة على توليد وتشغيل تطبيقات وبوتات ووكلاء جدد في ثوانٍ.

### 🧠 المحركات الجديدة (v7.0 Core)
| المحرك | الوصف |
|---|---|
| 🌐 **WebForge** | محرك بناء مواقع ويب (Landing Pages, Dashboards, APIs) بملف واحد وأسلوب عصري. |
| 🤖 **AgentSmith** | مصنع الوكلاء؛ يصمم ويبني ويشغل وكلاء مخصصين من وصف نصي فقط. |
| 🏗️ **BotBuilder** | يولّد بوتات Telegram كاملة بشخصيات وقدرات محددة ويشغلها كعمليات PM2. |
| 📡 **BotNetwork** | ناقل تواصل بين البوتات والوكلاء عبر Redis Pub/Sub مع fallback محلي. |
| 📢 **ChannelManager** | مدير بث متقدم للنشر والجدولة المتزامنة عبر قنوات متعددة. |
| 🟢 **BotFleet** | أسطول بوتات يعمل بشكل مستقل ومدار بالكامل عبر لوحة التحكم. |

---

## 🏗️ المعمارية المحدثة (Architecture)

```
┌─────────────────────────────────────────────────────────┐
│              🌐 Web Dashboard (v5.0 UI)                 │
│    (Status | WebForge | Agents | Bots | Channels)       │
└──────────────┬──────────────────────┬───────────────────┘
               ↓                      ↓
┌──────────────────────┐      ┌───────────────────────────┐
│ 🔱 NEXUM CORE MAIN  │ ←──→ │   FastAPI Gateway (v5.0)  │
│ (Telegram Interface) │      │   (18+ API Endpoints)     │
└──────────────┬───────┘      └───────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────┐
│            🧠 OS ORCHESTRATOR & PLANNER                 │
│         (Dynamic DAG + Tool Execution Layer)            │
└──────────────┬──────────────────────────────────────────┘
               ↓
┌───────┬───────────────┬───────────────┬────────────────┐
│  🌐   │      🤖       │      🏗️       │       📢       │
│WebForge│ AgentSmith   │  BotBuilder   │ ChannelManager │
└───────┴───────────────┴───────────────┴────────────────┘
```

---

## 💻 التفاعل والأوامر (Interpreter v7.0)

النظام الآن يفهم سياقات معقدة ويوجهها للوكيل المناسب:

*   **🌐 بناء الويب:** "انشئ صفحة هبوط لشركة عقارية" → WebForge
*   **🤖 بناء الوكلاء:** "ابني وكيل يراقب أسعار العملات" → AgentSmith
*   **🏗️ بناء البوتات:** "انشئ بوت تواصل لعملاء أصولي" → BotBuilder
*   **📢 القنوات:** "انشر هذا العرض في كل قنواتي" → ChannelManager
*   **📊 المراقبة:** "وضعية أسطول البوتات" → BotFleet

---

## 🖥️ لوحة التحكم (FastAPI Dashboard)

تأتي النسخة السابعة بواجهة ويب احترافية (Premium Dark Mode) تحتوي على 5 تبويبات:
1.  **📊 النظام:** مراقبة الموارد (CPU, RAM, Disk) والعمليات.
2.  **🌐 المواقع:** عرض المواقع المبنية بـ WebForge مع روابط معاينة حية.
3.  **🤖 الوكلاء:** إدارة وتصدير الوكلاء المخصصين المولّدين بـ AgentSmith.
4.  **🤖 البوتات:** مراقبة أسطول البوتات المستقلة وإعادة تشغيلها.
5.  **📢 القنوات:** إدارة قنوات التلجرام والنشر المتزامن.

---

## 🚀 التثبيت والتشغيل السريع

### 1- المتطلبات
- Python 3.10+
- Redis (اختياري، يوصى به لـ BotNetwork)
- PM2 (لإدارة العمليات)

### 2- التثبيت
```bash
git clone https://github.com/ossoolli/Nexum-Core.git
cd Nexum-Core
pip install -r requirements.txt
```

### 3- التشغيل عبر PM2 (5 عمليات نشطة)
```bash
pm2 start ecosystem.config.js
```

---

## 📁 هيكل التخزين والنتائج
- `registry/apps/`: المواقع والتطبيقات التي بناها WebForge.
- `registry/bots/`: البوتات المستقلة التي بناها BotBuilder.
- `agents/generated/`: الوكلاء الذين صممهم AgentSmith.
- `storage/templates/`: قوالب البوتات والمواقع الاحترافية.

---

## 👨‍💻 المطوّر
تم تطوير **NEXUM CORE OS** بواسطة **معتز إسماعيل تيلخ (Mutaz Tailakh)**.

*🔱 NEXUM CORE OS v7.0 — Sovereign Agentic Operating System*
