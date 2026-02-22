import data_retrieval
import analysis_engine
import scanner
import reporting
import visualization
import os
import pandas as pd
from datetime import datetime

def run_scanner():
    print("Starting Swing Trading Scanner (Daily & Weekly)...")
    
    # 1. Get tickers
    tickers = data_retrieval.get_combined_tickers()
    
    # 2. Download Daily Data
    # 2 years is enough for EMA 200 daily and EMA 50 weekly
    daily_data = data_retrieval.download_data(tickers, interval='1d', period='2y')
    
    all_signals = []
    
    # Directory for charts
    if not os.path.exists('charts'):
        os.makedirs('charts')

    print(f"Analyzing {len(tickers)} tickers...")
    
    for ticker in tickers:
        try:
            # Extract ticker data
            if ticker not in daily_data.columns.get_level_values(0):
                continue
            
            df_daily = daily_data[ticker].copy()
            df_daily.dropna(subset=['Close'], inplace=True)
            
            if len(df_daily) < 200:
                continue
                
            # 3. Calculate Daily Indicators
            df_daily = analysis_engine.calculate_indicators(df_daily)
            
            # 4. Calculate Weekly Indicators
            df_weekly = analysis_engine.get_weekly_data(df_daily)
            
            # 5. Scan for Signals (Daily)
            signals = scanner.scan_for_signals(df_daily, ticker)
            
            if signals:
                # Filter/Enhance with Weekly Trend
                weekly_uptrend = False
                if not df_weekly.empty:
                    # Weekly Uptrend: Price > EMA 20 Weekly
                    latest_weekly = df_weekly.iloc[-1]
                    if 'EMA_20' in latest_weekly and latest_weekly['Close'] > latest_weekly['EMA_20']:
                        weekly_uptrend = True
                
                # Get the best signal
                best_signal = scanner.evaluate_high_conviction(signals)
                
                # Mark if weekly trend aligns
                if weekly_uptrend:
                    best_signal['detail'] += " | WEEKLY BULLISH"
                    best_signal['conviction'] += 2
                else:
                    best_signal['detail'] += " | WEEKLY BEARISH/NEUTRAL"
                
                # Add extra info for report
                best_signal['price'] = df_daily['Close'].iloc[-1]
                best_signal['rsi'] = df_daily['RSI'].iloc[-1]
                
                all_signals.append(best_signal)
                
                # 6. Generate Chart for signals
                chart_path = f"charts/{ticker}_signal.html"
                visualization.generate_interactive_chart(df_daily, ticker, signals, chart_path)
                
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")

    # 7. Print Report
    reporting.print_scan_report(all_signals)
    print(f"Total signals found: {len(all_signals)}")
    print(f"Interactive charts saved in 'charts/' directory.")

if __name__ == "__main__":
    run_scanner()
