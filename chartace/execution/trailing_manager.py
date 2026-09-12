"""
Trailing stop and dynamic position manager.
"""

from typing import Dict, Any


class TrailingManager:
    """
    Manages trailing stops, take profits, and dynamic position adjustments.
    """

    def __init__(self, trailing_pct: float = 0.05):
        self.trailing_pct = trailing_pct

    def update_stop_price(self, current_price: float, high_watermark: float) -> float:
        """
        Update the dynamic trailing stop loss level based on price movements.
        """
        new_watermark = max(current_price, high_watermark)
        return round(new_watermark * (1.0 - self.trailing_pct), 2)
