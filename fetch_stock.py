import yfinance as yf
import pandas as pd
import time
import requests

def fetch_stock_data(ticker, period="5y", max_retries=3):
    # Create session with headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker, session=session)
            df = stock.history(period=period)
            
            if df.empty:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise ValueError(f"No data found for {ticker}")
            
            if len(df) < 30:
                raise ValueError(f"{ticker}: Only {len(df)} days of data (need 30+)")
            
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            raise ValueError(f"Failed to fetch {ticker}: {str(e)}")
