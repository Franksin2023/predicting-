"""
Data alignment and synchronization module.
"""

from typing import List, Dict
import pandas as pd
from chartace.config.settings import Timeframe, TIMEFRAME_MINUTES


class TimeframeAligner:
    """
    Aligns time-series features across multiple timeframes.
    """

    def __init__(self, base_timeframe: Timeframe = Timeframe.H1):
        self.base_tf = base_timeframe
        self.base_minutes = TIMEFRAME_MINUTES.get(base_timeframe, 60)

    def align(self, feature_frames: Dict[Timeframe, pd.DataFrame]) -> pd.DataFrame:
        if self.base_tf not in feature_frames:
            raise ValueError(f"Base timeframe {self.base_tf} not in feature_frames")

        base_df = feature_frames[self.base_tf].copy()
        base_df = base_df.add_suffix(f"_{self.base_tf.value}")

        for tf, df in feature_frames.items():
            if tf == self.base_tf:
                continue

            df_suffixed = df.add_suffix(f"_{tf.value}")
            aligned = self._align_single(base_df.index, df_suffixed, tf)
            base_df = base_df.join(aligned, how="left")

        return base_df

    def _align_single(self, base_index: pd.DatetimeIndex, higher_df: pd.DataFrame, tf: Timeframe) -> pd.DataFrame:
        tf_minutes = TIMEFRAME_MINUTES.get(tf, 240)

        higher_df = higher_df.copy()
        higher_df["close_time"] = higher_df.index + pd.Timedelta(minutes=tf_minutes)
        higher_df = higher_df.reset_index().rename(columns={"index": "bar_time"})
        higher_df = higher_df.set_index("close_time").sort_index()

        base_df = pd.DataFrame({"base_time": base_index}).set_index("base_time")

        aligned = pd.merge_asof(
            base_df,
            higher_df,
            left_index=True,
            right_index=True,
            direction="backward",
        )

        aligned = aligned.drop(columns=["bar_time"], errors="ignore")
        aligned.index.name = None

        return aligned


class DataAligner(TimeframeAligner):
    """
    Backward-compatible alias for TimeframeAligner.
    """
    def align_timestamps(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Align multiple DataFrames to a common timestamp index.
        """
        if not dataframes:
            return {}

        common_index = None
        for df in dataframes.values():
            if not df.empty:
                if common_index is None:
                    common_index = df.index
                else:
                    common_index = common_index.intersection(df.index)

        if common_index is None:
            return dataframes

        aligned = {}
        for symbol, df in dataframes.items():
            if not df.empty:
                aligned[symbol] = df.reindex(common_index)
            else:
                aligned[symbol] = df
        return aligned
