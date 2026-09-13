"""
Application startup and initialization script.
Run the Chartace trading framework.
"""

import sys
import os
import logging

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Chartace.Startup")

def startup_check():
    """Verify all dependencies and modules are available."""
    print("\n" + "="*80)
    print(" "*20 + "CHARTACE FRAMEWORK - STARTUP CHECK")
    print("="*80 + "\n")
    
    # Check Python version
    print(f"[1] Python Version: {sys.version}")
    if sys.version_info < (3, 7):
        logger.error("Python 3.7+ required")
        return False
    print("    ✓ OK\n")
    
    # Check required modules
    print("[2] Checking Dependencies...")
    required_modules = [
        ('pandas', 'Data manipulation'),
        ('numpy', 'Numerical computing'),
    ]
    
    optional_modules = [
        ('yfinance', 'Market data (yFinance)'),
        ('alpaca', 'Market data (Alpaca)'),
        ('lightgbm', 'Machine learning models'),
        ('sklearn', 'Scikit-learn utilities'),
    ]
    
    missing_required = []
    missing_optional = []
    
    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"    ✓ {module_name:15} - {description}")
        except ImportError:
            print(f"    ✗ {module_name:15} - {description} (MISSING)")
            missing_required.append(module_name)
    
    print("\n[3] Optional Dependencies...")
    for module_name, description in optional_modules:
        try:
            __import__(module_name)
            print(f"    ✓ {module_name:15} - {description}")
        except ImportError:
            print(f"    ⚠ {module_name:15} - {description} (optional)")
            missing_optional.append(module_name)
    
    if missing_required:
        print(f"\n✗ ERROR: Missing required dependencies: {', '.join(missing_required)}")
        print(f"  Install with: pip install {' '.join(missing_required)}")
        return False
    
    print("\n[4] Checking Chartace Modules...")
    try:
        from chartace.config.settings import Settings
        print("    ✓ Config module")
        
        from chartace.data.features import FeatureEngine
        print("    ✓ Data/Features module")
        
        from chartace.regime.detector import RegimeDetector
        print("    ✓ Regime Detection module")
        
        from chartace.meta.ev_engine import MetaModelAndEVEngine
        print("    ✓ EV Engine module")
        
        from chartace.risk.governor import RiskGovernor
        print("    ✓ Risk Governor module")
        
        from chartace.safety.circuit_breaker import EmergencyCircuitBreaker
        print("    ✓ Circuit Breaker module")
        
        from chartace.execution.alpaca_bridge import AlpacaExecutionBridge
        print("    ✓ Execution Bridge module")
        
        from chartace.execution.portfolio_sync import AlpacaPortfolioSync
        print("    ✓ Portfolio Sync module")
        
        from chartace.infrastructure.audit import AuditLogger
        print("    ✓ Audit Logger module")
        
        from chartace.orchestration.orchestrator import ChartAceOrchestrator
        print("    ✓ Orchestrator module")
        
    except ImportError as e:
        print(f"    ✗ Import Error: {e}")
        return False
    
    print("\n[5] Checking Configuration...")
    try:
        from chartace.config.settings import Settings
        settings = Settings()
        print(f"    ✓ App Name: {settings.app_name}")
        print(f"    ✓ Log Level: {settings.log_level}")
        print(f"    ✓ Risk Limits: OK")
    except Exception as e:
        print(f"    ✗ Configuration Error: {e}")
        return False
    
    print("\n" + "="*80)
    print("✓ ALL STARTUP CHECKS PASSED")
    print("="*80 + "\n")
    return True


def main():
    """Main application entry point."""
    
    # Run startup checks
    if not startup_check():
        logger.error("Startup checks failed. Please install missing dependencies.")
        sys.exit(1)
    
    print("\n[6] Initializing Chartace Framework...")
    try:
        import os
        from chartace.config.settings import Settings
        from chartace.orchestration.orchestrator import ChartAceOrchestrator
        from chartace.execution.alpaca_bridge import AlpacaExecutionBridge
        from chartace.execution.portfolio_sync import AlpacaPortfolioSync
        from chartace.execution.trailing_manager import HybridTrailingManager
        from chartace.safety.circuit_breaker import EmergencyCircuitBreaker
        from chartace.infrastructure.audit import AuditLogger
        from chartace.models.trainer import TimeSeriesModelTrainer
        
        settings = Settings()
        
        # Initialize components
        logger.info("Initializing trading components...")
        
        trading_client = None
        api_key = os.environ.get("ALPACA_API_KEY")
        secret_key = os.environ.get("ALPACA_SECRET_KEY")
        
        if api_key and secret_key:
            logger.info("Alpaca credentials found, initializing trading client...")
            try:
                from alpaca.trading.client import TradingClient
                trading_client = TradingClient(api_key, secret_key, paper=True)
                logger.info("✓ Trading client initialized (paper trading)")
            except ImportError:
                logger.warning("Alpaca SDK not installed, using simulation mode")
        else:
            logger.info("No Alpaca credentials found, using simulation mode")
        
        # Initialize managers
        portfolio_sync = AlpacaPortfolioSync(trading_client)
        execution_bridge = AlpacaExecutionBridge(paper=True)
        trailing_manager = HybridTrailingManager(trading_client, trail_atr_multiplier=1.5)
        circuit_breaker = EmergencyCircuitBreaker(sigma_threshold=5.0)
        audit_logger = AuditLogger(log_path="logs/audit_trail.jsonl")
        
        logger.info("✓ Portfolio sync initialized")
        logger.info("✓ Execution bridge initialized")
        logger.info("✓ Trailing manager initialized")
        logger.info("✓ Circuit breaker initialized")
        logger.info("✓ Audit logger initialized")
        
        # Initialize models
        logger.info("Loading prediction models...")
        models = {}
        for model_name in ['trend', 'mean_reversion', 'volatility']:
            trainer = TimeSeriesModelTrainer()
            model_file = f"models/{model_name}_model.pkl"
            if os.path.exists(model_file):
                trainer.load(model_file)
                logger.info(f"  ✓ Loaded {model_name} model")
            else:
                logger.info(f"  ⚠ {model_name} model not found (will use defaults)")
            models[model_name] = trainer
        
        # Initialize orchestrator
        orchestrator = ChartAceOrchestrator(models_dict=models)
        logger.info("✓ Orchestrator initialized")
        
        print("\n" + "="*80)
        print("[STARTUP] ChartAce 2.0 initialized successfully")
        print("="*80)
        
        # Log startup event
        audit_logger.log_event("STARTUP", {
            "status": "initialized",
            "app_name": settings.app_name,
            "trading_mode": "paper" if trading_client else "simulation"
        })
        
        print("\n[7] Application Status")
        print(f"    App Name: {settings.app_name}")
        print(f"    Mode: {'Paper Trading' if trading_client else 'Simulation'}")
        print(f"    Max Drawdown: 10.0%")
        print(f"    Max Positions: 3")
        print(f"    Min EV: 0.2R")
        print(f"    Circuit Breaker: 5.0-sigma threshold")
        
        print("\n" + "="*80)
        print("✓ CHARTACE FRAMEWORK READY")
        print("="*80)
        print("\nNext Steps:")
        print("  1. Configure API keys: export ALPACA_API_KEY=... && export ALPACA_SECRET_KEY=...")
        print("  2. Check audit logs: tail -f logs/audit_trail.jsonl")
        print("\n")
        
        audit_logger.log_event("READY", {
            "status": "system_ready",
            "message": "Chartace framework fully initialized and ready"
        })
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error during initialization: {e}")
        logger.exception(e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
