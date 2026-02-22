# visualization.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def build_interactive_chart(df, ticker, signals):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        subplot_titles=(f"{ticker} Price & EMAs", "RSI", "MACD"),
                        row_width=[0.2, 0.2, 0.6])

    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"
    ), row=1, col=1)

    for ema in ["EMA_9", "EMA_20", "EMA_50", "EMA_200"]:
        if ema in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[ema], name=ema), row=1, col=1)

    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", row=2, col=1)

    macd_cols = [c for c in df.columns if "MACD" in c]
    macd_line = next((c for c in macd_cols if c.startswith("MACD_")), None)
    macd_hist = next((c for c in macd_cols if c.startswith("MACDh_")), None)
    macd_signal = next((c for c in macd_cols if c.startswith("MACDs_")), None)

    if macd_hist:
        fig.add_trace(go.Bar(x=df.index, y=df[macd_hist], name="MACD Histogram"), row=3, col=1)
    if macd_line:
        fig.add_trace(go.Scatter(x=df.index, y=df[macd_line], name="MACD"), row=3, col=1)
    if macd_signal:
        fig.add_trace(go.Scatter(x=df.index, y=df[macd_signal], name="Signal"), row=3, col=1)

    # marker on last candle
    last_date = df.index[-1]
    last_price = df["High"].iloc[-1]
    for s in signals:
        fig.add_annotation(x=last_date, y=last_price, text=f"SIGNAL: {s['type']}", showarrow=True, ay=-40, row=1, col=1)

    fig.update_layout(title=f"Swing Trading Analysis: {ticker}", xaxis_rangeslider_visible=False, height=900)
    return fig


def generate_interactive_chart(df, ticker, signals, output_path):
    fig = build_interactive_chart(df, ticker, signals)
    fig.write_html(output_path)
    return output_path
