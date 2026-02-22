# main.py
import os
import data_retrieval
import analysis_engine
import scanner
import visualization

def run_scan(
    universe: str = "combined",
    tickers: list[str] | None = None,
    interval: str = "1d",
    period: str = "2y",
    rsi_oversold: int = 30,
    rsi_overbought: int = 70,
    generate_charts: bool = False,
):
    # 1) tickers
    if tickers is None:
        if universe == "sp500":
            tickers = data_retrieval.get_sp500_tickers()
        elif universe == "nasdaq100":
            tickers = data_retrieval.get_nasdaq100_tickers()
        else:
            tickers = data_retrieval.get_combined_tickers()

    if not tickers:
        return [], {}

    # 2) download
    daily_data = data_retrieval.download_data(tickers, interval=interval, period=period)

    all_signals = []
    charts = {}

    # 3) analyze
    for ticker in tickers:
        try:
            if ticker not in daily_data.columns.get_level_values(0):
                continue

            df_daily = daily_data[ticker].copy()
            df_daily.dropna(subset=["Close"], inplace=True)

            if len(df_daily) < 200:
                continue

            df_daily = analysis_engine.calculate_indicators(df_daily)
            df_weekly = analysis_engine.get_weekly_data(df_daily)

            # IMPORTANT: pass thresholds (we’ll update scanner.py below)
            signals = scanner.scan_for_signals(
                df_daily,
                ticker,
                rsi_oversold=rsi_oversold,
                rsi_overbought=rsi_overbought,
            )

            if not signals:
                continue

            weekly_uptrend = False
            if not df_weekly.empty:
                latest_weekly = df_weekly.iloc[-1]
                if "EMA_20" in latest_weekly and latest_weekly["Close"] > latest_weekly["EMA_20"]:
                    weekly_uptrend = True

            best_signal = scanner.evaluate_high_conviction(signals)
            if best_signal is None:
                continue

            if weekly_uptrend:
                best_signal["detail"] += " | WEEKLY BULLISH"
                best_signal["conviction"] += 2
            else:
                best_signal["detail"] += " | WEEKLY BEARISH/NEUTRAL"

            best_signal["price"] = float(df_daily["Close"].iloc[-1])
            best_signal["rsi"] = float(df_daily["RSI"].iloc[-1])

            all_signals.append(best_signal)

            if generate_charts:
                fig = visualization.build_interactive_chart(df_daily, ticker, signals)
                charts[ticker] = fig

        except Exception:
            # In Streamlit we’ll show exceptions in app.py if you want
            continue

    return all_signals, charts


if __name__ == "__main__":
    # keep your CLI behavior if you still want it
    import reporting

    signals, charts = run_scan(universe="combined", generate_charts=False)
    reporting.print_scan_report(signals)
    print(f"Total signals found: {len(signals)}")
