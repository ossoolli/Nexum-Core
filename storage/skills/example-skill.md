---
name: example-skill
description: A sample skill for Nexum-Core demonstrating SovereignSkillsManager functionality.
version: 1.0.0
author: MadarMutaz
tags: [sample, sovereign, skills]
---

# Example Skill

Welcome to the example skill of **Nexum-Core**!

This skill serves as a template and a functional test for the `SovereignSkillsManager`.

## Purpose
The Sovereign Skills system empowers Nexum-Core agents with modular, localized capabilities. Skills are defined as Markdown files containing YAML frontmatter that specifies:
- Unique, identifiable name
- High-level descriptions for progressive disclosure in agent prompts
- Version control parameters
- Structural configurations or requirements

## How to use
You can load this skill via the `SovereignSkillsManager`:
```python
from nexum.skills import SovereignSkillsManager

manager = SovereignSkillsManager()
skills = manager.list_skills()
print(skills)

# Load the specific skill
skill = manager.load_skill("example-skill")
print(skill["metadata"])
print(skill["body"])
```
