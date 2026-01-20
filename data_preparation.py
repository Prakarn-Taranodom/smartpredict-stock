# data_preparation.py
import pandas as pd
import numpy as np
from fetch_stock import fetch_stock_data
from volatility_pipeline import compute_conditional_volatility
from pmdarima import auto_arima
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from arch import arch_model
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

def get_stock_industry(ticker):
    """
    Get industry information for a stock ticker using yfinance.

    Args:
        ticker: Stock ticker symbol

    Returns:
        str: Industry name or 'Unknown' if not found
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('industry', 'Unknown')
    except Exception as e:
        print(f"Could not get industry for {ticker}: {e}")
        return 'Unknown'

def prepare_stock_data_for_clustering(stocks, window_days=60, include_industry=False, add_suffix=None):
    cv_series_list = []
    total = len(stocks)
    failed_stocks = []
    
    for idx, stock in enumerate(stocks, 1):
        try:
            ticker = f"{stock}{add_suffix}" if add_suffix else stock
            print(f"[{idx}/{total}] Processing {ticker}...")

            df = fetch_stock_data(ticker)
            if df is None or len(df) < window_days:
                print(f"Skipping {ticker}: insufficient data")
                failed_stocks.append(ticker)
                continue

            df_cv = compute_conditional_volatility(df)
            cv_series = df_cv['cv'].tail(window_days).values
            cv_normalized = (cv_series - cv_series.mean()) / cv_series.std()

            row_data = {'stock_id': stock}
            for i, cv_value in enumerate(cv_normalized):
                row_data[f'cv_t_{i+1}'] = cv_value

            if include_industry:
                row_data['industry'] = get_stock_industry(ticker)

            cv_series_list.append(row_data)

        except Exception as e:
            print(f"Skipping {stock}: {str(e)}")
            failed_stocks.append(stock)
            continue

    if not cv_series_list:
        raise ValueError(f"No valid stocks found. Failed: {', '.join(failed_stocks[:10])}")
    
    print(f"\nSuccessfully processed {len(cv_series_list)}/{total} stocks")
    if failed_stocks:
        print(f"Failed stocks: {', '.join(failed_stocks[:10])}{'...' if len(failed_stocks) > 10 else ''}")

    cv_df = pd.DataFrame(cv_series_list)
    cv_df = cv_df.fillna(0)

    return cv_df

def prepare_single_stock_data(ticker, window_days=60):
    """
    Prepare data for a single stock ticker.

    Args:
        ticker: Stock ticker symbol
        window_days: Number of days to use for CV time series

    Returns:
        pd.DataFrame: CV time series for the stock or None if failed
    """
    try:
        # Fetch data
        df = fetch_stock_data(ticker)
        if df is None or len(df) < window_days:
            return None

        # Compute conditional volatility
        df_cv = compute_conditional_volatility(df)

        # Extract last window_days of CV
        cv_series = df_cv['cv'].tail(window_days).values

        # Normalize using z-score
        cv_normalized = (cv_series - cv_series.mean()) / cv_series.std()

        # Create DataFrame
        row_data = {}
        for i, cv_value in enumerate(cv_normalized):
            row_data[f'cv_t_{i+1}'] = cv_value

        # Create single-row DataFrame
        cv_df = pd.DataFrame([row_data])

        # Fill NaN values
        cv_df = cv_df.fillna(0)

        return cv_df

    except Exception as e:
        print(f"Error processing single stock {ticker}: {e}")
        return None

def get_market_stocks(market):
    """
    Get stock list for a specific market.
    For NASDAQ-100, SET-50, SET-100: get all available stocks

    Args:
        market: Market identifier ('nasdaq100', 'set50', 'set100', 'sp500')

    Returns:
        list: Stock tickers for the market
    """
    if market == 'nasdaq100':
        # Try to get NASDAQ-100 stocks dynamically
        try:
            import yfinance as yf
            # Get NASDAQ-100 index components
            nasdaq100 = yf.Ticker("^NDX")
            # This might not work directly, so fallback to expanded list
            return get_nasdaq100_stocks()
        except:
            return get_nasdaq100_stocks()

    elif market == 'set50':
        # SET-50 stocks (Thailand)
        return get_set50_stocks()

    elif market == 'set100':
        # SET-100 stocks (Thailand)
        return get_set100_stocks()

    elif market == 'sp500':
        # S&P 500 stocks
        return get_sp500_stocks()

    else:
        return []

def get_nasdaq100_stocks():
    """Get top NASDAQ-100 stocks (limited for performance)"""
    return [
        'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA', 'NFLX',
        'ADBE', 'CRM', 'ORCL', 'CSCO', 'INTC', 'AMD', 'QCOM', 'AVGO',
        'COST', 'TMUS', 'BKNG', 'ISRG', 'MU', 'ASML', 'VRTX', 'REGN'
    ]

def get_set50_stocks():
    """Get top SET-50 stocks (limited for performance)"""
    return [
        'AOT', 'BBL', 'BDMS', 'BEM', 'BH', 'BTS', 'CPALL', 'CPF',
        'CPN', 'EGCO', 'GPSC', 'INTUCH', 'KBANK', 'KTB', 'PTT',
        'PTTEP', 'PTTGC', 'RATCH', 'SCC', 'SCGP', 'TOP', 'TRUE', 'TU'
    ]

def get_set100_stocks():
    """Get SET-100 stocks (Thailand) - includes SET-50 plus additional stocks"""
    set50 = get_set50_stocks()
    additional = [
        'ACE', 'ADVANC', 'AEONTS', 'AMATA', 'AP', 'ASIAN', 'ASK', 'ASP',
        'BAM', 'BANPU', 'BAY', 'BCH', 'BCPG', 'BEAUTY', 'BEC', 'BKI',
        'BLAND', 'BPP', 'BROCK', 'BTG', 'CENTEL', 'CHG', 'CK', 'CKP',
        'COM7', 'CPAXT', 'CPC', 'CPNCG', 'DELTA', 'DEMCO', 'DIF', 'E1VFVN3001',
        'EASTW', 'EKH', 'EPG', 'FORTH', 'FPT', 'FSMART', 'FSS', 'GC',
        'GFPT', 'GLOBAL', 'GPI', 'GRAND', 'HANA', 'HFT', 'HREIT', 'ICHI',
        'III', 'ILINK', 'INET', 'INOX', 'INSURE', 'ITD', 'ITEL', 'J',
        'JAS', 'JMART', 'JMT', 'JWD', 'KAMART', 'KARM', 'KBS', 'KEX',
        'KGI', 'KIAT', 'KISS', 'KSL', 'KTIS', 'KWC', 'L&E', 'LALIN',
        'LANNA', 'LEE', 'LOXLEY', 'LPH', 'LPN', 'M', 'MACO', 'MAJOR',
        'MASTER', 'MATI', 'MAX', 'MBAX', 'MC', 'MCS', 'MEGA', 'METCO',
        'MGT', 'MICRO', 'MILL', 'MJLF', 'MK', 'ML', 'MNIT', 'MNIT2',
        'MODERN', 'MONO', 'MTI', 'NER', 'NETBAY', 'NEW', 'NEX', 'NOBLE',
        'NUSA', 'NVD', 'NYT', 'OCC', 'OISHI', 'ORI', 'PACO', 'PAP',
        'PATO', 'PF', 'PG', 'PHOL', 'PIMO', 'PJW', 'PK', 'PL', 'PLANB',
        'PLE', 'PM', 'PMTA', 'POLAR', 'PREB', 'PRG', 'PRIN', 'PRM',
        'PSH', 'PSL', 'PT', 'PTG', 'PTL', 'PTT', 'PTTEP', 'PTTGC',
        'PYLON', 'QC', 'QH', 'QTC', 'RABBIT', 'RBF', 'RCL', 'RICHY',
        'ROBINS', 'ROJNA', 'RPX', 'RS', 'S', 'S11', 'SABINA', 'SALEE',
        'SAM', 'SAMART', 'SAMCO', 'SAMTEL', 'SAPPE', 'SAT', 'SAUCE',
        'SAWAD', 'SC', 'SCAP', 'SCB', 'SCC', 'SCCC', 'SCG', 'SCGP',
        'SCI', 'SCM', 'SCORE', 'SCP', 'SDC', 'SE-ED', 'SEAFCO', 'SEAOIL',
        'SELIC', 'SENA', 'SF', 'SFC', 'SFLEX', 'SFP', 'SFT', 'SGC',
        'SGP', 'SHANG', 'SHR', 'SI', 'SINGER', 'SIRI', 'SIS', 'SISB',
        'SITHAI', 'SJWD', 'SK', 'SKN', 'SKR', 'SLM', 'SLP', 'SMIT',
        'SMK', 'SMM', 'SMPC', 'SMT', 'SNC', 'SNP', 'SOLAR', 'SORKON',
        'SPA', 'SPALI', 'SPC', 'SPCG', 'SPG', 'SPI', 'SPRC', 'SPRIME',
        'SQ', 'SR', 'SRICHA', 'SRIPANWA', 'SSC', 'SSF', 'SSP', 'SSTEEL',
        'SST', 'STA', 'STANLY', 'STARK', 'STEC', 'STGT', 'STHAI', 'STI',
        'STPI', 'SUC', 'SUPER', 'SUSCO', 'SUTHA', 'SVH', 'SVI', 'SVOA',
        'SWC', 'SYNEX', 'SYNTEC', 'TAE', 'TAKUNI', 'TASCO', 'TBSP',
        'TC', 'TCAP', 'TCJ', 'TCMC', 'TCOAT', 'TEAM', 'TEAMG', 'TECH',
        'TEKA', 'TFG', 'TGE', 'TGH', 'TH', 'THANI', 'THCOM', 'THE',
        'THG', 'THIP', 'THL', 'THMUI', 'THRE', 'THREL', 'TIC', 'TICON',
        'TIF1', 'TIW', 'TJW', 'TK', 'TKC', 'TKN', 'TKS', 'TKT', 'TLHPF',
        'TLI', 'TLOGIS', 'TM', 'TMB', 'TMC', 'TMD', 'TMI', 'TMILL',
        'TMT', 'TMW', 'TNDT', 'TNITY', 'TNL', 'TNPC', 'TNP', 'TNR',
        'TOA', 'TOG', 'TOP', 'TOPP', 'TPA', 'TPAC', 'TPBI', 'TPCORP',
        'TPIPL', 'TPIPP', 'TPIPL', 'TPL', 'TPOLY', 'TPP', 'TPRIME',
        'TR', 'TRC', 'TRITN', 'TRU', 'TRUBB', 'TRUE', 'TSC', 'TSE',
        'TSI', 'TSR', 'TSTE', 'TSTH', 'TTA', 'TTCL', 'TTI', 'TTLPF',
        'TTT', 'TTW', 'TU', 'TUCC', 'TVD', 'TVI', 'TVO', 'TVT', 'TWP',
        'TWPC', 'TWZ', 'TYCN', 'U', 'UAC', 'UBIS', 'UEC', 'UKEM', 'UNIQ',
        'UOBKH', 'UP', 'UPA', 'UPF', 'UPOIC', 'URBNPF', 'UT', 'UTP',
        'UV', 'UVAN', 'UWC', 'VCOM', 'VGI', 'VIH', 'VNG', 'VNT', 'VPO',
        'W', 'WACOAL', 'WAVE', 'WFX', 'WGE', 'WHA', 'WHAUP', 'WICE',
        'WORK', 'WP', 'WPH', 'WYNCO', 'XPG', 'YCI', 'YONG', 'YUASA',
        'ZAA', 'ZMICO'
    ]
    return list(set(set50 + additional))

def get_sp500_stocks():
    """Get S&P 500 stocks"""
    return [
        'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA', 'JPM',
        'JNJ', 'V', 'WMT', 'PG', 'UNH', 'HD', 'MA', 'BAC', 'DIS', 'PFE',
        'KO', 'XOM', 'CVX', 'ABBV', 'COST', 'AVGO', 'VZ', 'ADBE', 'CRM',
        'NFLX', 'CMCSA', 'PEP', 'ABT', 'ACN', 'TXN', 'DHR', 'LLY', 'PM',
        'ORCL', 'IBM', 'NEE', 'UNP', 'LIN', 'UPS', 'AMGN', 'MDT', 'HON',
        'SPGI', 'BLK', 'INTC', 'AMD', 'QCOM', 'NOW', 'INTU', 'AMAT', 'CAT'
    ]

def get_market_tickers(market):
    """
    Alias for get_market_stocks for backward compatibility.
    """
    return get_market_stocks(market)

def prepare_market_data(market, window_days=60, include_industry=False):
    """
    Prepare market data for clustering.

    Args:
        market: Market identifier
        window_days: Window size for CV series
        include_industry: Whether to include industry information

    Returns:
        pd.DataFrame: Prepared data for clustering
    """
    stocks = get_market_stocks(market)

    # Add suffix for Thailand markets
    suffix = '.BK' if market in ['set50', 'set100'] else None

    return prepare_stock_data_for_clustering(stocks, window_days, include_industry, add_suffix=suffix)