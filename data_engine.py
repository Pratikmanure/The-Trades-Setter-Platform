import yfinance as yf
import pandas as pd
import numpy as np

def fetch_crypto_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        return df
    except Exception as e:
        return pd.DataFrame()

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df.dropna(inplace=True)
    return df

def apply_strategy(df: pd.DataFrame, fast_ema: int = 9, slow_ema: int = 21) -> dict:
    df = df.copy()
    
    df['ema_fast'] = df['close'].ewm(span=fast_ema, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=slow_ema, adjust=False).mean()
    
    df['signal'] = np.where(df['ema_fast'] > df['ema_slow'], 1, -1)
    df['trade_trigger'] = df['signal'].diff()
    
    df['market_returns'] = df['close'].pct_change().fillna(0)
    df['strategy_returns'] = df['market_returns'] * df['signal'].shift(1)
    df['strategy_returns'] = df['strategy_returns'].fillna(0)
    
    initial_capital = 10000.0
    df['equity_curve'] = initial_capital * (1 + df['strategy_returns']).cumprod()
    
    df['peak'] = df['equity_curve'].cummax()
    df['drawdown'] = ((df['equity_curve'] - df['peak']) / df['peak']) * 100
    
    total_return = ((df['equity_curve'].iloc[-1] / initial_capital) - 1) * 100 if not df.empty else 0
    max_drawdown = abs(df['drawdown'].min()) if not df.empty else 0
    
    returns_std = df['strategy_returns'].std()
    sharpe_ratio = (df['strategy_returns'].mean() / returns_std) * np.sqrt(365) if returns_std > 0 else 0.0
        
    trades_executed = len(df[df['strategy_returns'] != 0])
    win_rate = (len(df[df['strategy_returns'] > 0]) / trades_executed) * 100 if trades_executed > 0 else 0
    
    # Generate simple Trade Log
    buys = df[df['trade_trigger'] == 2].copy()
    buys['Action'] = 'BUY'
    sells = df[df['trade_trigger'] == -2].copy()
    sells['Action'] = 'SELL'
    
    trade_log = pd.concat([buys, sells]).sort_index()
    if not trade_log.empty:
        trade_log = trade_log[['Action', 'close', 'ema_fast', 'ema_slow', 'equity_curve']]
        trade_log.reset_index(inplace=True)
    
    return {
        "df": df,
        "trade_log": trade_log,
        "kpi": {
            "total_return": total_return,
            "win_rate": win_rate,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
        }
    }

def get_live_data(symbol: str, fast_ema: int = 9, slow_ema: int = 21, period: str = "1y", interval: str = "1d") -> dict:
    raw_df = fetch_crypto_data(symbol, period, interval)
    if raw_df.empty:
        return {}
        
    clean_df = clean_data(raw_df)
    strategy_results = apply_strategy(clean_df, fast_ema, slow_ema)
    df_return = strategy_results['df']
    
    df_return = df_return.reset_index()
    if 'Date' in df_return.columns:
        df_return['Date'] = pd.to_datetime(df_return['Date'], utc=True).dt.date
    elif 'Datetime' in df_return.columns:
        df_return = df_return.rename(columns={'Datetime': 'Date'})
        df_return['Date'] = pd.to_datetime(df_return['Date'], utc=True).dt.date
        
    strategy_results['df'] = df_return
    return strategy_results

def optimize_strategy(symbol: str, period: str = "1y", interval: str = "1d"):
    raw_df = fetch_crypto_data(symbol, period, interval)
    clean = clean_data(raw_df)
    if clean.empty: return pd.DataFrame()
    
    results = []
    # Grid search ranges for visual heatmap (fast: 5-20, slow: 20-50, step 5)
    for f in range(5, 25, 5):
        for s in range(25, 65, 5):
            kpi = apply_strategy(clean, f, s)['kpi']
            results.append({'Fast MA': f, 'Slow MA': s, 'Total Return': kpi['total_return']})
            
    res_df = pd.DataFrame(results)
    return res_df.pivot(index='Slow MA', columns='Fast MA', values='Total Return')
