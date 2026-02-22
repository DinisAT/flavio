# reporting.py
import pandas as pd
from tabulate import tabulate

def signals_to_df(all_signals):
    """
    Convert list[dict] signals into a sorted pandas DataFrame.
    """
    if not all_signals:
        return pd.DataFrame(columns=["Ticker", "Price", "RSI", "Signal Type", "Details", "Conviction"])

    rows = []
    for s in all_signals:
        rows.append({
            "Ticker": s.get("ticker"),
            "Price": s.get("price"),
            "RSI": s.get("rsi"),
            "Signal Type": s.get("type"),
            "Details": s.get("detail"),
            "Conviction": s.get("conviction"),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Conviction", ascending=False)
    return df


def print_scan_report(all_signals):
    """
    Terminal-friendly report (optional, for CLI usage).
    """
    if not all_signals:
        print("\nNo trading signals found for the selected tickers.")
        return

    df = signals_to_df(all_signals)

    print("\n" + "=" * 80)
    print("SWING TRADING SCAN REPORT")
    print("=" * 80)
    print(tabulate(df.values.tolist(), headers=df.columns.tolist(), tablefmt="grid"))
    print("=" * 80 + "\n")
