import yfinance as yf
import pandas as pd
import time

def fetch_stock_data(ticker, period="5y", max_retries=3):
    for attempt in range(max_retries):
        try:
            df = yf.download(ticker, period=period, progress=False, timeout=10)
            
            if df.empty:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                raise ValueError(f"No data found for {ticker}")
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            if len(df) < 30:
                raise ValueError(f"{ticker}: Only {len(df)} days of data (need 30+)")
            
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise ValueError(f"Failed to fetch {ticker}: {str(e)}")
