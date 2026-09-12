"""
Data alignment and synchronization module.
"""

from typing import List, Dict
import pandas as pd


class DataAligner:
    """
    Aligns time-series data across multiple instruments or timeframes.
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
