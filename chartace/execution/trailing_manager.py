"""
Trailing stop and dynamic position manager.
"""

import os
from typing import Dict, Any, Optional


class HybridTrailingManager:
    """
    Manages dynamic ATR trailing stops, take profits, and native order safety with Alpaca TradingClient API.
    """

    def __init__(self, trading_client: Any, trail_atr_multiplier: float = 1.5):
        self.client = trading_client
        self.trail_mult = trail_atr_multiplier
        self.tracked_positions: Dict[str, Dict[str, Any]] = {}

    def submit_bracket_with_native_safety(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        qty: float,
        initial_atr: float,
        take_profit: float
    ) -> dict:
        trail_distance = initial_atr * self.trail_mult

        if self.client is None or not hasattr(self.client, "submit_order"):
            mock_entry_id = "mock_entry_123"
            mock_trail_id = "mock_trail_123"
            mock_tp_id = "mock_tp_123"
            self.tracked_positions[symbol] = {
                "entry_order_id": mock_entry_id,
                "trailing_stop_id": mock_trail_id,
                "take_profit_id": mock_tp_id,
                "side": side,
                "entry_price": entry_price,
                "qty": qty,
                "initial_atr": initial_atr,
                "peak_price": entry_price,
                "current_trail_distance": trail_distance
            }
            return {
                "status": "SUBMITTED_WITH_NATIVE_SAFETY",
                "entry_order_id": mock_entry_id,
                "trailing_stop_id": mock_trail_id,
                "take_profit_id": mock_tp_id
            }

        try:
            from alpaca.trading.requests import LimitOrderRequest, TrailingStopOrderRequest
            from alpaca.trading.enums import OrderSide, TimeInForce

            entry_side = OrderSide.BUY if side == "LONG" else OrderSide.SELL
            entry_order = self.client.submit_order(
                LimitOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=entry_side,
                    time_in_force=TimeInForce.GTC,
                    limit_price=round(entry_price, 2)
                )
            )

            stop_side = OrderSide.SELL if side == "LONG" else OrderSide.BUY
            trailing_stop = self.client.submit_order(
                TrailingStopOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=stop_side,
                    time_in_force=TimeInForce.GTC,
                    trail_price=round(trail_distance, 2)
                )
            )

            tp_side = OrderSide.SELL if side == "LONG" else OrderSide.BUY
            take_profit_order = self.client.submit_order(
                LimitOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=tp_side,
                    time_in_force=TimeInForce.GTC,
                    limit_price=round(take_profit, 2)
                )
            )

            self.tracked_positions[symbol] = {
                "entry_order_id": entry_order.id,
                "trailing_stop_id": trailing_stop.id,
                "take_profit_id": take_profit_order.id,
                "side": side,
                "entry_price": entry_price,
                "qty": qty,
                "initial_atr": initial_atr,
                "peak_price": entry_price,
                "current_trail_distance": trail_distance
            }

            return {
                "status": "SUBMITTED_WITH_NATIVE_SAFETY",
                "entry_order_id": entry_order.id,
                "trailing_stop_id": trailing_stop.id,
                "take_profit_id": take_profit_order.id
            }

        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def optimize_trailing_stop(self, symbol: str, current_price: float, current_atr: float):
        if symbol not in self.tracked_positions:
            return

        pos = self.tracked_positions[symbol]

        if pos["side"] == "LONG" and current_price > pos["peak_price"]:
            pos["peak_price"] = current_price
        elif pos["side"] == "SHORT" and current_price < pos["peak_price"]:
            pos["peak_price"] = current_price

        optimal_trail = current_atr * self.trail_mult

        if optimal_trail < pos["current_trail_distance"] and self.client is not None and hasattr(self.client, "cancel_order_by_id"):
            try:
                from alpaca.trading.requests import TrailingStopOrderRequest
                from alpaca.trading.enums import OrderSide, TimeInForce

                self.client.cancel_order_by_id(pos["trailing_stop_id"])

                stop_side = OrderSide.SELL if pos["side"] == "LONG" else OrderSide.BUY
                new_trailing_stop = self.client.submit_order(
                    TrailingStopOrderRequest(
                        symbol=symbol,
                        qty=pos["qty"],
                        side=stop_side,
                        time_in_force=TimeInForce.GTC,
                        trail_price=round(optimal_trail, 2)
                    )
                )

                pos["trailing_stop_id"] = new_trailing_stop.id
                pos["current_trail_distance"] = optimal_trail

            except Exception as e:
                pass


class TrailingManager(HybridTrailingManager):
    """
    Backward-compatible alias for HybridTrailingManager.
    """

    def __init__(self, trailing_pct: float = 0.05):
        super().__init__(trading_client=None, trail_atr_multiplier=1.5)
        self.trailing_pct = trailing_pct

    def update_stop_price(self, current_price: float, high_watermark: float) -> float:
        new_watermark = max(current_price, high_watermark)
        return round(new_watermark * (1.0 - self.trailing_pct), 2)
