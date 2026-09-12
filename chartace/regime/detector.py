"""
Market regime detector module.
"""

from dataclasses import dataclass
from typing import Dict, Any, Literal
import numpy as np
import pandas as pd


@dataclass
class RegimeState:
    volatility: Literal["LOW_VOL", "NORMAL_VOL", "HIGH_VOL_SHOCK"]
    trend: Literal["STRONG_TREND", "WEAK_TREND", "MEAN_REVERTING"]
    liquidity: Literal["NORMAL", "LOW_LIQUIDITY"]
    confidence: float

    def should_halt_trading(self) -> bool:
        return self.liquidity == "LOW_LIQUIDITY" or self.volatility == "HIGH_VOL_SHOCK"


class RegimeDetector:
    """
    Classifies market conditions into volatility, trend, and liquidity regimes.
    """

    def __init__(self, lookback: int = 100):
        self.lookback = lookback
        self.lookback_period = lookback

    def classify(self, features: pd.DataFrame) -> RegimeState:
        if len(features) < self.lookback:
            return RegimeState("NORMAL_VOL", "WEAK_TREND", "NORMAL", 0.5)

        latest = features.iloc[-1]
        history = features.iloc[-self.lookback:]

        bb_pct = (history['bb_width'].rank(pct=True).iloc[-1]) * 100
        vol_pct = (history['realized_vol_15'].rank(pct=True).iloc[-1]) * 100

        if bb_pct > 90 or vol_pct > 90:
            vol_regime = "HIGH_VOL_SHOCK"
        elif bb_pct < 25 and vol_pct < 25:
            vol_regime = "LOW_VOL"
        else:
            vol_regime = "NORMAL_VOL"

        adx = latest['adx_14'] if not pd.isna(latest['adx_14']) else 20
        hurst = latest['hurst_50'] if not pd.isna(latest['hurst_50']) else 0.5

        if adx > 25 and hurst > 0.55:
            trend_regime = "STRONG_TREND"
        elif hurst < 0.45 and adx < 20:
            trend_regime = "MEAN_REVERTING"
        else:
            trend_regime = "WEAK_TREND"

        vol_pct_10 = (history['rel_volume'].rank(pct=True).iloc[-1]) * 100
        liq_regime = "LOW_LIQUIDITY" if vol_pct_10 < 10 else "NORMAL"

        return RegimeState(vol_regime, trend_regime, liq_regime, 0.75)

    def detect_regime(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Backward-compatible wrapper method.
        """
        if df.empty or len(df) < self.lookback:
            return {"regime": "UNKNOWN", "confidence": 0.0}

        state = self.classify(df)
        return {
            "volatility": state.volatility,
            "trend": state.trend,
            "liquidity": state.liquidity,
            "confidence": state.confidence,
            "should_halt": state.should_halt_trading()
        }
