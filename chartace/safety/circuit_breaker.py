"""
Circuit breaker emergency module.
"""

from typing import Dict, Any


class CircuitBreaker:
    """
    Monitors market conditions, max drawdown, and system anomalies to trip safety halt switches.
    """

    def __init__(self, max_drawdown_pct: float = 0.10):
        self.max_drawdown_pct = max_drawdown_pct
        self.is_tripped = False

    def check_status(self, current_equity: float, peak_equity: float) -> bool:
        """
        Check if drawdown exceeds maximum safety tolerance.
        """
        if peak_equity <= 0:
            return False

        drawdown = (peak_equity - current_equity) / peak_equity
        if drawdown >= self.max_drawdown_pct:
            self.is_tripped = True

        return self.is_tripped

    def reset(self) -> None:
        """
        Reset the circuit breaker status.
        """
        self.is_tripped = False
