"""
Persistence helper utilities.
"""

import json
import os
from typing import Dict, Any


class PersistenceManager:
    """
    Manages local json state and configuration persistence.
    """

    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir

    def save_json(self, data: Dict[str, Any], filename: str) -> str:
        """
        Save dictionary object to JSON file.
        """
        os.makedirs(self.base_dir, exist_ok=True)
        filepath = os.path.join(self.base_dir, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        return filepath

    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load dictionary object from JSON file.
        """
        filepath = os.path.join(self.base_dir, filename)
        if not os.path.exists(filepath):
            return {}
        with open(filepath, "r") as f:
            return json.load(f)
