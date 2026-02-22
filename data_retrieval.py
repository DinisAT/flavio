import pandas as pd
import requests
import yfinance as yf
import os
from io import StringIO

def get_sp500_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        table = pd.read_html(StringIO(response.text))[0]
        return table['Symbol'].tolist()
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        return []

def get_nasdaq100_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        tables = pd.read_html(StringIO(response.text))
        for table in tables:
            if 'Ticker' in table.columns:
                return table['Ticker'].tolist()
            if 'Symbol' in table.columns:
                return table['Symbol'].tolist()
        return []
    except Exception as e:
        print(f"Error fetching Nasdaq 100 tickers: {e}")
        return []

def download_data(tickers, interval='1d', period='2y'):
    """
    Downloads historical data for a list of tickers.
    """
    print(f"Downloading {interval} data for {len(tickers)} tickers...")
    # yfinance download might fail for some tickers, we should handle it if necessary
    # or just let it return what it can.
    data = yf.download(tickers, period=period, interval=interval, group_by='ticker', threads=True)
    return data

def get_combined_tickers():
    sp500 = get_sp500_tickers()
    nasdaq100 = get_nasdaq100_tickers()
    combined = list(set(sp500 + nasdaq100))
    # Replace dots with hyphens for yfinance (e.g., BRK.B -> BRK-B)
    combined = [t.replace('.', '-') for t in combined]
    return sorted(combined)

if __name__ == "__main__":
    tickers = get_combined_tickers()
    print(f"Total unique tickers: {len(tickers)}")
    if tickers:
        print(f"Sample tickers: {tickers[:10]}")
    else:
        print("No tickers found!")
