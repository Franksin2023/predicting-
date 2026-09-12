"""
Audit and trade activity logger.
"""

import logging
from datetime import datetime
from typing import Dict, Any


class AuditLogger:
    """
    Records trade execution logs and system state changes for audit trails.
    """

    def __init__(self, log_name: str = "chartace_audit"):
        self.logger = logging.getLogger(log_name)

    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log structured system event.
        """
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details
        }
        self.logger.info(f"AUDIT_EVENT: {record}")
