# NEXUM PRO — Technical Architecture (v7.2.5)

## 5-Tier Architecture

```
                  [ INTERFACE LAYER ]
                  Telegram Bot / CLI
                         |
                [ COGNITIVE CORE ]
                Gemini Agent Platform (ADC + API Key)
                ask() | generate_image() | execute_code()
                         |
              [ KERNEL & CONTEXT BUS ]
              SovereignMemory + ContextEngine + TrustEngine
                       /   \
         [ SWARM ENGINE ]   [ WATCHDOG SERVICE ]
         SwarmEngine         Watchdog + RecoveryManager
         CouncilOfSages      Heartbeat Monitor
              |                      |
     [ AGENT DIRECTORY ]    [ LEARNING LOOP ]
     AgentRegistry           ExperienceAnalyzer
     BaseAgent               PatternExtractor
     ExecutionEngine          InitiativeEngine
```

## Module Dependency Map

```
main.py
  |-- nexum/config.py (NexumConfig)
  |-- services/gemini_service.py (GeminiService)
  |-- core/memory_local.py (context_memory)
  |-- core/memory/sovereign_memory.py (SovereignMemory)
  |   |-- core/memory/components.py (InfrastructureMap, DecisionMemory, MissionLog)
  |-- core/context/context_engine.py (ContextEngine)
  |   |-- core/context/engines.py (PriorityEngine, DelegationEngine, RiskEngine)
  |-- core/trust/trust_engine.py (TrustEngine)
  |-- core/trust/behavior_engine.py (BehaviorEngine, DailyReport)
  |-- core/learning/engines.py (ExperienceAnalyzer, PatternExtractor)
  |-- core/learning/initiative_engine.py (PredictionEngine, InitiativeEngine)
  |-- core/terminal_controller.py (SovereignTerminalController)
  |-- core/executive_agent.py (ExecutiveAgent)
  |   |-- core/execution_engine.py (ExecutionEngine)
  |   |-- core/planner.py (AIPlanner)
  |-- watchdog/monitor.py (Watchdog)
  |-- watchdog/recovery.py (RecoveryManager)
  |-- swarm/engine.py (SwarmEngine)
  |-- swarm/council.py (CouncilOfSages)
```

## Data Flow: Command → Execution → Result

```
1. User sends message via Telegram
2. main.py receives message, checks ADMIN_ID
3. Intent Classifier categorizes the message
4. Context Engine evaluates the action:
   a. PriorityEngine scores alignment with goals
   b. DelegationEngine checks permissions (ALWAYS_ASK / AUTONOMOUS)
   c. RiskEngine calculates risk score
5. BehaviorEngine cross-references trust level:
   - OBSERVE: Log only
   - SUGGEST: Ask for approval
   - NOTIFY: Execute and notify
   - AUTONOMOUS: Execute silently
   - SOVEREIGN: Execute + learn + improve
6. If approved: TerminalController/ExecutionEngine executes
7. TrustEngine records outcome (success/fail/override)
8. ExperienceAnalyzer extracts lessons
9. PatternExtractor discovers recurring patterns
10. Result sent back to user via Telegram
```

## Security Architecture

| Layer | Protection | Module |
|-------|-----------|--------|
| Input | Forbidden commands blocklist | `terminal_controller.py` |
| Delegation | ALWAYS_ASK / ALWAYS_PROCEED lists | `context/engines.py` |
| Risk | Risk matrix scoring (0.0-1.0) | `context/engines.py` |
| Trust | 5-tier trust gating | `trust/trust_engine.py` |
| Council | Multi-agent weighted voting | `swarm/council.py` |
| Watchdog | Heartbeat + exponential backoff | `watchdog/monitor.py` |
| Recovery | Safe mode + context flush | `watchdog/recovery.py` |
| Secrets | `.gitignore` + env vars only | `nexum/config.py` |
| Files | Zip/Tar Slip + core jailbreak guard | `core/fs_control.py` |
| Paths | realpath grounding + boundary check | `core/planner.py` |
