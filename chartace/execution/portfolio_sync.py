"""
Portfolio state synchronizer.
"""

import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from chartace.risk.governor import PortfolioState


class AlpacaPortfolioSync:
    """
    Synchronizes local portfolio state with Alpaca TradingClient API.
    """

    def __init__(self, trading_client: Any):
        self.client = trading_client
        self._starting_equity_today: Optional[float] = None
        self._peak_equity_today: Optional[float] = None
        self._last_reset_date: Optional[Any] = None

    def _update_equity_baselines(self, current_equity: float):
        today = datetime.now(timezone.utc).date()

        if self._last_reset_date != today:
            self._starting_equity_today = current_equity
            self._peak_equity_today = current_equity
            self._last_reset_date = today
        else:
            if self._peak_equity_today is None or current_equity > self._peak_equity_today:
                self._peak_equity_today = current_equity

    def fetch_synchronized_portfolio_state(self) -> PortfolioState:
        if self.client is None or not hasattr(self.client, "get_account"):
            equity = 100000.0
            self._update_equity_baselines(equity)
            return PortfolioState(
                account_equity=equity,
                current_daily_drawdown_pct=0.0,
                open_positions_count=0,
                current_asset_exposure_pct=0.0
            )

        account = self.client.get_account()
        positions = self.client.get_all_positions()

        equity = float(account.equity)
        self._update_equity_baselines(equity)

        total_notional_exposure = sum(float(pos.market_value) for pos in positions)
        exposure_pct = (total_notional_exposure / equity) * 100 if equity > 0 else 0

        if self._peak_equity_today and self._peak_equity_today > 0:
            drawdown_val = self._peak_equity_today - equity
            drawdown_pct = max(0.0, (drawdown_val / self._peak_equity_today) * 100)
        else:
            drawdown_pct = 0.0

        open_count = len(positions)

        return PortfolioState(
            account_equity=equity,
            current_daily_drawdown_pct=round(drawdown_pct, 2),
            open_positions_count=open_count,
            current_asset_exposure_pct=round(exposure_pct, 2)
        )


class PortfolioSync(AlpacaPortfolioSync):
    """
    Backward-compatible alias for AlpacaPortfolioSync.
    """

    def __init__(self, broker_bridge: Any = None):
        super().__init__(trading_client=getattr(broker_bridge, "client", None))
        self.broker = broker_bridge

    def sync_positions(self) -> List[Dict[str, Any]]:
        return []

    def sync_orders(self) -> List[Dict[str, Any]]:
        return []
