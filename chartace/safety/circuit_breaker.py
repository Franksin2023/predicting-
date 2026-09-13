"""
Emergency circuit breaker and market shock detection module.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd


@dataclass
class CircuitBreakerState:
    tripped: bool
    reason: str
    severity: str


class EmergencyCircuitBreaker:
    """
    Detects extreme market shocks (e.g., 5-sigma moves) and triggers trading halts.
    """

    def __init__(
        self,
        sigma_threshold: float = 5.0,
        check_window_bars: int = 5,
        reset_cooldown_minutes: int = 30
    ):
        self.sigma_threshold = sigma_threshold
        self.check_window_bars = check_window_bars
        self.reset_cooldown_minutes = reset_cooldown_minutes
        self.last_trip_time: Optional[float] = None

    def check_shock(self, bars: pd.DataFrame) -> CircuitBreakerState:
        """
        Check if recent price movement exceeds shock threshold.
        
        Args:
            bars: DataFrame with OHLCV data (must have 'close' column)
        
        Returns:
            CircuitBreakerState indicating if breaker is tripped
        """
        if bars.empty or len(bars) < self.check_window_bars:
            return CircuitBreakerState(tripped=False, reason="Insufficient data", severity="NONE")
        
        recent = bars.iloc[-self.check_window_bars:]
        closes = recent['close'].values
        
        if len(closes) < 2:
            return CircuitBreakerState(tripped=False, reason="Insufficient bars", severity="NONE")
        
        # Calculate returns and z-score
        returns = np.diff(closes) / closes[:-1]
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return CircuitBreakerState(tripped=False, reason="Zero volatility", severity="NONE")
        
        latest_return = returns[-1]
        z_score = abs((latest_return - mean_return) / std_return)
        
        if z_score > self.sigma_threshold:
            return CircuitBreakerState(
                tripped=True,
                reason=f"{z_score:.2f}-sigma move detected ({latest_return*100:.2f}%)",
                severity="CRITICAL"
            )
        
        return CircuitBreakerState(tripped=False, reason="Normal", severity="NONE")


class DynamicFrictionModeler:
    """
    Models transaction costs and market friction for position sizing.
    """

    def __init__(self, baseline_cost_bps: float = 5.0):
        """
        Args:
            baseline_cost_bps: Baseline transaction cost in basis points
        """
        self.baseline_cost_bps = baseline_cost_bps

    def calculate_friction(self, position_size: float, volatility: float, liquidity_score: float) -> float:
        """
        Calculate dynamic transaction cost based on market conditions.
        
        Args:
            position_size: Size of position in units
            volatility: Current realized volatility
            liquidity_score: Relative liquidity (0-1, where 1 = most liquid)
        
        Returns:
            Estimated transaction cost in basis points
        """
        # Base cost
        cost = self.baseline_cost_bps
        
        # Adjust for volatility (higher vol = higher cost)
        cost *= (1.0 + volatility)
        
        # Adjust for liquidity (lower liquidity = higher cost)
        if liquidity_score < 1.0:
            cost *= (1.0 / max(liquidity_score, 0.1))
        
        return max(cost, self.baseline_cost_bps)
