# config_loader.py
"""Utility to load configuration for Nexum‑Core.
Falls back to the existing ``nexum.config`` module if a ``config.yaml``
file is not present. Supports environment‑variable overrides.
"""
import os
import yaml
from types import SimpleNamespace

def _load_yaml(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        # If yaml is not installed or file missing, return empty dict
        return {}

def get_config() -> SimpleNamespace:
    """Return a configuration object with required attributes.
    Expected keys (at minimum):
        - ``telegram_token``
        - ``admin_id``
        - ``project`` (optional, used by cloud agent)
    Environment variables override values from ``config.yaml``.
    """
    cfg = {}
    yaml_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if os.path.isfile(yaml_path):
        cfg.update(_load_yaml(yaml_path))

    # Environment variable overrides (upper‑case names)
    env_map = {
        "TELEGRAM_TOKEN": "telegram_token",
        "ADMIN_ID": "admin_id",
        "PROJECT": "project",
        "LOCATION": "location",
    }
    for env_key, cfg_key in env_map.items():
        if env_val := os.getenv(env_key):
            cfg[cfg_key] = env_val

    # Fallback to legacy config module if key missing
    try:
        from nexum.config import config as legacy_cfg
        for key in ["telegram_token", "admin_id", "project", "location"]:
            if key not in cfg and hasattr(legacy_cfg, key):
                cfg[key] = getattr(legacy_cfg, key)
    except Exception:
        pass

    # Validate required fields
    required = ["telegram_token", "admin_id"]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise RuntimeError(f"Missing required configuration keys: {', '.join(missing)}")

    return SimpleNamespace(**cfg)
