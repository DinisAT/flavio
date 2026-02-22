import pandas as pd

def scan_for_signals(df, ticker):
    """
    Analyzes the latest data in df for specific swing trade entry signals.
    Returns a list of signal dictionaries.
    """
    if df.empty or len(df) < 200: # Need enough data for EMA 200
        return []

    signals = []
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    price = latest['Close']
    ema20 = latest['EMA_20']
    ema50 = latest['EMA_50']
    ema200 = latest['EMA_200']
    rsi = latest['RSI']
    rel_vol = latest['Rel_Vol']

    # --- Trend Setup ---
    is_uptrend = price > ema200 and ema50 > ema200
    
    # --- 1. Pullback Signal ---
    if is_uptrend:
        # Near EMA 20
        if abs(price - ema20) / ema20 < 0.01:
            signals.append({'ticker': ticker, 'type': 'Pullback', 'detail': 'Price near EMA 20', 'conviction': 1})
        # Near EMA 50
        elif abs(price - ema50) / ema50 < 0.01:
            signals.append({'ticker': ticker, 'type': 'Pullback', 'detail': 'Price near EMA 50', 'conviction': 1})

    # --- 2. Breakout Signal ---
    recent_high = df.iloc[-21:-1]['High'].max() # 20-day high excluding today
    if price > recent_high and rel_vol > 1.5:
        signals.append({'ticker': ticker, 'type': 'Breakout', 'detail': f'New 20-day high with {rel_vol:.2f}x vol', 'conviction': 2})

    # --- 3. Mean Reversion Signal ---
    if rsi < 35:
        detail = f'RSI Oversold ({rsi:.2f})'
        conv = 1
        if latest['CDL_BULLISH_ENGULFING'] > 0 or latest['CDL_HAMMER'] > 0 or latest['CDL_MORNING_STAR'] > 0:
            detail += ' + Bullish Candle'
            conv = 3
        signals.append({'ticker': ticker, 'type': 'Mean Reversion', 'detail': detail, 'conviction': conv})

    # --- 4. Momentum Cross ---
    if prev['EMA_9'] <= prev['EMA_20'] and latest['EMA_9'] > latest['EMA_20']:
        signals.append({'ticker': ticker, 'type': 'Momentum', 'detail': 'EMA 9 cross above EMA 20', 'conviction': 1})

    # --- 5. Candlestick Patterns alone in Uptrend ---
    if is_uptrend:
        if latest['CDL_BULLISH_ENGULFING'] > 0:
            signals.append({'ticker': ticker, 'type': 'Candle Pattern', 'detail': 'Bullish Engulfing in Uptrend', 'conviction': 2})
        if latest['CDL_HAMMER'] > 0:
            signals.append({'ticker': ticker, 'type': 'Candle Pattern', 'detail': 'Hammer in Uptrend', 'conviction': 2})
        if latest['CDL_MORNING_STAR'] > 0:
            signals.append({'ticker': ticker, 'type': 'Candle Pattern', 'detail': 'Morning Star in Uptrend', 'conviction': 2})

    return signals

def evaluate_high_conviction(signals):
    """
    If a ticker has multiple signals, combine them into a high conviction report.
    """
    if not signals:
        return None
    
    if len(signals) > 1:
        combined_detail = " | ".join([s['detail'] for s in signals])
        total_conviction = sum([s['conviction'] for s in signals])
        return {
            'ticker': signals[0]['ticker'],
            'type': 'HIGH CONVICTION',
            'detail': combined_detail,
            'conviction': total_conviction
        }
    return signals[0]
