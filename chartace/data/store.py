"""
Feature store for caching and managing computed features.
"""

import pandas as pd
from typing import Dict, Optional


class FeatureStore:
    """
    In-memory store for computed features.
    """

    def __init__(self):
        self.features: Dict[str, pd.DataFrame] = {}

    def store_features(self, symbol: str, features: pd.DataFrame) -> None:
        """Store features for a symbol."""
        self.features[symbol] = features.copy()

    def get_features(self, symbol: str) -> Optional[pd.DataFrame]:
        """Retrieve features for a symbol."""
        return self.features.get(symbol)

    def list_symbols(self) -> list:
        """List all stored symbols."""
        return list(self.features.keys())
