"""
Expected Value (EV) evaluation engine module.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Literal
import numpy as np


@dataclass
class TradeHypothesis:
    direction: Literal["LONG", "SHORT"]
    entry_price: float
    stop_loss: float
    take_profit: float

    @property
    def risk(self) -> float:
        return abs(self.entry_price - self.stop_loss)

    @property
    def reward(self) -> float:
        return abs(self.take_profit - self.entry_price)


@dataclass
class EVResult:
    hypothesis: TradeHypothesis
    adjusted_win_probability: float
    expected_value_r: float
    is_viable: bool
    reasoning: str


class MetaModelAndEVEngine:
    """
    Evaluates expected value and trade quality scores based on model probabilities and market regimes.
    """

    def __init__(self, min_ev_r: float = 0.20, cost_bps: float = 5.0):
        self.min_ev_r = min_ev_r
        self.cost_pct = cost_bps / 10000.0

    def evaluate_market(
        self,
        current_price: float,
        current_atr: float,
        regime_state: Any,
        model_probs: Dict[str, float]
    ) -> Dict[str, Any]:
        stop_dist = current_atr * 1.5
        target_dist = current_atr * 3.0

        long_hyp = TradeHypothesis("LONG", current_price, current_price - stop_dist, current_price + target_dist)
        short_hyp = TradeHypothesis("SHORT", current_price, current_price + stop_dist, current_price - target_dist)

        results = {}
        for hyp in [long_hyp, short_hyp]:
            base_prob, weight = 0.5, 0.5

            if hyp.direction == "LONG":
                if getattr(regime_state, "trend", "") == "STRONG_TREND":
                    base_prob, weight = model_probs.get('trend', 0.5), 1.0
                elif getattr(regime_state, "trend", "") == "MEAN_REVERTING":
                    base_prob, weight = model_probs.get('mean_reversion', 0.5), 0.7
            else:
                if getattr(regime_state, "trend", "") == "STRONG_TREND":
                    base_prob, weight = model_probs.get('mean_reversion', 0.5), 0.6
                elif getattr(regime_state, "trend", "") == "MEAN_REVERTING":
                    base_prob, weight = 1.0 - model_probs.get('trend', 0.5), 0.8

            if getattr(regime_state, "volatility", "") == "HIGH_VOL_SHOCK":
                weight *= 0.5

            adj_prob = float(np.clip((base_prob * weight) + (0.5 * (1 - weight)), 0.35, 0.85))

            gross_ev = (adj_prob * hyp.reward) - ((1 - adj_prob) * hyp.risk)
            cost_per_share = hyp.entry_price * (self.cost_pct * 2)
            net_ev = gross_ev - cost_per_share
            ev_r = float(net_ev / hyp.risk) if hyp.risk > 0 else 0.0

            is_viable = (ev_r >= self.min_ev_r) and (adj_prob > 0.50)
            results[hyp.direction] = EVResult(hyp, adj_prob, ev_r, is_viable, f"EV: {ev_r:.2f}R, Prob: {adj_prob:.1%}")

        viable = [r for r in results.values() if r.is_viable]
        if not viable:
            return {"decision": "NO_TRADE", "reason": "No hypothesis met min EV threshold", "evaluations": results}

        best = max(viable, key=lambda x: x.expected_value_r)
        return {"decision": "TRADE", "ev_result": best, "evaluations": results}


class EVEngine(MetaModelAndEVEngine):
    """
    Backward-compatible alias for MetaModelAndEVEngine.
    """

    def evaluate_opportunity(self, signal: Dict[str, Any], regime: str) -> Dict[str, Any]:
        probability_win = signal.get("confidence", 0.5)
        reward_ratio = signal.get("reward_ratio", 1.5)

        ev = (probability_win * reward_ratio) - ((1 - probability_win) * 1.0)

        return {
            "symbol": signal.get("symbol", ""),
            "expected_value": round(ev, 4),
            "is_actionable": ev > 0.1,
            "regime": regime
        }
