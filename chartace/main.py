"""
Main entry point for Chartace system.
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone

from chartace.config.settings import DEFAULT_TRADING_CONFIG, settings
from chartace.orchestration.orchestrator import ChartAceOrchestrator
from chartace.execution.alpaca_bridge import AlpacaExecutionBridge
from chartace.execution.portfolio_sync import AlpacaPortfolioSync
from chartace.execution.trailing_manager import HybridTrailingManager
from chartace.safety.circuit_breaker import EmergencyCircuitBreaker
from chartace.safety.friction_modeler import DynamicFrictionModeler
from chartace.infrastructure.audit import AuditLogger
from chartace.models.trainer import TimeSeriesModelTrainer

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Chartace.Main")


def fetch_latest_bars(symbols):
    """
    Placeholder/Helper function for fetching latest price bars.
    """
    return {}


def get_latest_quote(symbol):
    """
    Placeholder/Helper function for fetching latest quote.
    """
    return {"bid": 0.0, "ask": 0.0}


def get_average_daily_volume(symbol):
    """
    Placeholder/Helper function for calculating average daily volume.
    """
    return 1_500_000.0


def get_rolling_average_spread(symbol, period=20):
    """
    Placeholder/Helper function for rolling average spread.
    """
    return 5.0


def close_all_positions(symbol, client):
    """
    Placeholder/Helper function for position liquidation.
    """
    logger.info(f"Closing all positions for {symbol} due to circuit breaker trip.")


def main():
    trading_client = None
    api_key = os.environ.get("ALPACA_API_KEY")
    secret_key = os.environ.get("ALPACA_SECRET_KEY")

    if api_key and secret_key:
        try:
            from alpaca.trading.client import TradingClient
            trading_client = TradingClient(api_key, secret_key, paper=True)
        except ImportError:
            trading_client = None

    portfolio_sync = AlpacaPortfolioSync(trading_client)
    execution_bridge = AlpacaExecutionBridge(paper=True)
    trailing_manager = HybridTrailingManager(trading_client, trail_atr_multiplier=1.5)
    circuit_breaker = EmergencyCircuitBreaker(
        sigma_threshold=DEFAULT_TRADING_CONFIG.sigma_threshold,
        check_window_bars=DEFAULT_TRADING_CONFIG.check_window_bars,
        reset_cooldown_minutes=DEFAULT_TRADING_CONFIG.reset_cooldown_minutes
    )
    friction_modeler = DynamicFrictionModeler(baseline_cost_bps=DEFAULT_TRADING_CONFIG.baseline_cost_bps)
    audit_logger = AuditLogger(log_path="logs/audit_trail.jsonl")

    models = {}
    for model_name in ['trend', 'mean_reversion', 'volatility']:
        trainer = TimeSeriesModelTrainer()
        model_file = f"models/{model_name}_model.pkl"
        if os.path.exists(model_file):
            trainer.load(model_file)
        models[model_name] = trainer

    orchestrator = ChartAceOrchestrator(models_dict=models)

    print("[STARTUP] ChartAce 2.0 initialized successfully")
    audit_logger.log_event("STARTUP", {"status": "initialized"})

    symbols = ["SPY", "QQQ", "BTC-USD"]
    latest_bars = fetch_latest_bars(symbols=symbols)

    for symbol, bars in latest_bars.items():
        breaker_state = circuit_breaker.check_shock(bars)
        if breaker_state.tripped:
            audit_logger.log_event("CIRCUIT_BREAKER_TRIPPED", {
                "symbol": symbol,
                "reason": breaker_state.reason
            })
            close_all_positions(symbol, trading_client)
            continue

    live_portfolio_state = portfolio_sync.fetch_synchronized_portfolio_state()
    audit_logger.log_event("PORTFOLIO_STATE", {
        "equity": live_portfolio_state.account_equity,
        "drawdown_pct": live_portfolio_state.current_daily_drawdown_pct,
        "open_positions": live_portfolio_state.open_positions_count
    })


if __name__ == "__main__":
    main()
