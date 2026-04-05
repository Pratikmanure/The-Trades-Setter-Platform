import ccxt
import yfinance as yf
import pandas as pd
import numpy as np
import ta

def fetch_data(symbol: str, timeframe: str = "1d") -> pd.DataFrame:
    # Format symbol for yfinance (e.g. BTC/USDT -> BTC-USD)
    yf_symbol = symbol.replace("/", "-").replace("USDT", "USD")
    
    tf_map = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h", "4h": "1h", "1d": "1d"}
    yf_tf = tf_map.get(timeframe, "1d")
    
    # Maximize history requested (1 Year) while respecting exact API limits
    period = "1y" 
    if yf_tf == "1m": period = "7d" # max allowed
    elif yf_tf in ["5m", "15m", "30m"]: period = "60d" # max allowed
    elif yf_tf == "1h": period = "730d"
    
    try:
        # YFinance is massively more stable on Streamlit Cloud (US IPs) than Binance CCXT
        df = yf.Ticker(yf_symbol).history(period=period, interval=yf_tf).reset_index()
        if not df.empty:
            df['timestamp'] = df['Datetime'] if 'Datetime' in df.columns else df['Date']
            df.columns = [c.lower() for c in df.columns]
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    except Exception:
        pass
        
    # CCXT Fallback via Kraken (avoids Binance US IP block)
    if '/' in symbol:
        try:
            exchange = ccxt.kraken()
            # Kraken uses USD instead of USDT heavily
            ccxt_sym = symbol.replace("USDT", "USD")
            ohlcv = exchange.fetch_ohlcv(ccxt_sym, timeframe=timeframe, limit=1000)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"CCXT Error: {e}")
            return pd.DataFrame()
            
    return pd.DataFrame()

def apply_strategy(df: pd.DataFrame, ema_list: list) -> dict:
    df = df.copy()
    if df.empty or len(ema_list) < 2: 
        return {"df": df, "kpi": {"total_return": 0, "win_rate": 0, "max_drawdown": 0, "sharpe_ratio": 0}}
    
    for ema in ema_list:
        df[f'ema_{ema}'] = df['close'].ewm(span=ema, adjust=False).mean()
        
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    df['macd'] = ta.trend.MACD(df['close']).macd()
    
    fast_ema, slow_ema = ema_list[0], ema_list[1]
    df['signal'] = np.where(df[f'ema_{fast_ema}'] > df[f'ema_{slow_ema}'], 1, -1)
    df['trade_trigger'] = df['signal'].diff()
    
    df['market_returns'] = df['close'].pct_change().fillna(0)
    df['strategy_returns'] = (df['market_returns'] * df['signal'].shift(1)).fillna(0)
    
    df['equity_curve'] = 10000.0 * (1 + df['strategy_returns']).cumprod()
    df['peak'] = df['equity_curve'].cummax()
    df['drawdown'] = ((df['equity_curve'] - df['peak']) / df['peak']) * 100
    
    total_return = ((df['equity_curve'].iloc[-1] / 10000.0) - 1) * 100
    max_drawdown = abs(df['drawdown'].min())
    returns_std = df['strategy_returns'].std()
    sharpe_ratio = (df['strategy_returns'].mean() / returns_std) * np.sqrt(252 * (1440/15)) if returns_std > 0 else 0.0
    
    trades_executed = len(df[df['strategy_returns'] != 0])
    win_rate = (len(df[df['strategy_returns'] > 0]) / trades_executed) * 100 if trades_executed > 0 else 0
    return {"df": df, "kpi": {"total_return": total_return, "win_rate": win_rate, "max_drawdown": max_drawdown, "sharpe_ratio": sharpe_ratio}}
