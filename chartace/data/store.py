"""
Data storage and persistence manager.
"""

import os
from typing import Optional
import pandas as pd


class DataStore:
    """
    Handles reading and writing dataset artifacts locally or to cloud storage.
    """

    def __init__(self, base_path: str = "data"):
        self.base_path = base_path

    def save_dataframe(self, df: pd.DataFrame, filename: str) -> str:
        """
        Save a DataFrame to disk.
        """
        os.makedirs(self.base_path, exist_ok=True)
        filepath = os.path.join(self.base_path, filename)
        if filename.endswith(".parquet"):
            df.to_parquet(filepath)
        else:
            df.to_csv(filepath)
        return filepath

    def load_dataframe(self, filename: str) -> pd.DataFrame:
        """
        Load a DataFrame from disk.
        """
        filepath = os.path.join(self.base_path, filename)
        if not os.path.exists(filepath):
            return pd.DataFrame()
        if filename.endswith(".parquet"):
            return pd.read_parquet(filepath)
        return pd.read_csv(filepath)
