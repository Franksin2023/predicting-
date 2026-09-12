"""
Risk governor module for enforcing position sizing and portfolio risk limits.
"""

from typing import Dict, Any, List


class RiskGovernor:
    """
    Monitors and enforces risk limits across trades and overall portfolio allocation.
    """

    def __init__(self, max_portfolio_risk_pct: float = 0.02, max_position_size_pct: float = 0.10):
        self.max_portfolio_risk_pct = max_portfolio_risk_pct
        self.max_position_size_pct = max_position_size_pct

    def calculate_position_size(self, portfolio_value: float, entry_price: float, stop_loss: float) -> int:
        """
        Calculate maximum allowable share size based on risk parameters.
        """
        if entry_price <= 0 or stop_loss >= entry_price or portfolio_value <= 0:
            return 0

        risk_per_share = entry_price - stop_loss
        max_risk_amount = portfolio_value * self.max_portfolio_risk_pct
        shares_by_risk = int(max_risk_amount / risk_per_share)

        max_position_amount = portfolio_value * self.max_position_size_pct
        shares_by_cap = int(max_position_amount / entry_price)

        return max(0, min(shares_by_risk, shares_by_cap))

    def validate_trade(self, trade_proposal: Dict[str, Any], current_exposure: float) -> bool:
        """
        Check if a trade proposal complies with portfolio risk constraints.
        """
        return current_exposure < (1.0 - self.max_portfolio_risk_pct)
