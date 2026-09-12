"""
Feature engineering module.
"""

import pandas as pd


class FeatureEngineer:
    """
    Generates technical indicators and custom features from raw price data.
    """

    def compute_sma(self, df: pd.DataFrame, column: str = "close", window: int = 20) -> pd.Series:
        """Compute Simple Moving Average."""
        if df.empty or column not in df.columns:
            return pd.Series(dtype=float)
        return df[column].rolling(window=window).mean()

    def compute_rsi(self, df: pd.DataFrame, column: str = "close", window: int = 14) -> pd.Series:
        """Compute Relative Strength Index."""
        if df.empty or column not in df.columns:
            return pd.Series(dtype=float)
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def generate_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate full suite of feature columns."""
        if df.empty:
            return df
        features_df = df.copy()
        if "close" in features_df.columns:
            features_df["sma_20"] = self.compute_sma(features_df, "close", 20)
            features_df["rsi_14"] = self.compute_rsi(features_df, "close", 14)
        return features_df
