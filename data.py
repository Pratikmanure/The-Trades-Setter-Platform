from __future__ import annotations

from typing import Iterable

import ccxt
import pandas as pd
import streamlit as st

TIMEFRAME_OPTIONS = {
    "1 Minute": "1m",
    "5 Minutes": "5m",
    "15 Minutes": "15m",
    "30 Minutes": "30m",
    "1 Hour": "1h",
    "4 Hours": "4h",
}

DEFAULT_SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "XRP/USDT",
    "ADA/USDT",
]

TIMEFRAME_LIMITS = {
    "1m": 720,
    "5m": 900,
    "15m": 1000,
    "30m": 1000,
    "1h": 1000,
    "4h": 1000,
}


def _build_exchange() -> ccxt.Exchange:
    exchange = ccxt.kraken({"enableRateLimit": True})
    exchange.load_markets()
    return exchange


def _normalize_symbol(exchange: ccxt.Exchange, symbol: str) -> str:
    candidates = [
        symbol,
        symbol.replace("USDT", "USD"),
        symbol.replace("/USDT", "/USD"),
    ]
    for candidate in candidates:
        if candidate in exchange.markets:
            return candidate
    raise ValueError(f"Symbol {symbol} is not available on the configured exchange.")


@st.cache_data(ttl=180, show_spinner=False)
def load_market_data(symbol: str, timeframe: str) -> pd.DataFrame:
    exchange = _build_exchange()
    normalized = _normalize_symbol(exchange, symbol)
    limit = TIMEFRAME_LIMITS.get(timeframe, 1000)
    ohlcv = exchange.fetch_ohlcv(normalized, timeframe=timeframe, limit=limit)
    if not ohlcv:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert(None)
    numeric_cols = ["open", "high", "low", "close", "volume"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df = df.dropna().reset_index(drop=True)
    return df


@st.cache_data(ttl=180, show_spinner=False)
def load_portfolio_data(symbols: Iterable[str], timeframe: str) -> dict[str, pd.DataFrame]:
    return {symbol: load_market_data(symbol, timeframe) for symbol in symbols}
