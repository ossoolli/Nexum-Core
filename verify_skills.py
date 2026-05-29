# -*- coding: utf-8 -*-
"""
Verification script for Nexum Core Skills System (Task 1)
"""

import sys
from pathlib import Path

# Add project root to path to ensure clean imports
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from nexum.skills import SovereignSkillsManager

def run_verification():
    print("=== Starting SovereignSkillsManager Verification ===")
    
    # 1. Initialize SovereignSkillsManager
    manager = SovereignSkillsManager()
    print(f"Skills directory: {manager.skills_dir}")
    print(f"Skills directory exists: {manager.skills_dir.exists()}")
    
    # 2. List Skills
    print("\n--- Listing Skills ---")
    skills = manager.list_skills()
    print(f"Found {len(skills)} skills:")
    for skill in skills:
        print(f" - File: {skill['file_name']}")
        print(f"   Name: {skill['name']}")
        print(f"   Description: {skill['description']}")
        print(f"   Version: {skill['version']}")
        print(f"   Valid: {skill['valid']}")
        if not skill['valid']:
            print(f"   Errors: {skill['errors']}")
            
    if len(skills) == 0:
        print("FAIL: No skills found in directory!")
        sys.exit(1)
        
    # 3. Load Sample Skill
    print("\n--- Loading 'example-skill' ---")
    try:
        loaded = manager.load_skill("example-skill")
        print("Success! Loaded skill.")
        print(f"Loaded Path: {loaded['path']}")
        print("Metadata:")
        for k, v in loaded['metadata'].items():
            print(f"  {k}: {v}")
        print("\nBody (First 150 chars):")
        print(loaded['body'].strip()[:150] + "...")
    except Exception as e:
        print(f"FAIL: Failed to load skill: {e}")
        sys.exit(1)
        
    # 4. Validate Specific Invalid/Malformed YAML Frontmatter content
    print("\n--- Validating Edge Cases ---")
    
    invalid_content_no_name = """---
description: This is a description without a name.
version: 1.0.0
---
# Some Body
"""
    frontmatter, _ = SovereignSkillsManager.parse_skill_content(invalid_content_no_name)
    is_valid, errors = manager.validate_frontmatter(frontmatter)
    print(f"No Name Frontmatter: valid={is_valid}, errors={errors}")
    assert not is_valid, "Should be invalid"
    assert "Missing required field: 'name'" in errors
    
    invalid_name_too_long = f"""---
name: {"a" * 100}
description: Valid description
version: 1.0.0
---
"""
    frontmatter, _ = SovereignSkillsManager.parse_skill_content(invalid_name_too_long)
    is_valid, errors = manager.validate_frontmatter(frontmatter)
    print(f"Too Long Name Frontmatter: valid={is_valid}, errors={errors}")
    assert not is_valid, "Should be invalid"
    assert any("too long" in err for err in errors)

    print("\n=== All Verifications Passed Successfully! ===")

if __name__ == "__main__":
    run_verification()
