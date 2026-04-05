from __future__ import annotations

import math
import sqlite3
from itertools import product
from typing import Iterable

import numpy as np
import pandas as pd
import ta

from data import load_portfolio_data


def _annualization_factor(timeframe: str) -> float:
    mapping = {
        "1m": 365 * 24 * 60,
        "5m": 365 * 24 * 12,
        "15m": 365 * 24 * 4,
        "30m": 365 * 24 * 2,
        "1h": 365 * 24,
        "4h": 365 * 6,
    }
    return float(mapping.get(timeframe, 365 * 24))


def _safe_value(value: float) -> float:
    if pd.isna(value) or np.isinf(value):
        return 0.0
    return float(value)


def _compute_streaks(trades: pd.DataFrame) -> tuple[int, int]:
    if trades.empty:
        return 0, 0
    wins = trades["net_return_pct"] > 0
    max_win = max_loss = current_win = current_loss = 0
    for is_win in wins:
        if is_win:
            current_win += 1
            current_loss = 0
        else:
            current_loss += 1
            current_win = 0
        max_win = max(max_win, current_win)
        max_loss = max(max_loss, current_loss)
    return max_win, max_loss


def _trade_sql_insights(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["metric", "value"])

    sql_df = trades.copy()
    sql_df["entry_time"] = pd.to_datetime(sql_df["entry_time"])
    sql_df["exit_time"] = pd.to_datetime(sql_df["exit_time"])
    sql_df["trade_day"] = sql_df["exit_time"].dt.day_name()

    conn = sqlite3.connect(":memory:")
    sql_df.to_sql("trades", conn, index=False, if_exists="replace")

    best_day = pd.read_sql_query(
        """
        SELECT trade_day AS metric, ROUND(AVG(net_return_pct), 4) AS value
        FROM trades
        GROUP BY trade_day
        ORDER BY value DESC
        LIMIT 1
        """,
        conn,
    )
    best_day["metric"] = "Best Day"

    avg_duration = pd.read_sql_query(
        """
        SELECT 'Avg Duration (hrs)' AS metric,
               ROUND(AVG(duration_minutes) / 60.0, 4) AS value
        FROM trades
        """,
        conn,
    )

    avg_trade = pd.read_sql_query(
        """
        SELECT 'Avg Trade Return %' AS metric,
               ROUND(AVG(net_return_pct), 4) AS value
        FROM trades
        """,
        conn,
    )
    conn.close()
    return pd.concat([best_day, avg_duration, avg_trade], ignore_index=True)


def _build_trade_log(df: pd.DataFrame) -> pd.DataFrame:
    flips = df.index[df["trade_trigger"] != 0].tolist()
    trades: list[dict] = []
    entry_index = None
    entry_signal = 0

    for idx in flips:
        signal = int(df.at[idx, "signal"])
        if entry_index is None:
            entry_index = idx
            entry_signal = signal
            continue

        exit_row = df.loc[idx]
        entry_row = df.loc[entry_index]
        gross = (exit_row["close"] / entry_row["close"] - 1.0) * 100.0
        if entry_signal < 0:
            gross *= -1

        trades.append(
            {
                "entry_time": entry_row["timestamp"],
                "exit_time": exit_row["timestamp"],
                "side": "LONG" if entry_signal > 0 else "SHORT",
                "entry_price": entry_row["close"],
                "exit_price": exit_row["close"],
                "net_return_pct": gross,
                "bars_held": idx - entry_index,
                "duration_minutes": (exit_row["timestamp"] - entry_row["timestamp"]).total_seconds() / 60.0,
            }
        )
        entry_index = idx
        entry_signal = signal

    return pd.DataFrame(trades)


