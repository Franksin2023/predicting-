"""
Persistence helper utilities.
"""

import json
import os
import sqlite3
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class TrackedPosition:
    order_id: str
    symbol: str
    side: str
    entry_price: float
    qty: float
    initial_atr: float
    peak_price: float
    current_stop_loss: float
    take_profit: float
    stop_order_id: Optional[str] = None


class TrailingStopStore:
    """
    SQLite persistence store for tracked positions and trailing stop state.
    """

    def __init__(self, db_path: str = "data/chartace_state.db"):
        self.db_path = db_path
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tracked_positions (
                    symbol TEXT PRIMARY KEY,
                    side TEXT,
                    entry_price REAL,
                    qty REAL,
                    initial_atr REAL,
                    peak_price REAL,
                    current_stop_loss REAL,
                    take_profit REAL,
                    stop_order_id TEXT
                )
            """)
            conn.commit()

    def save_position(self, pos: TrackedPosition):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tracked_positions
                (symbol, side, entry_price, qty, initial_atr, peak_price, current_stop_loss, take_profit, stop_order_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pos.symbol, pos.side, pos.entry_price, pos.qty,
                pos.initial_atr, pos.peak_price, pos.current_stop_loss,
                pos.take_profit, pos.stop_order_id
            ))
            conn.commit()

    def remove_position(self, symbol: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM tracked_positions WHERE symbol = ?", (symbol,))
            conn.commit()

    def load_all_positions(self) -> Dict[str, TrackedPosition]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol, side, entry_price, qty, initial_atr, peak_price, current_stop_loss, take_profit, stop_order_id FROM tracked_positions")
            rows = cursor.fetchall()

        positions = {}
        for row in rows:
            symbol = row[0]
            positions[symbol] = TrackedPosition(
                order_id="",
                symbol=symbol,
                side=row[1],
                entry_price=row[2],
                qty=row[3],
                initial_atr=row[4],
                peak_price=row[5],
                current_stop_loss=row[6],
                take_profit=row[7],
                stop_order_id=row[8]
            )
        return positions


class PersistenceManager:
    """
    Manages local json state and configuration persistence.
    """

    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir

    def save_json(self, data: Dict[str, Any], filename: str) -> str:
        """
        Save dictionary object to JSON file.
        """
        os.makedirs(self.base_dir, exist_ok=True)
        filepath = os.path.join(self.base_dir, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        return filepath

    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load dictionary object from JSON file.
        """
        filepath = os.path.join(self.base_dir, filename)
        if not os.path.exists(filepath):
            return {}
        with open(filepath, "r") as f:
            return json.load(f)
