import yfinance as yf
import pandas as pd
import numpy as np

def fetch_crypto_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """ Fetches historical market data dynamically with safeguards. """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        return df
    except Exception as e:
        print(f"Failed to fetch {symbol} from Yahoo Finance: {str(e)}")
        return pd.DataFrame()

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """ Normalizes Yahoo Finance data format """
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.dropna()
    return df

def apply_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """ The Default 9/21 EMA Strategy """
    df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['signal'] = np.where(df['ema_9'] > df['ema_21'], 1, -1)
    df['trade_trigger'] = df['signal'].diff()
    return df

def get_live_data(symbol: str) -> pd.DataFrame:
    """ Main Pipeline function called by Streamlit dropdowns """
    raw_df = fetch_crypto_data(symbol)
    if raw_df.empty:
        return pd.DataFrame()
        
    clean_df = clean_data(raw_df)
    strategy_df = apply_strategy(clean_df)
    
    # Reset index so 'Date' is a column for our charts
    df_return = strategy_df.reset_index()
    if 'Date' in df_return.columns:
        df_return['Date'] = pd.to_datetime(df_return['Date'], utc=True)
    elif 'Datetime' in df_return.columns:
        df_return = df_return.rename(columns={'Datetime': 'Date'})
        df_return['Date'] = pd.to_datetime(df_return['Date'], utc=True)
        
    return df_return
