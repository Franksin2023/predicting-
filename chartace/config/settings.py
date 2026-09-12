"""
Configuration settings for Chartace algorithmic trading framework.
"""

import os
from dataclasses import dataclass, field
from typing import List, Literal
from enum import Enum


class Timeframe(str, Enum):
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


@dataclass
class AssetConfig:
    symbol: str
    asset_class: Literal["equity", "crypto", "forex"]
    timeframes: List[Timeframe] = field(default_factory=lambda: [Timeframe.H1, Timeframe.D1])
    enable_volume_features: bool = True


@dataclass
class PipelineConfig:
    assets: List[AssetConfig]
    lookback_days: int = 730
    feature_lag_bars: int = 1
    output_dir: str = "data/features"


@dataclass
class TradingConfig:
    # Risk parameters
    max_daily_drawdown_pct: float = 10.0
    max_open_positions: int = 3
    max_asset_exposure_pct: float = 20.0
    risk_per_trade_pct: float = 1.5

    # EV parameters
    min_ev_r: float = 0.20
    baseline_cost_bps: float = 5.0

    # Trailing stop parameters
    trail_atr_multiplier: float = 1.5
    atr_multiplier_stop: float = 1.5
    atr_multiplier_target: float = 3.0

    # Circuit breaker parameters
    sigma_threshold: float = 5.0
    check_window_bars: int = 5
    reset_cooldown_minutes: int = 30


# Default configuration
DEFAULT_ASSETS = [
    AssetConfig(symbol="SPY", asset_class="equity"),
    AssetConfig(symbol="QQQ", asset_class="equity"),
    AssetConfig(symbol="BTC-USD", asset_class="crypto"),
]

DEFAULT_PIPELINE_CONFIG = PipelineConfig(
    assets=DEFAULT_ASSETS,
    lookback_days=730,
    feature_lag_bars=1,
    output_dir="data/features"
)

DEFAULT_TRADING_CONFIG = TradingConfig()


@dataclass
class Settings:
    app_name: str = "Chartace"
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = os.getenv("CHARTACE_DATA_DIR", "data")
    logs_dir: str = os.getenv("CHARTACE_LOGS_DIR", "logs")
    models_dir: str = os.getenv("CHARTACE_MODELS_DIR", "models")
    alpaca_api_key: str = os.getenv("ALPACA_API_KEY", "")
    alpaca_secret_key: str = os.getenv("ALPACA_SECRET_KEY", "")
    alpaca_base_url: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    symbols: List[str] = field(default_factory=lambda: ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"])
    pipeline: PipelineConfig = field(default_factory=lambda: DEFAULT_PIPELINE_CONFIG)
    trading: TradingConfig = field(default_factory=lambda: DEFAULT_TRADING_CONFIG)


settings = Settings()
