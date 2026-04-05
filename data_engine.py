from data import load_market_data as fetch_data
from strategy import run_strategy


def apply_strategy(df, ema_list):
    fast = ema_list[0] if len(ema_list) > 0 else 9
    slow = ema_list[1] if len(ema_list) > 1 else 21
    return run_strategy(
        df=df,
        symbol="LEGACY",
        timeframe="15m",
        ema_periods=ema_list,
        fast_ema=fast,
        slow_ema=slow,
        initial_capital=10000.0,
        fee_bps=7.5,
        slippage_bps=2.0,
        show_rsi=True,
        show_macd=True,
        benchmark="Buy & Hold",
    )
