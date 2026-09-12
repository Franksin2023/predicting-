"""
Circuit breaker emergency module.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


@dataclass
class CircuitBreakerState:
    tripped: bool
    reason: str
    timestamp: Optional[str] = None


class EmergencyCircuitBreaker:
    """
    Monitors statistical returns and anomalies (z-score shocks) to trip emergency halt switches.
    """

    def __init__(self, sigma_threshold: float = 5.0, check_window_bars: int = 5, reset_cooldown_minutes: int = 30):
        self.sigma_threshold = sigma_threshold
        self.window = check_window_bars
        self.reset_cooldown = reset_cooldown_minutes
        self.tripped_state = CircuitBreakerState(tripped=False, reason="")
        self.trip_timestamp = None

    def check_shock(self, recent_bars: pd.DataFrame) -> CircuitBreakerState:
        if len(recent_bars) < self.window + 50:
            return self.tripped_state

        if self.tripped_state.tripped and self.trip_timestamp:
            minutes_since_trip = (datetime.now(timezone.utc) - self.trip_timestamp).total_seconds() / 60
            if minutes_since_trip < self.reset_cooldown:
                return self.tripped_state
            else:
                self.tripped_state = CircuitBreakerState(tripped=False, reason="")
                self.trip_timestamp = None

        closes = recent_bars['close']
        returns = np.log(closes / closes.shift(1)).dropna()

        rolling_mean = returns.rolling(window=50).mean().iloc[-1]
        rolling_std = returns.rolling(window=50).std().iloc[-1]

        if rolling_std == 0 or np.isnan(rolling_std):
            return self.tripped_state

        latest_return = returns.iloc[-1]
        cumulative_return = returns.iloc[-self.window:].sum()

        latest_z = (latest_return - rolling_mean) / rolling_std
        cumulative_z = (cumulative_return - (rolling_mean * self.window)) / (rolling_std * np.sqrt(self.window))

        if abs(latest_z) >= self.sigma_threshold or abs(cumulative_z) >= self.sigma_threshold:
            self.tripped_state = CircuitBreakerState(
                tripped=True,
                reason=f"Emergency Circuit Breaker: Latest z={latest_z:.2f}, Cumulative z={cumulative_z:.2f} over {self.window} bars",
                timestamp=str(recent_bars.index[-1])
            )
            self.trip_timestamp = datetime.now(timezone.utc)

        return self.tripped_state


class CircuitBreaker(EmergencyCircuitBreaker):
    """
    Backward-compatible alias for EmergencyCircuitBreaker.
    """

    def __init__(self, max_drawdown_pct: float = 0.10, sigma_threshold: float = 5.0):
        super().__init__(sigma_threshold=sigma_threshold)
        self.max_drawdown_pct = max_drawdown_pct
        self.is_tripped = False

    def check_status(self, current_equity: float, peak_equity: float) -> bool:
        if peak_equity <= 0:
            return False

        drawdown = (peak_equity - current_equity) / peak_equity
        if drawdown >= self.max_drawdown_pct:
            self.is_tripped = True

        return self.is_tripped

    def reset(self) -> None:
        self.is_tripped = False
        self.tripped_state = CircuitBreakerState(tripped=False, reason="")
        self.trip_timestamp = None
