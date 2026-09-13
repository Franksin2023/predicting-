"""
Audit logging and event tracking.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict


class AuditLogger:
    """
    Logs all trading events to JSONL file for auditing and analysis.
    """

    def __init__(self, log_path: str = "logs/audit_trail.jsonl"):
        """
        Initialize audit logger.
        
        Args:
            log_path: Path to audit log file
        """
        self.log_path = log_path
        
        # Create log directory if it doesn't exist
        os.makedirs(os.path.dirname(log_path) if os.path.dirname(log_path) else ".", exist_ok=True)

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log an event to the audit trail.
        
        Args:
            event_type: Type of event (e.g., 'TRADE', 'CIRCUIT_BREAKER_TRIPPED')
            data: Event data dictionary
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        try:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            print(f"Error writing to audit log: {e}")
