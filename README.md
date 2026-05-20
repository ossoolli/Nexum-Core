# 🔱 NEXUM CORE OS v7.2 | Sovereign Agentic Operating System

> **نظام تشغيل سيادي ذكي متكامل.** NEXUM v7.2 هو القفزة الكبرى نحو الاستقلالية التامة، مع "وعي" نظام تشغيل مركزي وقدرات تخزين سحابية هجينة لضمان كفاءة السيرفر المطلقة.

[![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue?style=for-the-badge&logo=telegram)](https://core.telegram.org/bots/api)
[![Version](https://img.shields.io/badge/Version-7.2--ULTRA-gold?style=for-the-badge)](#)
[![AI](https://img.shields.io/badge/AI-Gemini%20Flash/Pro%20+%20Claude-purple?style=for-the-badge&logo=google)](#)

---

## 🚀 ما الجديد في الإصدار 7.2؟ (إصدار الكفاءة والوعي)

تم تقديم ميزات ثورية لضمان بقاء السيرفر خفيفاً ومنظماً مهما كثرت المشاريع:
- **Hybrid Cloud Storage Manager:** نظام تخزين هجين يربط السيرفر بـ **Supabase** وقنوات **Telegram** للتخزين الخارجي.
- **Auto-Archiving (Zip & Offload):** قدرة النظام على أرشفة المشاريع المكتملة في ملفات ZIP ورفعها للسحاب وحذفها محلياً لتوفير مساحة السيرفر.
- **OS Consciousness Layer:** تحديث "وعي" النظام ليدرك دوره كقائد مركزي (Central Orchestrator) مع تحسين فهم النوايا (Intent Recognition) حتى مع الاختلافات اللغوية.
- **Strict Organizational Hierarchy:** فرض هيكلية تنظيمية صارمة للمجلدات لضمان عدم تراكم الملفات العشوائية في جذر النظام.

---

## 🧠 المحركات المركزية (v7.2 Core)
| المحرك | الوصف | المجلد المخصص |
|---|---|---|
| ☁️ **CloudManager** | مدير التخزين السحابي؛ يرفع النسخ الاحتياطية لتيليجرام وسوباباس. | `core/cloud_storage.py` |
| 🌐 **WebForge** | محرك بناء المواقع والتطبيقات السحابية. | `registry/apps/` |
| 🤖 **AgentSmith** | مصنع الوكلاء الذكي وتصميم الشخصيات الرقمية. | `registry/agents/` |
| 🏗️ **BotBuilder** | توليد وتشغيل أسطول بوتات تيليجرام المستقلة. | `registry/bots/` |
| 📦 **Storage Engine** | إدارة الملفات والوثائق والأرشفة التلقائية. | `storage/` |

---

## 🏗️ المعمارية السحابية المحدثة (Architecture)

```
┌─────────────────────────────────────────────────────────┐
│              🌐 Web Dashboard (v7.2 UI)                 │
│    (Status | Cloud Backups | Apps | Bots | Storage)     │
└──────────────┬──────────────────────┬───────────────────┘
               ↓                      ↓
┌──────────────────────┐      ┌───────────────────────────┐
│ 🔱 NEXUM CORE MAIN  │ ←──→ │   Supabase Cloud Sync     │
│ (Telegram Interface) │      │   (Database & Storage)    │
└──────────────┬───────┘      └───────────────────────────┘
               ↓                       |
┌─────────────────────────────────────────────────────────┐
│            🧠 OS ORCHESTRATOR & PLANNER                 │
│         (Cloud-Aware Task Execution Layer)              │
└──────────────┬──────────────────────────────────────────┘
               ↓
┌───────┬───────────────┬───────────────┬────────────────┐
│  ☁️    │      🌐       │      🤖       │       🏗️       │
│Backup │ WebForge      │ AgentSmith   │  BotBuilder    │
└───────┴───────────────┴───────────────┴────────────────┘
```

---

## 💻 التفاعل والوعي (Intelligence Layer)

النظام الآن يمتلك "وعياً" بالمكان والزمان والمساحة التخزينية:

*   **📦 الأرشفة:** "اضغط مشروع WebApp وارفعه للقناة" → (Build > Zip > Upload > Local Delete).
*   **☁️ السحاب:** "احفظ هذه النسخة في سوباباس" → CloudBackup Tool.
*   **📂 التنظيم:** أي رسائل أو وثائق يتم تخزينها تلقائياً في `storage/docs/` لضمان نظافة النظام.
*   **🛡️ الأمان:** يتم فحص جميع الأوامر والمسارات لمنع الخروج عن نطاق مجلد العمل (`BASE_DIR`).

---

## 🚀 التثبيت والتشغيل السريع

### 1- المتطلبات السحابية
للحصول على كامل قدرات الإصدار 7.2، أضف هذه القيم لملف الـ `.env`:
- `SUPABASE_URL` & `SUPABASE_KEY` (للتخزين السحابي)
- `TELEGRAM_CHANNEL_ID` (لقناة التخزين الاحتياطي)

### 2- التثبيت
```bash
git clone https://github.com/ossoolli/Nexum-Core.git
cd Nexum-Core
pip install -r requirements.txt
```

### 3- التشغيل
```bash
pm2 start ecosystem.config.js
```

---

## 👨‍💻 المطوّر
تم تطوير **NEXUM CORE OS** بواسطة **معتز إسماعيل تيلخ (Mutaz Tailakh)**.

*🔱 NEXUM CORE OS v7.2 — Sovereign Agentic Operating System*
