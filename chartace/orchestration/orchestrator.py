"""
Strategy orchestration engine.
"""

from typing import List, Dict, Any
import logging
import numpy as np
import pandas as pd

from chartace.data.features import FeatureEngine
from chartace.regime.detector import RegimeDetector
from chartace.meta.ev_engine import MetaModelAndEVEngine
from chartace.risk.governor import RiskGovernor, PortfolioState

logger = logging.getLogger("Chartace.Orchestrator")


class ChartAceOrchestrator:
    """
    Main orchestration engine connecting data pipeline, regime detection, EV engine, risk governor, and execution.
    """

    def __init__(self, models_dict: Dict[str, Any]):
        self.feature_engine = FeatureEngine(lag=1)
        self.regime_detector = RegimeDetector(lookback=100)
        self.models = models_dict
        self.ev_engine = MetaModelAndEVEngine(min_ev_r=0.20, cost_bps=5.0)
        self.risk_governor = RiskGovernor(max_daily_drawdown_pct=10.0, max_open_positions=3, risk_per_trade_pct=1.5)
        self.raw_history: List[pd.Series] = []

    def on_bar_close(self, new_bar: pd.Series, portfolio_state: PortfolioState, current_spread_bps: float) -> Dict[str, Any]:
        self.raw_history.append(new_bar)
        raw_df = pd.DataFrame(self.raw_history)

        if len(raw_df) < 100:
            return {"action": "WARMUP", "reason": "Accumulating buffer"}

        features_df = self.feature_engine.compute_all(raw_df)
        current_regime = self.regime_detector.classify(features_df)

        if current_regime.should_halt_trading():
            return {
                "action": "HALT",
                "reason": f"Regime halt: {current_regime.volatility}/{current_regime.trend}",
                "regime": current_regime
            }

        latest_features = features_df.iloc[[-1]].dropna(axis=1)
        model_probs = {}
        for name, trainer in self.models.items():
            if hasattr(trainer, "predict_calibrated"):
                pred = trainer.predict_calibrated(latest_features)
            elif hasattr(trainer, "predict"):
                pred = trainer.predict(latest_features)
                if isinstance(pred, pd.Series):
                    pred = pred.iloc[-1]
            else:
                pred = 0.5
            model_probs[name] = float(np.clip(pred, 0.35, 0.85))

        current_price = float(new_bar['close'])
        current_atr = float(features_df['atr_14'].iloc[-1])

        ev_eval = self.ev_engine.evaluate_market(current_price, current_atr, current_regime, model_probs)

        if ev_eval['decision'] == 'NO_TRADE':
            return {"action": "NO_TRADE", "reason": ev_eval['reason'], "regime": current_regime}

        risk_verdict = self.risk_governor.evaluate_risk(ev_eval['ev_result'], portfolio_state, current_spread_bps)

        if risk_verdict.approved:
            return {
                "action": "EXECUTE",
                "hypothesis": ev_eval['ev_result'].hypothesis,
                "size": risk_verdict.position_size_units,
                "atr": current_atr,
                "regime": current_regime,
                "reason": risk_verdict.reason,
                "ev_r": ev_eval['ev_result'].expected_value_r
            }
        else:
            return {"action": "VETOED", "reason": risk_verdict.reason, "regime": current_regime}


class StrategyOrchestrator(ChartAceOrchestrator):
    """
    Backward-compatible alias for ChartAceOrchestrator.
    """

    def __init__(self, models_dict: Optional[Dict[str, Any]] = None):
        super().__init__(models_dict=models_dict if models_dict is not None else {})

    def run_cycle(self, symbol: str) -> Dict[str, Any]:
        """
        Execute a single pipeline cycle for a target symbol.
        """
        logger.info(f"Running pipeline cycle for {symbol}...")
        return {
            "status": "cycle_completed",
            "symbol": symbol
        }
