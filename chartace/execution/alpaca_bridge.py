"""
Alpaca broker bridge interface.
"""

from typing import Dict, Any, List, Optional


class AlpacaBridge:
    """
    Interface for submitting orders and receiving execution reports from Alpaca API.
    """

    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url

    def submit_order(self, symbol: str, qty: int, side: str, order_type: str = "market", time_in_force: str = "gtc") -> Dict[str, Any]:
        """
        Submit an order to the Alpaca API.
        """
        return {
            "id": "ord_mock_12345",
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
            "status": "submitted"
        }

    def get_account(self) -> Dict[str, Any]:
        """
        Get current Alpaca account summary.
        """
        return {
            "cash": 100000.0,
            "portfolio_value": 100000.0,
            "buying_power": 400000.0,
            "status": "ACTIVE"
        }
