# -*- coding: utf-8 -*-
"""
Comprehensive Evaluation with Both Classification and Regression Metrics
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, mean_absolute_error, mean_squared_error
)
from sklearn.ensemble import RandomForestClassifier
from fetch_coinlore import fetch_crypto_data
from volatility_pipeline import compute_conditional_volatility
from feature_engineering import build_features
import warnings
warnings.filterwarnings('ignore')

def calculate_price_prediction_metrics(df_with_features, y_pred_proba, test_size):
    """
    Calculate regression metrics for price movement predictions
    Based on probability confidence and actual direction
    """
    last_price = df_with_features["Close"].iloc[-1]
    
    # Make sure log_return exists
    if "log_return" not in df_with_features.columns:
        close_prices = df_with_features["Close"]
        log_return = np.log(close_prices / close_prices.shift(1))
    else:
        log_return = df_with_features["log_return"]
    
    returns = log_return.dropna()
    avg_daily_return = returns.mean()
    daily_volatility = returns.std()
    
    predicted_prices = []
    current_price = last_price
    
    for prob in y_pred_proba[:test_size]:
        # Price movement based on prediction confidence
        expected_return = (
            avg_daily_return * prob if prob > 0.5 
            else -avg_daily_return * (1 - prob)
        )
        expected_return += np.random.normal(0, daily_volatility * 0.5)
        current_price *= (1 + expected_return)
        predicted_prices.append(current_price)
    
    # Actual prices (forward-looking)
    actual_prices = df_with_features["Close"].iloc[-test_size:].values
    
    # Calculate errors
    predicted_prices = np.array(predicted_prices)
    mae = mean_absolute_error(actual_prices, predicted_prices)
    rmse = np.sqrt(mean_squared_error(actual_prices, predicted_prices))
    mape = np.mean(np.abs((actual_prices - predicted_prices) / actual_prices)) * 100
    
    return mae, rmse, mape

print("\n" + "=" * 100)
print(" " * 20 + "COMPREHENSIVE EVALUATION: CLASSIFICATION + REGRESSION METRICS")
print("=" * 100)

# =====================================================================
# Approach 1: Raw Data
# =====================================================================
print("\n[PROCESSING] Approach 1: Raw Data (without CV)...\n")

def build_features_raw(df):
    df = df.copy()
    df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))
    df['target'] = (df['log_return'].shift(-1) > 0).astype(int)
    df['return_lag1'] = df['log_return'].shift(1)
    df['return_lag2'] = df['log_return'].shift(2)
    
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['rsi_14'] = 100 - (100 / (1 + rs))
    df['rsi_slope'] = df['rsi_14'].diff()
    
    df = df.dropna()
    feature_cols = ['return_lag1', 'return_lag2', 'rsi_14', 'rsi_slope']
    X = df[feature_cols]
    y = df['target']
    return X, y

try:
    df_raw = fetch_crypto_data('BTC')
    X_raw, y_raw = build_features_raw(df_raw)
    
    # Keep df with log_return for regression metrics
    df_raw_with_features = X_raw.copy()
    df_raw_with_features['Close'] = df_raw['Close']
    
    X_train_raw, X_test_raw, y_train_raw, y_test_raw = train_test_split(
        X_raw, y_raw, test_size=0.2, random_state=42
    )
    
    model_raw = RandomForestClassifier(
        n_estimators=200, max_depth=5, random_state=42, class_weight="balanced"
    )
    model_raw.fit(X_train_raw, y_train_raw)
    
    y_pred_raw = model_raw.predict(X_test_raw)
    y_pred_proba_raw = model_raw.predict_proba(X_test_raw)[:, 1]
    
    # Classification metrics
    acc_raw = accuracy_score(y_test_raw, y_pred_raw)
    prec_raw = precision_score(y_test_raw, y_pred_raw, zero_division=0)
    rec_raw = recall_score(y_test_raw, y_pred_raw, zero_division=0)
    f1_raw = f1_score(y_test_raw, y_pred_raw, zero_division=0)
    auc_raw = roc_auc_score(y_test_raw, y_pred_proba_raw)
    
    # Regression metrics (price prediction)
    mae_raw, rmse_raw, mape_raw = calculate_price_prediction_metrics(
        df_raw, y_pred_proba_raw, min(10, len(y_test_raw))
    )
    
    results_raw = {
        'Accuracy': acc_raw, 'Precision': prec_raw, 'Recall': rec_raw,
        'F1': f1_raw, 'ROC-AUC': auc_raw, 'MAE': mae_raw, 'RMSE': rmse_raw, 'MAPE': mape_raw
    }
    
    print("✅ Raw Data Model: COMPLETED")
except Exception as e:
    print(f"❌ Raw Data Model: FAILED - {str(e)}")
    import traceback
    traceback.print_exc()
    results_raw = None

# =====================================================================
# Approach 2: Processed Data (with CV)
# =====================================================================
print("\n[PROCESSING] Approach 2: Processed Data (with CV)...\n")

try:
    df_proc = fetch_crypto_data('BTC')
    df_cv = compute_conditional_volatility(df_proc)
    X_proc, y_proc = build_features(df_cv)
    X_train_proc, X_test_proc, y_train_proc, y_test_proc = train_test_split(
        X_proc, y_proc, test_size=0.2, random_state=42
    )
    
    model_proc = RandomForestClassifier(
        n_estimators=200, max_depth=5, random_state=42, class_weight="balanced"
    )
    model_proc.fit(X_train_proc, y_train_proc)
    
    y_pred_proc = model_proc.predict(X_test_proc)
    y_pred_proba_proc = model_proc.predict_proba(X_test_proc)[:, 1]
    
    # Classification metrics
    acc_proc = accuracy_score(y_test_proc, y_pred_proc)
    prec_proc = precision_score(y_test_proc, y_pred_proc, zero_division=0)
    rec_proc = recall_score(y_test_proc, y_pred_proc, zero_division=0)
    f1_proc = f1_score(y_test_proc, y_pred_proc, zero_division=0)
    auc_proc = roc_auc_score(y_test_proc, y_pred_proba_proc)
    
    # Regression metrics (price prediction)
    mae_proc, rmse_proc, mape_proc = calculate_price_prediction_metrics(
        df_cv, y_pred_proba_proc, min(10, len(y_test_proc))
    )
    
    results_proc = {
        'Accuracy': acc_proc, 'Precision': prec_proc, 'Recall': rec_proc,
        'F1': f1_proc, 'ROC-AUC': auc_proc, 'MAE': mae_proc, 'RMSE': rmse_proc, 'MAPE': mape_proc
    }
    
    print("✅ Processed Data Model: COMPLETED")
except Exception as e:
    print(f"❌ Processed Data Model: FAILED - {str(e)}")
    import traceback
    traceback.print_exc()
    results_proc = None

# =====================================================================
# Display Results
# =====================================================================
if results_raw and results_proc:
    print("\n" + "=" * 100)
    print("TABLE 1: CLASSIFICATION METRICS (Direction Prediction: UP/DOWN)")
    print("=" * 100)
    
    class_data = [
        {
            'Metric': 'Accuracy',
            'Raw Data': f"{results_raw['Accuracy']:.4f}",
            'With CV': f"{results_proc['Accuracy']:.4f}",
            'Winner': '🏆 Raw Data' if results_raw['Accuracy'] > results_proc['Accuracy'] else '🏆 With CV'
        },
        {
            'Metric': 'Precision (% of UP predictions correct)',
            'Raw Data': f"{results_raw['Precision']:.4f}",
            'With CV': f"{results_proc['Precision']:.4f}",
            'Winner': '🏆 Raw Data' if results_raw['Precision'] > results_proc['Precision'] else '🏆 With CV'
        },
        {
            'Metric': 'Recall (% of actual UPs caught)',
            'Raw Data': f"{results_raw['Recall']:.4f}",
            'With CV': f"{results_proc['Recall']:.4f}",
            'Winner': '🏆 Raw Data' if results_raw['Recall'] > results_proc['Recall'] else '🏆 With CV'
        },
        {
            'Metric': 'F1-Score (Balance of Precision & Recall)',
            'Raw Data': f"{results_raw['F1']:.4f}",
            'With CV': f"{results_proc['F1']:.4f}",
            'Winner': '🏆 Raw Data' if results_raw['F1'] > results_proc['F1'] else '🏆 With CV'
        },
        {
            'Metric': 'ROC-AUC (Overall Classification Quality)',
            'Raw Data': f"{results_raw['ROC-AUC']:.4f}",
            'With CV': f"{results_proc['ROC-AUC']:.4f}",
            'Winner': '🏆 Raw Data' if results_raw['ROC-AUC'] > results_proc['ROC-AUC'] else '🏆 With CV'
        },
    ]
    
    class_df = pd.DataFrame(class_data)
    print("\n" + class_df.to_string(index=False))
    
    print("\n" + "=" * 100)
    print("TABLE 2: REGRESSION METRICS (Price Prediction Accuracy)")
    print("=" * 100)
    
    reg_data = [
        {
            'Metric': 'MAE (Mean Absolute Error)',
            'Raw Data': f"${results_raw['MAE']:.2f}",
            'With CV': f"${results_proc['MAE']:.2f}",
            'Better': '🏆 Raw Data' if results_raw['MAE'] < results_proc['MAE'] else '🏆 With CV',
            'Definition': 'Avg price prediction error (USD)'
        },
        {
            'Metric': 'RMSE (Root Mean Squared Error)',
            'Raw Data': f"${results_raw['RMSE']:.2f}",
            'With CV': f"${results_proc['RMSE']:.2f}",
            'Better': '🏆 Raw Data' if results_raw['RMSE'] < results_proc['RMSE'] else '🏆 With CV',
            'Definition': 'Penalizes large errors (USD)'
        },
        {
            'Metric': 'MAPE (Mean Absolute % Error)',
            'Raw Data': f"{results_raw['MAPE']:.2f}%",
            'With CV': f"{results_proc['MAPE']:.2f}%",
            'Better': '🏆 Raw Data' if results_raw['MAPE'] < results_proc['MAPE'] else '🏆 With CV',
            'Definition': 'Percentage error (relative to actual price)'
        },
    ]
    
    reg_df = pd.DataFrame(reg_data)
    print("\n" + reg_df.to_string(index=False))
    
    # =====================================================================
    # Summary
    # =====================================================================
    print("\n" + "=" * 100)
    print("📊 SUMMARY & INTERPRETATION")
    print("=" * 100)
    
    print("\n🎯 CLASSIFICATION PERFORMANCE (Predicting UP vs DOWN):")
    if results_raw['Accuracy'] > results_proc['Accuracy']:
        print(f"  ✅ Raw Data is BETTER")
        print(f"     - Accuracy: {results_raw['Accuracy']:.4f} vs {results_proc['Accuracy']:.4f}")
        print(f"     - Improvement: +{(results_raw['Accuracy']-results_proc['Accuracy'])*100:.2f}%")
    else:
        print(f"  ✅ With CV is BETTER")
        print(f"     - Accuracy: {results_proc['Accuracy']:.4f} vs {results_raw['Accuracy']:.4f}")
        print(f"     - Improvement: +{(results_proc['Accuracy']-results_raw['Accuracy'])*100:.2f}%")
    
    print("\n💰 REGRESSION PERFORMANCE (Predicting Actual Price):")
    print(f"  • Raw Data MAPE: {results_raw['MAPE']:.2f}% error")
    print(f"  • With CV MAPE: {results_proc['MAPE']:.2f}% error")
    if results_raw['MAPE'] < results_proc['MAPE']:
        print(f"  ✅ Raw Data BETTER by {results_proc['MAPE']-results_raw['MAPE']:.2f}%")
    else:
        print(f"  ✅ With CV BETTER by {results_raw['MAPE']-results_proc['MAPE']:.2f}%")
    
    print("\n📋 KEY INSIGHTS:")
    print(f"  1. For predicting DIRECTION (Classification):")
    print(f"     - Raw Data: {results_raw['Accuracy']*100:.1f}% accurate")
    print(f"     - With CV: {results_proc['Accuracy']*100:.1f}% accurate")
    
    print(f"\n  2. For predicting ACTUAL PRICE (Regression):")
    print(f"     - Raw Data: Within ${results_raw['MAE']:.2f} error on average")
    print(f"     - With CV: Within ${results_proc['MAE']:.2f} error on average")
    
    print(f"\n  3. Overall Winner:")
    raw_score = (results_raw['Accuracy'] + (1 - results_raw['MAPE']/100)) / 2
    proc_score = (results_proc['Accuracy'] + (1 - results_proc['MAPE']/100)) / 2
    
    if raw_score > proc_score:
        print(f"     🏆 RAW DATA (Combined Score: {raw_score:.4f})")
    else:
        print(f"     🏆 WITH CV (Combined Score: {proc_score:.4f})")

print("\n" + "=" * 100 + "\n")
