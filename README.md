# 🔱 Nexum-Core — Sovereign Agentic OS (v13.3.0 Release)

```
███╗   ██╗███████╗██╗  ██╗██╗   ██╗███╗   ███╗     ██████╗  ██████╗ ███████╗
████╗  ██║██╔════╝╚██╗██╔╝██║   ██║████╗ ████║    ██╔═══██╗██╔════╝ ██╔════╝
██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║██╔████╔██║    ██║   ██║██║      ███████╗
██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║██║╚██╔╝██║    ██║   ██║██║      ╚════██║
██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝██║ ╚═╝ ██║    ╚██████╔╝╚██████╗███████║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝     ╚═════╝  ╚═════╝╚══════╝
```

## 🤖 AI Agent Context (CRITICAL FOR ALL COGNITIVE SUBAGENTS)
**READ THIS FIRST BEFORE INTERACTING WITH THE CODEBASE OR EXECUTING WORKFLOWS**

Welcome, Agent. You are operating within **Nexum-Core**, an advanced, highly autonomous Sovereign Agentic OS (v13.3.0 architecture). The system is designed for secure, self-healing, multi-agent operations across diverse platforms (fully compatible with Windows and Linux). Before developing, debugging, or introducing changes, you must understand and adhere strictly to the system's core design system and security policies.

---

## 🏛️ System Identity & Key Infrastructure

1. **Self-Healing Code Repair**: Equipped with `SovereignEvolutionEngine` (`core/learning/evolution_engine.py`) to automatically detect script failures and repair them autonomously using LLM cognitive loops.
2. **PM2 & Process Isolation**: All operational daemons, bots, and monitoring agents are managed via **PM2** clusters.
3. **Model Context Protocol (MCP)**: Leverages a high-capacity MCP network. Registered catalog includes **23 remote MCP servers** and **18 local MCP servers** (configured in `storage/mcp-servers.json`).
4. **Vertex AI & LLM Engine**: Connected dynamically to Google Cloud Vertex AI and Gemini cognitive models for enterprise-grade operations.

---

## 🧬 The 5 Core System Protocols

All features and automation pipelines MUST inherit and utilize these established engines:
1. **YAMLProtocolEngine (`core/protocols/engine.py`)**: The DAG-based workflow executor using declarative `.yaml` pipelines.
2. **InterBotProtocol (`core/inter_bot_protocol.py`)**: Microservices orchestrator. Manages communication between sub-bots using signed REST APIs.
3. **CouncilDebateProtocol (`council/debate_protocol.py`)**: Multi-agent consensus system. Critical modifications require a unanimous vote of 3 cognitive agents or consensus debate resolution.
4. **ProtocolCompiler (`core/protocol_compiler.py`)**: Translates high-level natural language instructions into runnable DAG execution schemas.
5. **AgentContract / ProtocolBridge (`protocols/agent_contract.py`)**: High-throughput Event-Driven Architecture (EDA) using Protobuf and Pub/Sub over Redis/HTTP bridges.

---

## 🛡️ Strict Operating Policies & Best Practices

- **Agent Isolation Policy**: Agents operate inside strict sandboxes. No agent can execute code or make changes outside its whitelisted scope.
- **Dynamic Platform-Independent Pathing**: **Do NOT hardcode paths** (e.g. `/home/madarmutaz/`). The codebase resolved all project roots, databases (`~/.hermes/state.db`), and storage dynamically via `BASE_DIR = os.path.dirname(...)` to support Windows and Linux environments interchangeably.
- **SQLCipher Safe Parameterization**: Database encryption keys (`NEXUM_DB_ENCRYPTION_KEY`) in SQLCipher commands must be securely escaped (`db_key.replace("'", "''")`) to eliminate SQL injection vectors.
- **Robust Kanban Integration**: The sentinel maintenance agent is integrated natively via the `BoardManager` (`nexum/kanban/board_manager.py`) which dynamically searches, updates, and comments on tasks across all active visual boards using their ID or title.

---

## 🔱 الإصدار الحالي: v13.3 (الترقية السيادية وتأمين النظام)

تمت ترقية **Nexum-Core** إلى الإصدار **13.3**، متضمناً معالجة شاملة لأمن وجودة الكود، وإصلاح توافقية المسارات بين ويندوز ولينكس.

### 🌟 الميزات والتحديثات الجديدة:
* **مسارات ديناميكية بالكامل**: توافق 100% مع أنظمة Windows و Linux دون أي حاجة لتعديل المسارات الصلبة يدوياً.
* **تأمين قواعد البيانات (SQLCipher Hardening)**: إغلاق كافة ثغرات حقن الاستعلامات في `PRAGMA key` ومعالجة مفاتيح التشفير بأمان تام.
* **نظام الكانبان المدمج (Kanban Orchestration Hub)**: تفعيل موديول `board_manager` لإتاحة التحديث التلقائي للحارس الرقابي (**Sentinel**) وتتبع المهام بصرياً وعرض تقارير الفحص الفوري.
* **استقرار بنسبة 100%**: نجاح جميع اختبارات الوحدة والدمج (`186 Passed Tests`) بنسبة نجاح كاملة ودون أي خطأ.

### 📁 هيكل ودليل المطورين (Developer Reference)
قبل البدء في تعديل أو إضافة أي مهارة أو بروتوكول، يرجى قراءة الدليل الكامل في:
- [دليل البروتوكولات الشامل](file:///c:/Users/madar/Documents/nexum/docs/protocols/protocol_manual.md)
- [منظومة الحارس والمهام بصرياً](file:///c:/Users/madar/Documents/nexum/nexum/kanban/board_manager.py)
- [ملف مواصفات وقيود الحماية](file:///c:/Users/madar/Documents/nexum/agent_guardrails.json)

النظام الآن في حالة تشغيل كاملة ومثالية (Active & Live) ومتصل بخوادم البث المباشر.