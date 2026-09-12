"""
Alpaca broker bridge interface.
"""

import os
from typing import Dict, Any, List, Optional


class AlpacaExecutionBridge:
    """
    Interface for submitting bracket orders and receiving execution reports from Alpaca API.
    """

    def __init__(self, paper: bool = True):
        api_key = os.environ.get("ALPACA_API_KEY")
        secret_key = os.environ.get("ALPACA_SECRET_KEY")

        if not api_key or not secret_key:
            self.client = None
        else:
            try:
                from alpaca.trading.client import TradingClient
                self.client = TradingClient(api_key, secret_key, paper=paper)
            except ImportError:
                self.client = None

    def execute_verdict(self, symbol: str, verdict: dict) -> Optional[str]:
        if verdict.get('action') != 'EXECUTE':
            return "No action required."

        hyp = verdict['hypothesis']
        size = verdict['size']

        if self.client is None:
            print(f"[ALPACA EXECUTION MOCK] Executed {hyp.direction} for {symbol} - {size} units at {hyp.entry_price}")
            return "mock_order_id_12345"

        from alpaca.trading.requests import LimitOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass

        side = OrderSide.BUY if hyp.direction == "LONG" else OrderSide.SELL

        order_request = LimitOrderRequest(
            symbol=symbol,
            qty=size,
            side=side,
            time_in_force=TimeInForce.GTC,
            limit_price=round(hyp.entry_price, 2),
            order_class=OrderClass.BRACKET,
            stop_loss={"stop_price": round(hyp.stop_loss, 2)},
            take_profit={"limit_price": round(hyp.take_profit, 2)}
        )

        try:
            response = self.client.submit_order(order_request)
            print(f"[ALPACA EXECUTION SUCCESS] Order ID: {response.id}")
            return str(response.id)
        except Exception as e:
            print(f"[ALPACA EXECUTION ERROR] Failed to submit order: {str(e)}")
            return None


class AlpacaBridge(AlpacaExecutionBridge):
    """
    Backward-compatible alias for AlpacaExecutionBridge.
    """

    def submit_order(self, symbol: str, qty: int, side: str, order_type: str = "market", time_in_force: str = "gtc") -> Dict[str, Any]:
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
        return {
            "cash": 100000.0,
            "portfolio_value": 100000.0,
            "buying_power": 400000.0,
            "status": "ACTIVE"
        }
