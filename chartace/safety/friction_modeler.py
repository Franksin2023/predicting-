"""
Slippage and transaction friction modeling module.
"""

from datetime import datetime, timezone
from typing import Dict, Any


class DynamicFrictionModeler:
    """
    Calculates dynamic transaction costs, bid-ask spread, and market impact slippage.
    """

    def __init__(self, baseline_cost_bps: float = 5.0):
        self.baseline_cost_bps = baseline_cost_bps

    def calculate_friction(
        self,
        symbol: str,
        current_quote: dict,
        adv: float,
        rolling_avg_spread_bps: float
    ) -> float:
        bid = current_quote.get("bid", 0.0)
        ask = current_quote.get("ask", 0.0)

        if bid > 0 and ask > bid:
            current_spread_bps = ((ask - bid) / bid) * 10000.0
        else:
            current_spread_bps = rolling_avg_spread_bps if rolling_avg_spread_bps > 0 else self.baseline_cost_bps

        hour = datetime.now(timezone.utc).hour
        time_multiplier = 1.5 if hour in [14, 15, 20, 21] else 1.0

        adv_multiplier = 1.5 if adv < 1_000_000 else 1.0

        if current_spread_bps > (2.0 * rolling_avg_spread_bps):
            friction_bps = current_spread_bps * time_multiplier
        else:
            base_friction = rolling_avg_spread_bps if rolling_avg_spread_bps > 0 else self.baseline_cost_bps
            friction_bps = base_friction * adv_multiplier * time_multiplier

        return round(friction_bps, 2)


class FrictionModeler(DynamicFrictionModeler):
    """
    Backward-compatible alias for DynamicFrictionModeler.
    """

    def __init__(self, fixed_commission: float = 0.0, slippage_bps: float = 5.0):
        super().__init__(baseline_cost_bps=slippage_bps)
        self.fixed_commission = fixed_commission
        self.slippage_bps = slippage_bps

    def estimate_execution_price(self, side: str, price: float) -> float:
        slippage_factor = (self.slippage_bps / 10000.0)
        if side.lower() == "buy":
            return round(price * (1.0 + slippage_factor), 4)
        elif side.lower() == "sell":
            return round(price * (1.0 - slippage_factor), 4)
        return price
