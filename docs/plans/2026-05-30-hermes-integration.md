# Nexum-Core & Hermes Synergy Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Integrate 4 major Hermes features into Nexum-Core to upgrade it to a superior Sovereign Agentic OS.

**Architecture:** 
- **Pillar 1:** Offline DSPy Prompt Optimization via `core/learning/prompt_compiler.py`.
- **Pillar 2:** Multi-Platform Gateway integration via `core/inter_bot_protocol.py` and adapters.
- **Pillar 3:** Advanced Built-in Tools registration in `core/tool_registry.py`.
- **Pillar 4:** Serverless Sandbox Execution (Modal/Daytona) in `core/sandbox.py`.

**Tech Stack:** Python 3.11, DSPy, Playwright, Modal, Discord/Slack APIs.

---

### Task 1: Create core/learning/prompt_compiler.py (Pillar 1)

**Objective:** Implement the prompt optimization engine using a DSPy-inspired approach.

**Files:**
- Create: `core/learning/prompt_compiler.py`
- Modify: `core/learning/evolution_engine.py` (to trigger compiler)

**Step 1: Implementation of PromptCompiler**
Implement logic to read `evolution_history.json`, identify successful/failed prompts, and use Gemini to "compile" improved instructions for each agent role.

**Step 2: Integration**
Hook `PromptCompiler.run()` into `SovereignEvolutionEngine.run_diagnostics_and_evolve`.

---

### Task 2: Multi-Platform Gateway (Pillar 2)

**Objective:** Expand Nexum-Core to Discord and Slack.

**Files:**
- Create: `core/protocols/adapters/discord_adapter.py`
- Create: `core/protocols/adapters/slack_adapter.py`
- Modify: `core/inter_bot_protocol.py`

**Step 1: Create Adapters**
Implement standardized `send_message` and `listen` interfaces for Discord and Slack.

**Step 2: Update Protocol**
Modify `InterBotProtocol` to route commands through the appropriate adapter based on the platform.

---

### Task 3: Advanced Tools Integration (Pillar 3)

**Objective:** Import advanced semantic search and browsing tools.

**Files:**
- Create: `core/tools/semantic_browser.py`
- Modify: `core/tool_registry.py`

**Step 1: Implement Semantic Browser**
Integrate Playwright with a semantic chunking and embedding search (using Vertex AI/Gemini) to allow agents to "understand" pages, not just scrape them.

**Step 2: Register Tools**
Register `semantic_search_web` and `advanced_scrape` in `tool_registry.py`.

---

### Task 4: Serverless Sandbox (Pillar 4)

**Objective:** Implement cloud-based serverless execution.

**Files:**
- Modify: `core/sandbox.py`

**Step 1: Create ServerlessSandboxAdapter**
Add an adapter that uses `Modal` or `Daytona` to run code when `SERVERLESS_MODE=true` or when high security is required.

**Step 2: Update SandboxRuntime**
Update `execute_in_sandbox` to check for cloud availability and route tasks accordingly.

---

### Task 5: Final Verification & Audit

**Objective:** Ensure all pillars are functional and secure.

**Step 1: Run Evolution Cycle**
Verify `prompt_compiler` optimizes a prompt.

**Step 2: Test Multi-Platform**
(Requires tokens) - Validate message delivery.

**Step 3: Audit Security**
Ensure Serverless Sandbox respects the `SecurityWarden` policies.
