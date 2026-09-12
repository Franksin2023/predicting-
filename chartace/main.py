"""
Main entry point for Chartace system.
"""

import sys
import logging
from chartace.config.settings import settings
from chartace.orchestration.orchestrator import StrategyOrchestrator

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Chartace.Main")


def main():
    """
    Initialize and start the Chartace framework.
    """
    logger.info(f"Starting {settings.app_name} system...")
    orchestrator = StrategyOrchestrator()

    for symbol in settings.symbols:
        result = orchestrator.run_cycle(symbol)
        logger.info(f"Cycle result for {symbol}: {result}")


if __name__ == "__main__":
    main()
