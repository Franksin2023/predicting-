"""
Portfolio state synchronization with Alpaca.
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class PortfolioSyncState:
    account_equity: float
    current_daily_drawdown_pct: float
    open_positions_count: int


class AlpacaPortfolioSync:
    """
    Synchronizes portfolio state from Alpaca API.
    """

    def __init__(self, trading_client: Optional[Any] = None):
        """
        Initialize portfolio synchronizer.
        
        Args:
            trading_client: Alpaca TradingClient instance (optional)
        """
        self.trading_client = trading_client

    def fetch_synchronized_portfolio_state(self) -> PortfolioSyncState:
        """
        Fetch current portfolio state from Alpaca.
        
        Returns:
            PortfolioSyncState with current account metrics
        """
        if self.trading_client is None:
            # Return default state if no client configured
            return PortfolioSyncState(
                account_equity=100000.0,
                current_daily_drawdown_pct=0.0,
                open_positions_count=0
            )
        
        try:
            account = self.trading_client.get_account()
            positions = self.trading_client.get_all_positions()
            
            equity = float(account.portfolio_value)
            drawdown = float(account.equity) - float(account.last_equity)
            drawdown_pct = (drawdown / float(account.last_equity) * 100) if account.last_equity > 0 else 0.0
            
            return PortfolioSyncState(
                account_equity=equity,
                current_daily_drawdown_pct=min(0, drawdown_pct),  # Only negative drawdowns
                open_positions_count=len(positions) if positions else 0
            )
        except Exception as e:
            # Fallback to default state on error
            return PortfolioSyncState(
                account_equity=100000.0,
                current_daily_drawdown_pct=0.0,
                open_positions_count=0
            )
