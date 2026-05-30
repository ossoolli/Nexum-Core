---
name: nexum-core-documentation
description: Use when documenting Nexum-Core evolution, features, and system updates. Provides the structure for the project README and system evolution reports.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nexum-core, documentation, readme, evolution]
    related_skills: [hermes-agent-skill-authoring]
---

# Nexum-Core Documentation & Evolution Tracking

## Overview
Nexum-Core documentation must be comprehensive, structured, and reflect the system's status as a Sovereign Agentic Operating System. This skill governs the generation of the `README.md` and related evolution logs.

## When to Use
- User requests status updates on the system.
- Significant system changes (e.g., new agents, new integration managers).
- Updating project `README.md` for GitHub.

## Documentation Structure
1. **Title & Vision**: Core identity and technical goals.
2. **Architecture Highlights**: Key components (Self-Healing, Sovereign Operations).
3. **Evolution History**: Key updates distilled from `/storage/sovereign_memory/evolution_history.json`.
4. **Agent Registry**: Active agents and their roles (from `storage/agent_registry.json`).
5. **Operational Status**: Current system health.
6. **Arabic Localization**: All documentation, headers, and bullet points must be in professional Arabic. This includes system README files and version release notes.

## Pitfalls
- **Don't just summarize**: Ensure technical depth and explain the "why".
- **Keep it current**: Verify against `/storage/sovereign_memory/evolution_history.json` before writing.
- **Localization Requirement**: The user requires all UI, system documentation, and release communications to be natively localized to Arabic.

## Verification Checklist
- [ ] README is updated in the repo.
- [ ] Evolution history was cross-referenced.
- [ ] Arabic terminology is accurate and technical.
