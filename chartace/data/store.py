"""
Data storage and persistence manager.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import pandas as pd


class FeatureStore:
    """
    Manages parquet persistence for feature datasets grouped by symbol and timeframe.
    """

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, symbol: str, timeframe: str) -> Path:
        symbol_dir = self.output_dir / symbol
        symbol_dir.mkdir(exist_ok=True)
        return symbol_dir / f"{timeframe}_features.parquet"

    def save(self, symbol: str, timeframe: str, df: pd.DataFrame) -> None:
        path = self._path(symbol, timeframe)
        df.to_parquet(path, engine="pyarrow")

    def load(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        path = self._path(symbol, timeframe)
        if not path.exists():
            return None
        return pd.read_parquet(path)

    def append_new(self, symbol: str, timeframe: str, df: pd.DataFrame) -> pd.DataFrame:
        existing = self.load(symbol, timeframe)

        if existing is None:
            combined = df
        else:
            last_existing = existing.index.max()
            new_rows = df[df.index > last_existing]
            combined = pd.concat([existing, new_rows])

        combined = combined[~combined.index.duplicated(keep="last")]
        combined = combined.sort_index()

        self.save(symbol, timeframe, combined)
        return combined


class DataStore(FeatureStore):
    """
    Backward-compatible DataStore subclassing FeatureStore.
    """

    def __init__(self, base_path: str = "data"):
        super().__init__(output_dir=base_path)
        self.base_path = base_path

    def save_dataframe(self, df: pd.DataFrame, filename: str) -> str:
        """
        Save a DataFrame to disk.
        """
        os.makedirs(self.base_path, exist_ok=True)
        filepath = os.path.join(self.base_path, filename)
        if filename.endswith(".parquet"):
            df.to_parquet(filepath, engine="pyarrow")
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
