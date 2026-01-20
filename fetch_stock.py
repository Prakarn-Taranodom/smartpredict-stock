import pandas as pd
import requests
import os
import time
from datetime import datetime, timedelta

def fetch_stock_data(ticker, period="5y"):
    """
    Fetch stock data using Alpha Vantage API.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'MSFT')
        period: Time period (not used with Alpha Vantage, always returns max available)
    
    Returns:
        pandas.DataFrame: Stock data with Date index and OHLCV columns
    """
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY not found. "
            "Set it in Render Dashboard → Environment → Add Environment Variable"
        )
    
    # Alpha Vantage API endpoint
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "full",  # Get full historical data
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if "Error Message" in data:
            raise ValueError(f"Invalid ticker symbol: {ticker}")
        
        if "Note" in data:
            raise ValueError(f"API rate limit exceeded. Please wait and try again.")
        
        if "Time Series (Daily)" not in data:
            raise ValueError(f"No data found for {ticker}. Response: {data}")
        
        # Parse time series data
        time_series = data["Time Series (Daily)"]
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns to match expected format
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Filter to requested period (approximate)
        if period == "5y":
            cutoff_date = datetime.now() - timedelta(days=5*365)
        elif period == "1y":
            cutoff_date = datetime.now() - timedelta(days=365)
        elif period == "6mo":
            cutoff_date = datetime.now() - timedelta(days=180)
        else:
            cutoff_date = datetime.now() - timedelta(days=5*365)
        
        df = df[df.index >= cutoff_date]
        
        if len(df) < 30:
            raise ValueError(f"{ticker}: Only {len(df)} days of data (need 30+)")
        
        return df
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error fetching {ticker}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to fetch {ticker}: {str(e)}")
