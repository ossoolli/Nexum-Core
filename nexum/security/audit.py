import logging
import json
from datetime import datetime
from nexum.config import config

audit_logger = logging.getLogger("nexum.audit")

class AuditEvent:
    COMMAND_EXECUTED = "COMMAND_EXECUTED"
    COMMAND_BLOCKED  = "COMMAND_BLOCKED"
    COMMAND_PENDING  = "COMMAND_PENDING"
    AGENT_SPAWNED    = "AGENT_SPAWNED"
    DEPLOY_TRIGGERED = "DEPLOY_TRIGGERED"
    FILE_ACCESSED    = "FILE_ACCESSED"

def log_audit(event_type: str, user_id: int, details: dict):
    entry = {
        "timestamp": datetime.utcnow().timestamp(),
        "human_time": datetime.utcnow().isoformat(),
        "event": event_type,
        "user_id": user_id,
        "details": details,
    }
    audit_logger.info(json.dumps(entry, ensure_ascii=False))
