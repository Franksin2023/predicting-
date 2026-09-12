"""
Slippage and transaction friction modeling module.
"""

from typing import Dict, Any


class FrictionModeler:
    """
    Estimates transaction costs, spread, and market impact slippage.
    """

    def __init__(self, fixed_commission: float = 0.0, slippage_bps: float = 5.0):
        self.fixed_commission = fixed_commission
        self.slippage_bps = slippage_bps

    def estimate_execution_price(self, side: str, price: float) -> float:
        """
        Calculate expected execution price accounting for slippage.
        """
        slippage_factor = (self.slippage_bps / 10000.0)
        if side.lower() == "buy":
            return round(price * (1.0 + slippage_factor), 4)
        elif side.lower() == "sell":
            return round(price * (1.0 - slippage_factor), 4)
        return price
