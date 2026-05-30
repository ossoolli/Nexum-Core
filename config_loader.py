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

def _load_env_file(path: str) -> dict:
    env_dict = {}
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'").strip('"')
                        env_dict[k] = v
        except Exception:
            pass
    return env_dict

def get_config() -> SimpleNamespace:
    """Return a configuration object with required attributes.
    Expected keys (at minimum):
        - ``telegram_token``
        - ``admin_id``
        - ``project`` (optional, used by cloud agent)
    Environment variables override values from ``config.yaml``.
    """
    # Load .env / credentials.txt directly from possible root files to populate os.environ
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_env_files = [
        os.path.join(base_dir, ".env"),
        os.path.join(base_dir, "credentials.txt"),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "credentials.txt")
    ]
    
    env_vars = {}
    for pf in possible_env_files:
        if os.path.isfile(pf):
            env_vars = _load_env_file(pf)
            break
            
    # Populate os.environ with variables loaded from file, prioritizing .env
    for k, v in env_vars.items():
        os.environ[k] = v

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
        
    if "admin_id" in cfg:
        try:
            cfg["admin_id"] = int(cfg["admin_id"])
        except ValueError:
            pass

    # Validate required fields
    required = ["telegram_token", "admin_id"]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise RuntimeError(f"Missing required configuration keys: {', '.join(missing)}")

    return SimpleNamespace(**cfg)
