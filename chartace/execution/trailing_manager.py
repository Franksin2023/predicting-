"""
Trailing stop loss and take profit management.
"""

from typing import Optional, Any, Dict


class HybridTrailingManager:
    """
    Manages trailing stops and dynamic profit targets using ATR-based distance.
    """

    def __init__(
        self,
        trading_client: Optional[Any] = None,
        trail_atr_multiplier: float = 1.5
    ):
        """
        Initialize trailing stop manager.
        
        Args:
            trading_client: Alpaca TradingClient instance
            trail_atr_multiplier: ATR multiplier for stop distance
        """
        self.trading_client = trading_client
        self.trail_atr_multiplier = trail_atr_multiplier

    def update_trailing_stops(self, position_id: str, current_price: float, atr: float) -> Dict[str, Any]:
        """
        Update trailing stop for a position based on ATR.
        
        Args:
            position_id: Position identifier
            current_price: Current market price
            atr: Average True Range value
        
        Returns:
            Result of stop update
        """
        stop_distance = atr * self.trail_atr_multiplier
        
        return {
            "position_id": position_id,
            "current_price": current_price,
            "stop_distance": stop_distance,
            "trailing_stop": current_price - stop_distance,
            "status": "updated"
        }
