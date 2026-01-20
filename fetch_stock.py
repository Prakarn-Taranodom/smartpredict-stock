import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker, period="5y"):
    try:
        df = yf.download(ticker, period=period, progress=False)
        
        if df.empty:
            raise ValueError(f"No data found for {ticker}")
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        if len(df) < 30:
            raise ValueError(f"{ticker}: Only {len(df)} days of data (need 30+)")
        
        return df
    except Exception as e:
        raise ValueError(f"Failed to fetch {ticker}: {str(e)}")

