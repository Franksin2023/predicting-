"""
Persistence layer for trailing stops and position tracking.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TrackedPosition:
    symbol: str
    entry_price: float
    quantity: float
    direction: str  # 'LONG' or 'SHORT'
    entry_time: str
    trailing_stop: float
    take_profit: float


class TrailingStopStore:
    """
    Stores and retrieves trailing stop information for positions.
    """

    def __init__(self):
        self.positions: Dict[str, TrackedPosition] = {}

    def add_position(self, position: TrackedPosition) -> None:
        """Add a tracked position."""
        self.positions[position.symbol] = position

    def get_position(self, symbol: str) -> Optional[TrackedPosition]:
        """Get a tracked position by symbol."""
        return self.positions.get(symbol)

    def update_trailing_stop(self, symbol: str, new_stop: float) -> bool:
        """Update trailing stop for a position."""
        if symbol in self.positions:
            self.positions[symbol].trailing_stop = new_stop
            return True
        return False

    def remove_position(self, symbol: str) -> bool:
        """Remove a tracked position."""
        if symbol in self.positions:
            del self.positions[symbol]
            return True
        return False

    def list_positions(self) -> List[TrackedPosition]:
        """List all tracked positions."""
        return list(self.positions.values())
