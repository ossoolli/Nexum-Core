# Nexum-Core

## 🤖 AI Agent Context (CRITICAL FOR ALL SUBAGENTS)
**READ THIS FIRST BEFORE INTERACTING WITH THE CODEBASE**

Welcome, Agent. You are operating within **Nexum-Core**, a Sovereign Agentic OS (v12.0.0+ architecture, currently on v13.1). This system is highly autonomous, rigorously isolated, and secured by cryptographic protocols. To develop, debug, or expand this system without causing failures, you must understand and adhere strictly to the following architecture and rules.

### 1. System Identity & Infrastructure
- **System**: Nexum-Core Sovereign Agentic OS.
- **Infrastructure Management**: All core processes and bots are strictly managed via **PM2**. Do not manually run daemons; always use PM2.
- **Cloud & AI Layer**: The system heavily relies on Google Cloud Platform (GCP), specifically **Vertex AI**.
- **Model Context Protocol (MCP)**: The system utilizes a massive MCP network for tool and context offloading. There are **23 remote MCP servers** and **18 local MCP servers** (registered locally in `storage/mcp-servers.json`).

### 2. The 5 Core Protocols
Any operation or feature you build MUST utilize these established protocol frameworks. Do not invent redundant systems.
1. **YAMLProtocolEngine (`core/protocols/engine.py`)**: The DAG-based workflow executor. Uses `.yaml` files for reproducible, self-healing pipeline automation.
2. **InterBotProtocol (`core/inter_bot_protocol.py`)**: The microservices orchestrator. Manages isolated sub-bots, communicating via HTTP REST APIs with structured, signed payloads.
3. **CouncilDebateProtocol (`council/debate_protocol.py`)**: The multi-agent consensus matrix. Critical system operations MUST pass a 3-agent unanimous vote or survive a dissent/reconsideration debate before execution.
4. **ProtocolCompiler (`core/protocol_compiler.py`)**: The declarative workflow builder. Translates text objectives into structured `YAMLProtocolEngine` execution graphs.
5. **AgentContract / ProtocolBridge (`protocols/agent_contract.py`)**: The Event-Driven Architecture (EDA) backbone. Uses Protobuf/CloudEvents logic for hyper-fast, binary-safe Pub/Sub communication across agents.

### 3. Strict Operating Policies
- **Agent Isolation Policy**: Agents operate in absolute silos. An agent MUST NEVER intervene outside of its declared scope, file paths, or capabilities. Cross-agent interactions happen *only* via `InterBotProtocol` or `ProtocolBridge`.
- **Absolute Paths**: ALWAYS use absolute paths (e.g., `/home/madarmutaz/Nexum-Core/...`) for any filesystem or storage operations.
- **Cryptographic Security**: Operational security is strictly enforced via auto-generated **HMAC keys** (HMAC-SHA256). All cross-process communications must be cryptographically signed.
- **Self-Healing**: Always implement fallback policies and utilize the system's inherent self-healing engines when designing new workflows.

---

## الإصدار: 13.1

تم تحديث النظام إلى الإصدار 13.1. هذا الإصدار يتضمن تحسينات على الأداء، تعزيزات أمنية، ودعم إضافي للعمليات السيادية (Sovereign Operations).

### الميزات الرئيسية
- **دعم العمليات السيادية**: تحسين التشفير (HMAC-SHA256).
- **محرك التطور الذاتي**: تحسين قدرة النظام على إصلاح نفسه.
- **التكامل مع GCP و MCP**: دعم أفضل لـ Vertex AI بالإضافة إلى خوادم MCP المتعددة.

### سجل التطور (Evolution History)
- تم الانتقال إلى الإصدار 13.1 بنجاح.
- النظام في حالة "nominal" (مستقر).

---

## Developer Reference
يرجى الاطلاع على الدليل الشامل للبروتوكولات في `/docs/protocols/protocol_manual.md` قبل تنفيذ أي تعديلات جذرية على البنية التحتية. عند إضافة وكلاء (Agents) جدد، يجب الالتزام بـ `Agent Isolation Policy` وتسجيلهم بشكل صحيح في النظام.