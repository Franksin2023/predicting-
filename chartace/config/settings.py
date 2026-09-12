"""
Configuration settings for Chartace algorithmic trading framework.
"""

import os
from dataclasses import dataclass, field
from typing import List


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


settings = Settings()
