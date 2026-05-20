import logging
import sys
from pathlib import Path
from nexum.config import config

def setup_logging():
    log_dir = config.storage_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    fmt = "[%(asctime)s] %(levelname)-8s %(name)-25s %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "nexum.log", encoding="utf-8"),
    ]

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format=fmt,
        datefmt=datefmt,
        handlers=handlers,
    )

    # Audit log منفصل لكل أمر حساس
    audit = logging.getLogger("nexum.audit")
    audit_handler = logging.FileHandler(
        log_dir / "audit.log", encoding="utf-8"
    )
    audit_handler.setFormatter(logging.Formatter(fmt, datefmt))
    audit.addHandler(audit_handler)
    audit.propagate = False

    return logging.getLogger("nexum")

# تهيئة أولية
logger = setup_logging()
