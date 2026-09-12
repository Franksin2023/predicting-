"""
Data fetchers module for retrieving market and financial data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol
import pandas as pd


class DataFetcher(Protocol):
    """
    Protocol definition for data fetchers.
    """

    def fetch_ohlcv(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> pd.DataFrame:
        ...


class YFinanceFetcher:
    """
    Data fetcher implementation using yfinance.
    """

    def __init__(self):
        import yfinance
        self.yf = yfinance

    def fetch_ohlcv(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> pd.DataFrame:
        interval_map = {"15m": "15m", "1h": "60m", "4h": "60m", "1d": "1d"}
        interval = interval_map[timeframe]

        ticker = self.yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval=interval)

        if df.empty:
            raise ValueError(f"No data for {symbol}")

        df = df.rename(columns={
            "Open": "open", "High": "high", "Low": "low",
            "Close": "close", "Volume": "volume"
        })[["open", "high", "low", "close", "volume"]]

        df.index.name = "timestamp"
        return df


class AlpacaFetcher:
    """
    Data fetcher implementation using Alpaca historical stock data client.
    """

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.paper = paper
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from alpaca.data.historical import StockHistoricalDataClient
            self._client = StockHistoricalDataClient(self.api_key, self.secret_key)
        return self._client

    def fetch_ohlcv(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> pd.DataFrame:
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame as AlpacaTimeFrame

        tf_map = {
            "15m": AlpacaTimeFrame.Minute * 15,
            "1h": AlpacaTimeFrame.Hour,
            "4h": AlpacaTimeFrame.Hour * 4,
            "1d": AlpacaTimeFrame.Day,
        }

        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf_map[timeframe],
            start=start,
            end=end,
        )

        bars = self.client.get_stock_bars(request)
        df = bars.df

        if isinstance(df.index, pd.MultiIndex):
            df = df.xs(symbol, level=0)

        return df[["open", "high", "low", "close", "volume"]]
