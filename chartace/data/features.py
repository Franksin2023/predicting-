"""
Feature engineering module.
"""

import numpy as np
import pandas as pd


class FeatureEngine:
    """
    Computes technical indicators, volatility, RSI, Bollinger Bands, volume, ADX, and Hurst exponent.
    """

    def __init__(self, lag: int = 1):
        self.lag = lag

    def compute_all(self, df: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame(index=df.index)

        # Returns
        features['return_1'] = np.log(df['close'] / df['close'].shift(1))
        features['return_15'] = np.log(df['close'] / df['close'].shift(15))

        # Volatility
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        features['atr_14'] = true_range.rolling(window=14).mean()
        features['realized_vol_15'] = features['return_1'].rolling(window=15).std() * np.sqrt(252 * 24)

        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1/14, min_periods=14).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14).mean()
        rs = avg_gain / (avg_loss + 1e-6)
        features['rsi_14'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        sma_20 = df['close'].rolling(window=20).mean()
        std_20 = df['close'].rolling(window=20).std()
        features['bb_width'] = (4 * std_20) / (sma_20 + 1e-6)

        # Volume
        features['rel_volume'] = df['volume'] / (df['volume'].rolling(window=20).mean() + 1e-6)

        # ADX
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
        minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)
        atr_14_raw = true_range.rolling(window=14).mean()
        plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(window=14).mean() / (atr_14_raw + 1e-6))
        minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(window=14).mean() / (atr_14_raw + 1e-6))
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-6)
        features['adx_14'] = pd.Series(dx, index=df.index).rolling(window=14).mean()

        # Hurst Exponent Proxy
        def rolling_hurst(series, window=50):
            def hurst(ts):
                if len(ts) < 10:
                    return 0.5
                lags = range(2, min(20, len(ts)//2))
                tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
                if len(tau) < 2:
                    return 0.5
                poly = np.polyfit(np.log(list(lags)), np.log(tau), 1)
                return poly[0] * 2.0
            return series.rolling(window=window).apply(hurst, raw=True)

        features['hurst_50'] = rolling_hurst(df['close'], window=50)

        return features.shift(self.lag)


class FeatureEngineer(FeatureEngine):
    """
    Backward-compatible wrapper for FeatureEngine.
    """
    pass
