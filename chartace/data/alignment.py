"""
Timeframe alignment and data synchronization.
"""

import pandas as pd
from typing import Dict, List


class TimeframeAligner:
    """
    Aligns OHLCV data across different timeframes.
    """

    def __init__(self):
        pass

    def align_frames(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Align multiple DataFrames to common timestamps.
        
        Args:
            data_dict: Dictionary of symbol -> DataFrame
        
        Returns:
            Aligned dictionary of DataFrames
        """
        if not data_dict:
            return data_dict
        
        # Get common index (intersection of all indices)
        common_index = None
        for df in data_dict.values():
            if common_index is None:
                common_index = df.index
            else:
                common_index = common_index.intersection(df.index)
        
        # Reindex all DataFrames to common index
        aligned = {}
        for symbol, df in data_dict.items():
            aligned[symbol] = df.loc[common_index].copy()
        
        return aligned
