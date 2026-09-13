"""
Risk governance and position sizing module.
"""

from dataclasses import dataclass
from typing import Any, Optional
import numpy as np


@dataclass
class PortfolioState:
    account_equity: float
    current_daily_drawdown_pct: float
    open_positions_count: int
    daily_pnl: float


@dataclass
class RiskVerdict:
    approved: bool
    position_size_units: float
    reason: str


class RiskGovernor:
    """
    Evaluates trade hypotheses against portfolio risk constraints and position sizing limits.
    """

    def __init__(
        self,
        max_daily_drawdown_pct: float = 10.0,
        max_open_positions: int = 3,
        risk_per_trade_pct: float = 1.5
    ):
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        self.max_open_positions = max_open_positions
        self.risk_per_trade_pct = risk_per_trade_pct

    def evaluate_risk(self, ev_result: Any, portfolio_state: PortfolioState, current_spread_bps: float) -> 'RiskVerdict':
        """
        Evaluate a trade hypothesis against risk constraints.
        
        Args:
            ev_result: EVResult object with hypothesis and expected_value_r
            portfolio_state: Current portfolio state
            current_spread_bps: Bid-ask spread in basis points
        
        Returns:
            RiskVerdict with approval status and position size
        """
        # Check daily drawdown
        if portfolio_state.current_daily_drawdown_pct >= self.max_daily_drawdown_pct:
            return RiskVerdict(
                approved=False,
                position_size_units=0,
                reason=f"Daily drawdown {portfolio_state.current_daily_drawdown_pct:.2f}% >= limit {self.max_daily_drawdown_pct}%"
            )
        
        # Check open positions limit
        if portfolio_state.open_positions_count >= self.max_open_positions:
            return RiskVerdict(
                approved=False,
                position_size_units=0,
                reason=f"Open positions {portfolio_state.open_positions_count} >= limit {self.max_open_positions}"
            )
        
        # Check EV meets threshold
        if ev_result.expected_value_r < 0.20:
            return RiskVerdict(
                approved=False,
                position_size_units=0,
                reason=f"EV {ev_result.expected_value_r:.2f}R below minimum 0.20R"
            )
        
        # Calculate position size based on risk per trade
        risk_amount = portfolio_state.account_equity * (self.risk_per_trade_pct / 100.0)
        hypothesis = ev_result.hypothesis
        
        if hypothesis.risk > 0:
            position_size = risk_amount / hypothesis.risk
        else:
            return RiskVerdict(
                approved=False,
                position_size_units=0,
                reason="Zero risk distance, cannot size position"
            )
        
        # Approval with sized position
        return RiskVerdict(
            approved=True,
            position_size_units=position_size,
            reason=f"OK: EV={ev_result.expected_value_r:.2f}R, Size={position_size:.2f} units"
        )
