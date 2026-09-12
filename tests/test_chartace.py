import unittest
import pandas as pd
import numpy as np
from datetime import datetime

from chartace.config.settings import Settings, Timeframe, AssetConfig, PipelineConfig, TradingConfig
from chartace.data.fetchers import YFinanceFetcher
from chartace.data.features import FeatureEngine
from chartace.data.alignment import TimeframeAligner
from chartace.data.store import FeatureStore
from chartace.regime.detector import RegimeDetector, RegimeState
from chartace.meta.ev_engine import MetaModelAndEVEngine, TradeHypothesis
from chartace.risk.governor import RiskGovernor, PortfolioState
from chartace.safety.circuit_breaker import EmergencyCircuitBreaker
from chartace.safety.friction_modeler import DynamicFrictionModeler
from chartace.execution.trailing_manager import HybridTrailingManager
from chartace.execution.portfolio_sync import AlpacaPortfolioSync
from chartace.infrastructure.persistence import TrailingStopStore, TrackedPosition
from chartace.infrastructure.audit import AuditLogger
from chartace.orchestration.orchestrator import ChartAceOrchestrator


class TestChartaceModules(unittest.TestCase):

    def test_settings(self):
        s = Settings()
        self.assertEqual(s.app_name, "Chartace")
        self.assertIsNotNone(s.pipeline)
        self.assertIsNotNone(s.trading)

    def test_feature_engine(self):
        dates = pd.date_range("2023-01-01", periods=100, freq="1h")
        df = pd.DataFrame({
            "open": np.random.randn(100) + 100,
            "high": np.random.randn(100) + 102,
            "low": np.random.randn(100) + 98,
            "close": np.random.randn(100) + 100,
            "volume": np.random.randint(1000, 5000, size=100)
        }, index=dates)

        fe = FeatureEngine(lag=1)
        features = fe.compute_all(df)
        self.assertIn("return_1", features.columns)
        self.assertIn("rsi_14", features.columns)

    def test_regime_detector(self):
        detector = RegimeDetector(lookback=50)
        dates = pd.date_range("2023-01-01", periods=60, freq="1h")
        df = pd.DataFrame({
            "bb_width": np.random.rand(60),
            "realized_vol_15": np.random.rand(60),
            "adx_14": np.random.rand(60) * 30,
            "hurst_50": np.random.rand(60) * 0.6,
            "rel_volume": np.random.rand(60) * 20
        }, index=dates)

        state = detector.classify(df)
        self.assertIsInstance(state, RegimeState)

    def test_ev_engine(self):
        engine = MetaModelAndEVEngine(min_ev_r=0.20, cost_bps=5.0)
        regime = RegimeState("NORMAL_VOL", "STRONG_TREND", "NORMAL", 0.75)
        res = engine.evaluate_market(100.0, 2.0, regime, {"trend": 0.65, "mean_reversion": 0.50})
        self.assertIn("decision", res)

    def test_risk_governor(self):
        governor = RiskGovernor()
        hyp = TradeHypothesis("LONG", 100.0, 95.0, 110.0)
        from chartace.meta.ev_engine import EVResult
        ev_res = EVResult(hyp, 0.60, 0.50, True, "OK")
        portfolio = PortfolioState(100000.0, 0.0, 1, 10.0)
        verdict = governor.evaluate_risk(ev_res, portfolio, 5.0)
        self.assertTrue(verdict.approved)

    def test_circuit_breaker(self):
        breaker = EmergencyCircuitBreaker(sigma_threshold=5.0)
        dates = pd.date_range("2023-01-01", periods=60, freq="1h")
        df = pd.DataFrame({"close": np.linspace(100, 105, 60)}, index=dates)
        state = breaker.check_shock(df)
        self.assertFalse(state.tripped)


if __name__ == "__main__":
    unittest.main()
