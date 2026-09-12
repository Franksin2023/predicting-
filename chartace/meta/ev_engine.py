"""
Expected Value (EV) evaluation engine module.
"""

from typing import Dict, Any, List


class EVEngine:
    """
    Evaluates expected value and trade quality scores based on model signals and market regimes.
    """

    def evaluate_opportunity(self, signal: Dict[str, Any], regime: str) -> Dict[str, Any]:
        """
        Calculate expected value, win rate estimate, and risk reward ratio.
        """
        probability_win = signal.get("confidence", 0.5)
        reward_ratio = signal.get("reward_ratio", 1.5)

        ev = (probability_win * reward_ratio) - ((1 - probability_win) * 1.0)

        return {
            "symbol": signal.get("symbol", ""),
            "expected_value": round(ev, 4),
            "is_actionable": ev > 0.1,
            "regime": regime
        }
