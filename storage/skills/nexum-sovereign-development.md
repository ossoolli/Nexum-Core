---
name: nexum-sovereign-development
description: "Workflow for developing and maintaining the Nexum-Core autonomous agentic OS."
version: 1.0.0
---

# Nexum-Core Sovereign Development

This skill governs the development and maintenance of the Nexum-Core Agentic OS, emphasizing security, autonomy, and self-healing systems.

## Key Principles
- **Sovereignty**: Operations must be isolated in a workspace (`WORKSPACE_DIR`), audited (`nexum_audit.log`), and signed (`HMAC-SHA256`).
- **Self-Evolution**: Use `SovereignEvolutionEngine` to auto-repair crashed agents and synthesize new ones based on capability gaps.
- **Obstacle-Free Security**: Security measures (like HMAC keys) must be self-generating and persistent; never crash on missing config.

## Development Workflow
1. **Planning**: Use implementation plans (stored in `docs/plans/`) for all non-trivial changes.
2. **Implementation**: 
   - Use the `SovereignSkillsManager` to leverage reusable agentic workflows.
   - All code must adhere to the `nexum/cloud/` and `core/` architecture patterns.
   - **Native Library Linking**: When integrating separate repositories or modules (like `hermes-agent`) into Nexum-Core's virtual environment, write a `.pth` file in the environment's `site-packages` directory (e.g., `/home/madarmutaz/Nexum-Core/venv/lib/python3.11/site-packages/hermes.pth` containing the absolute path `/home/madarmutaz/hermes-agent`). This places the external codebase natively inside the import path, allowing python scripts and PM2 services to cleanly run `import hermes_cli` without env hacks.
3. **Review**: Rely on the Council of Sages consensus engine (Gemini/Claude/GPT/Grok) for critical architectural decisions.
4. **Maintenance**: 
   - Keep `storage/logs/err.log` clean.
   - Use `pm2` for process lifecycle management.
   - Monitor `nexum_audit.log` for security breaches.

## Verification
- Run `tests/test_sovereign_execution_gateway.py` after any change to core security or file operations.
- Verify `HMAC` integrity using `core.sovereign_execution_gateway.verify_audit_log`.

## Versioning and Release
- When releasing a new version, use standard git tagging: `git tag v<version> && git push origin v<version>`.
- Ensure all version-specific changes are documented in the project log.

## References
- `references/gcp-agent-platform-integration.md`: Setup and credential management for Vertex AI/Dialogflow CX.
- `references/security-manifest.md`: HMAC signing, path traversal filtering, and whitelist command definitions.
