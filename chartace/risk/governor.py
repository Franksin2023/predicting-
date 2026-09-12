"""
Risk governor module for enforcing position sizing and portfolio risk limits.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np


@dataclass
class PortfolioState:
    account_equity: float
    current_daily_drawdown_pct: float
    open_positions_count: int
    current_asset_exposure_pct: float


@dataclass
class RiskVerdict:
    approved: bool
    position_size_units: float
    risk_amount_dollars: float
    reason: str


class RiskGovernor:
    """
    Monitors and enforces risk limits across trades and overall portfolio allocation.
    """

    def __init__(
        self,
        max_daily_drawdown_pct: float = 10.0,
        max_open_positions: int = 3,
        max_asset_exposure_pct: float = 20.0,
        risk_per_trade_pct: float = 1.5
    ):
        self.max_dd_pct = max_daily_drawdown_pct
        self.max_positions = max_open_positions
        self.max_exposure = max_asset_exposure_pct
        self.risk_per_trade = risk_per_trade_pct / 100.0

    def evaluate_risk(self, ev_result: Any, portfolio: PortfolioState, current_spread_bps: float) -> RiskVerdict:
        hyp = ev_result.hypothesis

        if portfolio.current_daily_drawdown_pct >= self.max_dd_pct:
            return RiskVerdict(False, 0.0, 0.0, f"DD limit hit ({portfolio.current_daily_drawdown_pct:.1f}%)")
        if portfolio.open_positions_count >= self.max_positions:
            return RiskVerdict(False, 0.0, 0.0, f"Max positions ({self.max_positions}) reached")
        if portfolio.current_asset_exposure_pct >= self.max_exposure:
            return RiskVerdict(False, 0.0, 0.0, f"Exposure limit ({self.max_exposure}%) reached")
        if current_spread_bps > 15.0:
            return RiskVerdict(False, 0.0, 0.0, f"Spread too wide ({current_spread_bps} bps)")

        target_risk_dollars = portfolio.account_equity * self.risk_per_trade
        ev_multiplier = float(np.clip(ev_result.expected_value_r * 2.0, 0.5, 1.5))
        adjusted_risk_dollars = target_risk_dollars * ev_multiplier

        risk_per_unit = hyp.risk
        if risk_per_unit <= 0:
            return RiskVerdict(False, 0.0, 0.0, "Invalid risk distance")

        position_size = adjusted_risk_dollars / risk_per_unit
        return RiskVerdict(True, round(position_size, 4), round(adjusted_risk_dollars, 2), "Approved")

    def calculate_position_size(self, portfolio_value: float, entry_price: float, stop_loss: float) -> int:
        """
        Backward-compatible helper for calculating share sizes.
        """
        if entry_price <= 0 or stop_loss >= entry_price or portfolio_value <= 0:
            return 0

        risk_per_share = entry_price - stop_loss
        max_risk_amount = portfolio_value * self.risk_per_trade
        return max(0, int(max_risk_amount / risk_per_share))

    def validate_trade(self, trade_proposal: Dict[str, Any], current_exposure: float) -> bool:
        """
        Check if a trade proposal complies with portfolio risk constraints.
        """
        return current_exposure < (1.0 - (self.max_dd_pct / 100.0))
