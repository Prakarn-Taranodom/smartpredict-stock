# volatility_pipeline.py
import numpy as np
import pandas as pd
from pmdarima import auto_arima
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from arch import arch_model
from technical_indicators import add_technical_features

#check seasonality
def check_seasonality(series, period=7, alpha=0.05):
    result = seasonal_decompose(series, model="additive", period=period)
    seasonal = result.seasonal.dropna()
    p_value = adfuller(seasonal)[1]
    return p_value > alpha

#arima model
def fit_auto_arima(log_return, seasonal_period=7):
    has_seasonal = check_seasonality(log_return, seasonal_period)

    model = auto_arima(
        log_return,
        seasonal=has_seasonal,
        m=seasonal_period if has_seasonal else 1,
        start_p=0, start_q=0,
        max_p=5, max_q=5,
        d=None,
        trace=False,
        error_action="ignore",
        suppress_warnings=True,
        stepwise=True
    )

    residuals = pd.Series(model.resid(), index=log_return.index)
    return residuals


#cv
def compute_cv_from_residuals(residuals):
    am = arch_model(
        residuals * 100,
        vol="GARCH",
        p=1, o=1, q=1,
        dist="normal"
    )

    res = am.fit(disp="off")
    cv = res.conditional_volatility / 100

    return cv


#pipeline

def compute_conditional_volatility(price_df):
    df = price_df.copy()
    
    if len(df) < 30:
        raise ValueError(f"Not enough data: need at least 30 days, got {len(df)}")

    close_prices = df["Close"].squeeze()
    df["log_return"] = np.log(close_prices / close_prices.shift(1))
    df = df.dropna()
    
    if len(df) < 20:
        raise ValueError(f"Not enough data after dropna: {len(df)} observations")

    resid = fit_auto_arima(df["log_return"])
    cv = compute_cv_from_residuals(resid)

    df["cv"] = cv
    df = add_technical_features(df)

    return df


