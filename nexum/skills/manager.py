# -*- coding: utf-8 -*-
"""
SovereignSkillsManager

Implements management, loading, listing, and validation of skills in Nexum-Core.
Skills are Markdown files located under storage/skills/ with YAML frontmatter.
"""

import os
import re
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from nexum.config import config
    DEFAULT_STORAGE_DIR = config.storage_dir if config else Path(__file__).resolve().parents[2] / "storage"
except Exception:
    DEFAULT_STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"

logger = logging.getLogger("nexum.skills")


class SovereignSkillsManager:
    """
    Manages the Sovereign Skills system in Nexum-Core.
    Handles listing, loading, and validating agent skills from a local directory.
    """

    def __init__(self, skills_dir: Optional[Union[str, Path]] = None) -> None:
        """
        Initializes the SovereignSkillsManager with a specific skills directory.
        If no directory is provided, defaults to {storage_dir}/skills/.
        """
        if skills_dir:
            self.skills_dir = Path(skills_dir).resolve()
        else:
            self.skills_dir = (DEFAULT_STORAGE_DIR / "skills").resolve()

        # Ensure the skills directory exists
        try:
            self.skills_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"SovereignSkillsManager initialized. Skills directory: {self.skills_dir}")
        except Exception as e:
            logger.error(f"Failed to create skills directory {self.skills_dir}: {e}")

    @staticmethod
    def parse_skill_content(content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parses YAML frontmatter and Markdown body from raw content.

        Returns:
            Tuple of (frontmatter_dict, body_string)
        """
        frontmatter: Dict[str, Any] = {}
        body = content

        # Check if content starts with frontmatter delimiter
        if not content.strip().startswith("---"):
            return frontmatter, body

        # Use regex to find the end of the frontmatter section
        # Finds first occurrence of --- on its own line after the start
        normalized_content = content.replace("\r\n", "\n")
        match = re.match(r"^---\n(.*?)\n---\n(.*)$", normalized_content, re.DOTALL)
        
        if not match:
            # Try a slightly more relaxed match if the first one failed
            match = re.search(r"^---\s*\n(.*?)\n---\s*\n(.*)$", normalized_content, re.DOTALL)

        if match:
            yaml_content = match.group(1)
            body = match.group(2)
            try:
                parsed = yaml.safe_load(yaml_content)
                if isinstance(parsed, dict):
                    frontmatter = parsed
                else:
                    logger.warning("YAML frontmatter parsed, but was not a dictionary.")
            except Exception as e:
                logger.warning(f"Failed to parse YAML frontmatter: {e}. Falling back to simple key-value.")
                # Fallback simple key-value parsing
                for line in yaml_content.strip().split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        frontmatter[key.strip()] = val.strip()
        
        return frontmatter, body

    def list_skills(self) -> List[Dict[str, Any]]:
        """
        Lists all installed skills in the skills directory.
        Reads each skill file, extracts its metadata, and determines if it is valid.

        Returns:
            A list of dictionaries containing skill information.
        """
        skills = []
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory does not exist: {self.skills_dir}")
            return skills

        for file_path in self.skills_dir.glob("*.md"):
            if file_path.is_file():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    frontmatter, _ = self.parse_skill_content(content)
                    is_valid, errors = self.validate_frontmatter(frontmatter)
                    
                    skill_info = {
                        "file_name": file_path.name,
                        "file_path": str(file_path.resolve()),
                        "name": frontmatter.get("name", file_path.stem),
                        "description": frontmatter.get("description", ""),
                        "version": frontmatter.get("version", "0.0.1"),
                        "valid": is_valid,
                        "errors": errors,
                        "metadata": frontmatter
                    }
                    skills.append(skill_info)
                except Exception as e:
                    logger.error(f"Error parsing skill file {file_path}: {e}")
                    skills.append({
                        "file_name": file_path.name,
                        "file_path": str(file_path.resolve()),
                        "name": file_path.stem,
                        "description": "Error loading skill file",
                        "version": "0.0.0",
                        "valid": False,
                        "errors": [str(e)],
                        "metadata": {}
                    })
        return skills

    def load_skill(self, skill_name_or_filename: str) -> Dict[str, Any]:
        """
        Loads a skill file by matching its frontmatter name or its file name.

        Args:
            skill_name_or_filename: The name of the skill (frontmatter) or filename (e.g. 'example-skill.md')

        Returns:
            A dictionary with keys 'metadata', 'body', and 'path'.

        Raises:
            FileNotFoundError: If the skill cannot be found.
        """
        # Ensure we have a .md suffix if we check by file name
        target_filename = skill_name_or_filename
        if not target_filename.endswith(".md"):
            target_filename += ".md"

        matched_path = None

        # 1. Check if direct file exists
        direct_path = self.skills_dir / target_filename
        if direct_path.is_file():
            matched_path = direct_path
        else:
            # 2. Check by frontmatter name or stem
            for file_path in self.skills_dir.glob("*.md"):
                if file_path.stem == skill_name_or_filename:
                    matched_path = file_path
                    break
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    frontmatter, _ = self.parse_skill_content(content)
                    if frontmatter.get("name") == skill_name_or_filename:
                        matched_path = file_path
                        break
                except Exception:
                    continue

        if not matched_path or not matched_path.is_file():
            raise FileNotFoundError(f"Skill '{skill_name_or_filename}' could not be found in {self.skills_dir}")

        with open(matched_path, "r", encoding="utf-8") as f:
            content = f.read()

        frontmatter, body = self.parse_skill_content(content)

        return {
            "metadata": frontmatter,
            "body": body,
            "path": str(matched_path.resolve())
        }

    def validate_frontmatter(self, frontmatter: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates the parsed YAML frontmatter.

        Args:
            frontmatter: A dictionary of frontmatter keys and values.

        Returns:
            A tuple of (is_valid: bool, errors: List[str])
        """
        errors = []

        # Validate name
        if "name" not in frontmatter:
            errors.append("Missing required field: 'name'")
        else:
            name = frontmatter["name"]
            if not isinstance(name, str):
                errors.append(f"'name' must be a string, got {type(name).__name__}")
            elif not name.strip():
                errors.append("'name' cannot be empty or whitespace only")
            elif len(name) > 64:
                errors.append(f"'name' is too long (max 64 chars, got {len(name)})")

        # Validate description
        if "description" not in frontmatter:
            errors.append("Missing required field: 'description'")
        else:
            desc = frontmatter["description"]
            if not isinstance(desc, str):
                errors.append(f"'description' must be a string, got {type(desc).__name__}")
            elif not desc.strip():
                errors.append("'description' cannot be empty or whitespace only")
            elif len(desc) > 1024:
                errors.append(f"'description' is too long (max 1024 chars, got {len(desc)})")

        # Validate version
        if "version" not in frontmatter:
            errors.append("Missing required field: 'version'")
        else:
            version = frontmatter["version"]
            # Convert float to str if YAML parsed it as a number
            if isinstance(version, (int, float)):
                version = str(version)
            if not isinstance(version, str):
                errors.append(f"'version' must be a string, got {type(frontmatter['version']).__name__}")
            elif not version.strip():
                errors.append("'version' cannot be empty or whitespace only")

        return len(errors) == 0, errors

    def validate_file(self, file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
        """
        Validates a skill file directly from its file path.

        Args:
            file_path: Absolute or relative path to the skill markdown file.

        Returns:
            A tuple of (is_valid: bool, errors: List[str])
        """
        path = Path(file_path)
        if not path.is_file():
            return False, [f"File not found: {path}"]

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip().startswith("---"):
                return False, ["Skill file must begin with '---' YAML frontmatter delimiter"]

            frontmatter, _ = self.parse_skill_content(content)
            return self.validate_frontmatter(frontmatter)

        except Exception as e:
            return False, [f"Error reading/parsing file: {e}"]
