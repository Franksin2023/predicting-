"""
Strategy orchestration engine.
"""

from typing import List, Dict, Any
import logging

from chartace.data.fetchers import DataFetcher
from chartace.regime.detector import RegimeDetector
from chartace.risk.governor import RiskGovernor
from chartace.execution.alpaca_bridge import AlpacaBridge

logger = logging.getLogger("Chartace.Orchestrator")


class StrategyOrchestrator:
    """
    Main orchestration engine connecting data pipeline, regime detection, risk, and execution.
    """

    def __init__(self):
        self.fetcher = DataFetcher()
        self.regime_detector = RegimeDetector()
        self.risk_governor = RiskGovernor()
        self.execution_bridge = AlpacaBridge()

    def run_cycle(self, symbol: str) -> Dict[str, Any]:
        """
        Execute a single pipeline cycle for a target symbol.
        """
        logger.info(f"Running pipeline cycle for {symbol}...")
        quote = self.fetcher.fetch_latest_quote(symbol)
        account = self.execution_bridge.get_account()

        return {
            "status": "cycle_completed",
            "symbol": symbol,
            "quote": quote,
            "account_status": account.get("status")
        }