def _event_log(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    signal_events = df.loc[df["trade_trigger"] != 0, ["timestamp", "trade_trigger", "close"]].copy()
    if signal_events.empty:
        return pd.DataFrame(columns=["timestamp", "event", "detail"])
    signal_events["event"] = np.where(signal_events["trade_trigger"] > 0, "Signal Flip Long", "Signal Flip Short")
    signal_events["detail"] = signal_events.apply(
        lambda row: f"{symbol} changed regime at {row['close']:.2f}",
        axis=1,
    )
    return signal_events[["timestamp", "event", "detail"]].sort_values("timestamp", ascending=False)


def prepare_indicators(df: pd.DataFrame, ema_periods: Iterable[int], show_rsi: bool, show_macd: bool) -> pd.DataFrame:
    data = df.copy()
    for period in sorted(set(int(period) for period in ema_periods)):
        data[f"ema_{period}"] = data["close"].ewm(span=period, adjust=False).mean()

    if show_rsi:
        data["rsi"] = ta.momentum.RSIIndicator(close=data["close"], window=14).rsi()
    else:
        data["rsi"] = np.nan

    if show_macd:
        macd_indicator = ta.trend.MACD(close=data["close"], window_slow=26, window_fast=12, window_sign=9)
        data["macd"] = macd_indicator.macd()
        data["macd_signal"] = macd_indicator.macd_signal()
        data["macd_hist"] = macd_indicator.macd_diff()
    else:
        data["macd"] = np.nan
        data["macd_signal"] = np.nan
        data["macd_hist"] = np.nan
    return data


def run_strategy(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    ema_periods: Iterable[int],
    fast_ema: int,
    slow_ema: int,
    initial_capital: float,
    fee_bps: float,
    slippage_bps: float,
    show_rsi: bool,
    show_macd: bool,
    benchmark: str,
) -> dict:
    if df.empty:
        return {
            "data": df,
            "trades": pd.DataFrame(),
            "kpis": {"total_return": 0.0, "win_rate": 0.0, "max_drawdown": 0.0, "sharpe_ratio": 0.0},
            "summary": {},
            "sql_insights": pd.DataFrame(columns=["metric", "value"]),
            "event_log": pd.DataFrame(columns=["timestamp", "event", "detail"]),
        }

    fast_ema = int(fast_ema)
    slow_ema = int(slow_ema)
    if fast_ema >= slow_ema:
        slow_ema = fast_ema + 1

    all_emas = sorted(set([fast_ema, slow_ema, *list(ema_periods)]))
    data = prepare_indicators(df, all_emas, show_rsi, show_macd)
    data["signal"] = np.where(data[f"ema_{fast_ema}"] > data[f"ema_{slow_ema}"], 1, -1)
    data["signal"] = pd.Series(data["signal"], index=data.index).ffill().fillna(-1)
    data["trade_trigger"] = data["signal"].diff().fillna(0)
    data["market_returns"] = data["close"].pct_change().fillna(0.0)

    execution_cost = (fee_bps + slippage_bps) / 10000.0
    cost_series = np.where(data["trade_trigger"] != 0, execution_cost, 0.0)
    data["strategy_returns"] = (data["signal"].shift(1).fillna(0.0) * data["market_returns"]) - cost_series
    data["benchmark_returns"] = data["market_returns"] if benchmark == "Buy & Hold" else 0.0

    data["equity_curve"] = initial_capital * (1.0 + data["strategy_returns"]).cumprod()
    data["benchmark_curve"] = initial_capital * (1.0 + data["benchmark_returns"]).cumprod()
    data["equity_peak"] = data["equity_curve"].cummax()
    data["drawdown"] = ((data["equity_curve"] / data["equity_peak"]) - 1.0) * 100.0

    annualization = _annualization_factor(timeframe)
    returns_std = data["strategy_returns"].std()
    sharpe_ratio = 0.0 if returns_std == 0 or pd.isna(returns_std) else (data["strategy_returns"].mean() / returns_std) * math.sqrt(annualization)

    trades = _build_trade_log(data)
    if not trades.empty:
        trades["net_return_pct"] = trades["net_return_pct"] - ((fee_bps + slippage_bps) / 100.0)

    total_return = ((data["equity_curve"].iloc[-1] / initial_capital) - 1.0) * 100.0
    max_drawdown = abs(data["drawdown"].min()) if not data["drawdown"].empty else 0.0
    win_rate = (trades["net_return_pct"].gt(0).mean() * 100.0) if not trades.empty else 0.0
    avg_profit = trades.loc[trades["net_return_pct"] > 0, "net_return_pct"].mean() if not trades.empty else 0.0
    max_loss = trades["net_return_pct"].min() if not trades.empty else 0.0
    max_win_streak, max_loss_streak = _compute_streaks(trades)

    summary = {
        "symbol": symbol,
        "timeframe": timeframe,
        "fast_ema": fast_ema,
        "slow_ema": slow_ema,
        "avg_profit": _safe_value(avg_profit),
        "max_loss": _safe_value(max_loss),
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
        "trade_count": int(len(trades)),
        "last_close": _safe_value(data["close"].iloc[-1]),
        "benchmark_return": _safe_value(((data["benchmark_curve"].iloc[-1] / initial_capital) - 1.0) * 100.0),
    }

    kpis = {
        "total_return": _safe_value(total_return),
        "win_rate": _safe_value(win_rate),
        "max_drawdown": _safe_value(max_drawdown),
        "sharpe_ratio": _safe_value(sharpe_ratio),
    }

    return {
        "data": data,
        "trades": trades,
        "kpis": kpis,
        "summary": summary,
        "sql_insights": _trade_sql_insights(trades),
        "event_log": _event_log(data, symbol),
    }


def compare_strategies(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    ema_periods: Iterable[int],
    left_pair: tuple[int, int],
    right_pair: tuple[int, int],
    initial_capital: float,
    fee_bps: float,
    slippage_bps: float,
    show_rsi: bool,
    show_macd: bool,
    benchmark: str,
) -> dict:
    left = run_strategy(
        df=df,
        symbol=symbol,
        timeframe=timeframe,
        ema_periods=ema_periods,
        fast_ema=left_pair[0],
        slow_ema=left_pair[1],
        initial_capital=initial_capital,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        show_rsi=show_rsi,
        show_macd=show_macd,
        benchmark=benchmark,
    )
    right = run_strategy(
        df=df,
        symbol=symbol,
        timeframe=timeframe,
        ema_periods=ema_periods,
        fast_ema=right_pair[0],
        slow_ema=right_pair[1],
        initial_capital=initial_capital,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        show_rsi=show_rsi,
        show_macd=show_macd,
        benchmark=benchmark,
    )

    diff = pd.DataFrame(
        {
            "metric": ["Total Return", "Win Rate", "Max Drawdown", "Sharpe Ratio"],
            "primary": [left["kpis"]["total_return"], left["kpis"]["win_rate"], left["kpis"]["max_drawdown"], left["kpis"]["sharpe_ratio"]],
            "comparison": [right["kpis"]["total_return"], right["kpis"]["win_rate"], right["kpis"]["max_drawdown"], right["kpis"]["sharpe_ratio"]],
        }
    )
    diff["delta"] = diff["primary"] - diff["comparison"]
    return {"left": left, "right": right, "diff": diff}


def optimize_strategy(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    short_range: Iterable[int],
    long_range: Iterable[int],
    initial_capital: float,
    fee_bps: float,
    slippage_bps: float,
) -> dict:
    records = []
    for fast, slow in product(short_range, long_range):
        if fast >= slow:
            continue
        result = run_strategy(
            df=df,
            symbol=symbol,
            timeframe=timeframe,
            ema_periods=[fast, slow],
            fast_ema=fast,
            slow_ema=slow,
            initial_capital=initial_capital,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            show_rsi=False,
            show_macd=False,
            benchmark="Buy & Hold",
        )
        records.append(
            {
                "fast_ema": fast,
                "slow_ema": slow,
                "total_return": result["kpis"]["total_return"],
                "sharpe_ratio": result["kpis"]["sharpe_ratio"],
                "max_drawdown": result["kpis"]["max_drawdown"],
            }
        )
    heatmap_df = pd.DataFrame(records)
    pivot = heatmap_df.pivot(index="fast_ema", columns="slow_ema", values="total_return") if not heatmap_df.empty else pd.DataFrame()
    return {"raw": heatmap_df, "pivot": pivot}


def run_portfolio_mode(
    symbols: Iterable[str],
    timeframe: str,
    ema_periods: Iterable[int],
    fast_ema: int,
    slow_ema: int,
    initial_capital: float,
    fee_bps: float,
    slippage_bps: float,
    show_rsi: bool,
    show_macd: bool,
) -> dict:
    data_map = load_portfolio_data(tuple(symbols), timeframe)
    strategy_map = {}
    returns_frames = []
    summary_rows = []

    for symbol, df in data_map.items():
        result = run_strategy(
            df=df,
            symbol=symbol,
            timeframe=timeframe,
            ema_periods=ema_periods,
            fast_ema=fast_ema,
            slow_ema=slow_ema,
            initial_capital=initial_capital,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            show_rsi=show_rsi,
            show_macd=show_macd,
            benchmark="Buy & Hold",
        )
        strategy_map[symbol] = result
        if not result["data"].empty:
            returns_frames.append(
                result["data"][["timestamp", "strategy_returns"]].rename(columns={"strategy_returns": symbol})
            )
            summary_rows.append(
                {
                    "symbol": symbol,
                    "total_return": result["kpis"]["total_return"],
                    "sharpe_ratio": result["kpis"]["sharpe_ratio"],
                    "max_drawdown": result["kpis"]["max_drawdown"],
                    "trade_count": result["summary"].get("trade_count", 0),
                }
            )

    if not returns_frames:
        return {"summary": pd.DataFrame(), "equity": pd.DataFrame(), "strategies": strategy_map}

    merged = returns_frames[0]
    for frame in returns_frames[1:]:
        merged = merged.merge(frame, on="timestamp", how="outer")
    merged = merged.sort_values("timestamp").fillna(0.0)
    asset_cols = [col for col in merged.columns if col != "timestamp"]
    merged["portfolio_returns"] = merged[asset_cols].mean(axis=1)
    merged["portfolio_equity"] = initial_capital * (1.0 + merged["portfolio_returns"]).cumprod()
    merged["portfolio_peak"] = merged["portfolio_equity"].cummax()
    merged["portfolio_drawdown"] = ((merged["portfolio_equity"] / merged["portfolio_peak"]) - 1.0) * 100.0
    return {
        "summary": pd.DataFrame(summary_rows),
        "equity": merged,
        "strategies": strategy_map,
    }
