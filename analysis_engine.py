import pandas as pd
import pandas_ta as ta
import numpy as np

def calculate_indicators(df):
    """
    Calculates technical indicators for a given dataframe of a single ticker.
    df should have columns: Open, High, Low, Close, Volume
    """
    if df.empty or len(df) < 2:
        return df

    # Ensure columns are float and lowercase names for pandas_ta if needed, 
    # but yfinance returns Title Case. pandas_ta usually handles it.
    
    # EMAs
    df['EMA_9'] = ta.ema(df['Close'], length=9)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    df['EMA_50'] = ta.ema(df['Close'], length=50)
    df['EMA_200'] = ta.ema(df['Close'], length=200)

    # RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)

    # MACD
    macd = ta.macd(df['Close'])
    if macd is not None:
        df = pd.concat([df, macd], axis=1)

    # Bollinger Bands
    bbands = ta.bbands(df['Close'], length=20, std=2)
    if bbands is not None:
        df = pd.concat([df, bbands], axis=1)

    # ATR
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)

    # Relative Volume
    df['Vol_Avg_20'] = ta.sma(df['Volume'], length=20)
    df['Rel_Vol'] = df['Volume'] / df['Vol_Avg_20']

    # Manual Candlestick Patterns
    df['body'] = (df['Close'] - df['Open']).abs()
    df['range'] = df['High'] - df['Low']
    df['prev_open'] = df['Open'].shift(1)
    df['prev_close'] = df['Close'].shift(1)
    df['prev_body'] = (df['prev_close'] - df['prev_open']).abs()

    # Bullish Engulfing
    df['CDL_BULLISH_ENGULFING'] = (
        (df['prev_close'] < df['prev_open']) & 
        (df['Close'] > df['Open']) & 
        (df['Close'] >= df['prev_open']) & 
        (df['Open'] <= df['prev_close'])
    ).astype(int) * 100

    # Hammer
    df['CDL_HAMMER'] = (
        (df['range'] > 3 * df['body']) & 
        ((df['Low'] - df[['Open', 'Close']].min(axis=1)) > 0.6 * df['range']) &
        ((df['High'] - df[['Open', 'Close']].max(axis=1)) < 0.1 * df['range'])
    ).astype(int) * 100

    # Morning Star (Simplified 3-candle)
    df['prev2_open'] = df['Open'].shift(2)
    df['prev2_close'] = df['Close'].shift(2)
    df['CDL_MORNING_STAR'] = (
        (df['prev2_close'] < df['prev2_open']) & # Bearish first
        ((df['prev_close'] - df['prev_open']).abs() < (df['prev2_open'] - df['prev2_close']).abs() * 0.3) & # Small second
        (df['Close'] > df['Open']) & # Bullish third
        (df['Close'] > (df['prev2_open'] + df['prev2_close']) / 2) # Third closes above midpoint of first
    ).astype(int) * 100

    # Cleanup temp columns
    df.drop(columns=['body', 'range', 'prev_open', 'prev_close', 'prev_body', 'prev2_open', 'prev2_close'], inplace=True)

    return df

def get_weekly_data(df):
    """
    Converts daily data to weekly data and calculates indicators.
    """
    if df.empty:
        return df
    # Assuming df index is datetime
    logic = {
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }
    weekly_df = df.resample('W').apply(logic)
    return calculate_indicators(weekly_df)

if __name__ == "__main__":
    import yfinance as yf
    test_df = yf.download("AAPL", period="1y")
    if isinstance(test_df.columns, pd.MultiIndex):
        test_df.columns = test_df.columns.get_level_values(0)
    
    analyzed_df = calculate_indicators(test_df)
    print(analyzed_df.tail())
    print("Patterns detected in last 20 days:")
    print(analyzed_df[['CDL_BULLISH_ENGULFING', 'CDL_HAMMER', 'CDL_MORNING_STAR']].tail(20))
