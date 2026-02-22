import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def generate_interactive_chart(df, ticker, signals, output_path):
    """
    Generates an interactive Plotly chart for a stock with indicators and signals.
    """
    # Create subplots: Row 1 = Candlestick + EMAs, Row 2 = RSI, Row 3 = MACD
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, 
                        subplot_titles=(f'{ticker} Price & EMAs', 'RSI', 'MACD'),
                        row_width=[0.2, 0.2, 0.6])

    # 1. Candlestick Chart
    fig.add_trace(go.Candlestick(x=df.index,
                                open=df['Open'],
                                high=df['High'],
                                low=df['Low'],
                                close=df['Close'],
                                name='Price'), row=1, col=1)

    # Add EMAs (Check if they exist)
    for ema in ['EMA_9', 'EMA_20', 'EMA_50', 'EMA_200']:
        if ema in df.columns:
            color = 'blue' if '9' in ema else 'orange' if '20' in ema else 'red' if '50' in ema else 'black'
            width = 2 if '200' in ema else 1
            fig.add_trace(go.Scatter(x=df.index, y=df[ema], name=ema, line=dict(color=color, width=width)), row=1, col=1)

    # 2. RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # 3. MACD (Try to find columns dynamically)
    macd_cols = [c for c in df.columns if 'MACD' in c]
    # Standard pandas_ta names: MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
    macd_line = next((c for c in macd_cols if 'MACD_' in c), None)
    macd_hist = next((c for c in macd_cols if 'MACDh_' in c), None)
    macd_signal = next((c for c in macd_cols if 'MACDs_' in c), None)

    if macd_hist:
        fig.add_trace(go.Bar(x=df.index, y=df[macd_hist], name='MACD Histogram'), row=3, col=1)
    if macd_line:
        fig.add_trace(go.Scatter(x=df.index, y=df[macd_line], name='MACD', line=dict(color='blue')), row=3, col=1)
    if macd_signal:
        fig.add_trace(go.Scatter(x=df.index, y=df[macd_signal], name='Signal', line=dict(color='red')), row=3, col=1)

    # Add Signal markers
    for s in signals:
        # For simplicity, mark it on the last candle
        last_date = df.index[-1]
        last_price = df['High'].iloc[-1]
        fig.add_annotation(x=last_date, y=last_price,
                           text=f"SIGNAL: {s['type']}",
                           showarrow=True,
                           arrowhead=1,
                           ax=0, ay=-40,
                           bgcolor="yellow",
                           font=dict(color="black", size=10),
                           row=1, col=1)

    fig.update_layout(title=f'Swing Trading Analysis: {ticker}',
                      xaxis_rangeslider_visible=False,
                      height=900,
                      template='plotly_white')
    
    fig.write_html(output_path)
    return output_path
