import streamlit as st
import pandas as pd
import main
import reporting
# import your existing logic (keep these modules “pure”: no prints, no input)
# from scanner import run_scan   # example
# from data_retrieval import fetch_prices
# from reporting import build_signals_df

st.set_page_config(page_title="Swing Scanner", layout="wide")

st.title("Swing Trading Scanner")

# ---- Sidebar controls (replace CLI args) ----
st.sidebar.header("Settings")

index_choice = st.sidebar.selectbox("Universe", ["S&P 500", "Nasdaq 100", "Custom"])
custom_tickers = st.sidebar.text_area("Custom tickers (comma-separated)", "AAPL,MSFT")

rsi_low = st.sidebar.slider("RSI oversold threshold", 10, 50, 30)
rsi_high = st.sidebar.slider("RSI overbought threshold", 50, 90, 70)

run = st.sidebar.button("Run scan")

# ---- Helper: turn your list[dict] into a dataframe ----
def signals_to_df(all_signals: list[dict]) -> pd.DataFrame:
    if not all_signals:
        return pd.DataFrame(columns=["Ticker", "Price", "RSI", "Signal Type", "Details", "Conviction"])

    rows = []
    for s in all_signals:
        rows.append({
            "Ticker": s.get("ticker"),
            "Price": float(s.get("price", 0) or 0),
            "RSI": float(s.get("rsi", 0) or 0),
            "Signal Type": s.get("type"),
            "Details": s.get("detail"),
            "Conviction": s.get("conviction", 0),
        })

    df = pd.DataFrame(rows).sort_values("Conviction", ascending=False)
    return df
generate_charts = st.sidebar.checkbox("Show charts", value=False)
# ---- Run ----
if run:
    with st.spinner("Running scan..."):
        universe_key = {"S&P 500": "sp500", "Nasdaq 100": "nasdaq100", "Combined": "combined", "Custom": "custom"}[index_choice]

        tickers = None
        if index_choice == "Custom":
            tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]

        all_signals, charts = main.run_scan(
            universe=universe_key,
            tickers=tickers,
            rsi_oversold=rsi_low,
            rsi_overbought=rsi_high,
            generate_charts=generate_charts,
        )

    df = reporting.signals_to_df(all_signals)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if generate_charts and charts:
        # show chart for selected ticker
        selected = st.selectbox("Chart ticker", list(charts.keys()))
        st.plotly_chart(charts[selected], use_container_width=True)
