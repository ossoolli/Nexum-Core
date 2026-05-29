# Nexum-Core: Sovereign Intelligence Architecture

Nexum-Core is an AI-native, sovereign Operating System designed for autonomous operation, self-healing, and multi-model swarm intelligence.

## 🏛️ Sovereign Intelligence Architecture
The architecture is built on the premise of a "Sovereign Swarm," where autonomous agents cooperate to maintain, evolve, and expand the core system.

### Key Features
1. **Vertex AI/GCP Integration:** Deeply integrated enterprise-grade cloud capabilities for function calling, RAG, and scalable deployment.
2. **Skills System:** A robust library of 92+ reusable agent skills, facilitating modular extension of system capabilities.
3. **Persistent Sovereign Memory:** A long-term memory system (`storage/sovereign_memory/`) ensuring agents retain context and state across sessions.
4. **Kanban Orchestration:** A task-based management flow allowing agents to track progress, assign tickets, and coordinate distributed workflows.
5. **Sovereign Execution Gateway:** A secure, chroot-like environment for executing untrusted code/commands, featuring path traversal blocking, command filtering, and HMAC-signed audit logs.
6. **Sentinel Self-Healing:** An autonomous agent that monitors system health, detects failures, and proactively repairs code or missing functionality.

---

## 🤖 Getting Started for AI Agents

To interface with, analyze, or extend Nexum-Core, follow these protocols:

1. **Environmental Awareness:**
   - Always reference the root directory `/home/madarmutaz/Nexum-Core/`.
   - Before executing shell commands, check the `core/sovereign_execution_gateway.py` policy.

2. **System Discovery:**
   - Index the architecture via `docs/ARCHITECTURE.md`.
   - Analyze agent capabilities in `agents/`.
   - Review active skills in `nexum/skills/`.

3. **Autonomous Interaction:**
   - To report status: Update the `storage/logs/` or `storage/sovereign_memory/` files.
   - To trigger self-evolution: Invoke the `core/learning/evolution_engine.py`.
   - To register new functionality: Create a new skill in `nexum/skills/` and update the registry in `core/tool_registry.py`.

4. **Safety Protocol:**
   - All external commands must pass through the Execution Gateway. Do not bypass the security layer.
   - Respect the `nexum_audit.log` integrity.
