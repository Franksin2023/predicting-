"""
Audit and trade activity logger.
"""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any


class AuditLogger:
    """
    Records trade execution logs and system state changes for audit trails in JSONL format.
    """

    def __init__(self, log_path: str = "logs/audit_trail.jsonl"):
        self.log_path = log_path
        log_dir = os.path.dirname(self.log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        self.logger = logging.getLogger("ChartaceAudit")

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log structured system event to a JSONL file and Python logger.
        """
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "payload": data
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        self.logger.info(f"AUDIT_EVENT: {event_type} - {data}")
