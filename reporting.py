from tabulate import tabulate

def print_scan_report(all_signals):
    """
    Prints a formatted table of all signals found.
    all_signals is a list of dictionaries.
    """
    if not all_signals:
        print("\nNo trading signals found for the selected tickers.")
        return

    # Prepare data for tabulate
    table_data = []
    for s in all_signals:
        table_data.append([
            s.get('ticker'),
            f"{s.get('price', 0):.2f}",
            f"{s.get('rsi', 0):.2f}",
            s.get('type'),
            s.get('detail'),
            s.get('conviction')
        ])

    headers = ["Ticker", "Price", "RSI", "Signal Type", "Details", "Conviction"]
    
    # Sort by conviction descending
    table_data.sort(key=lambda x: x[5], reverse=True)

    print("\n" + "="*80)
    print("SWING TRADING SCAN REPORT")
    print("="*80)
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print("="*80 + "\n")
