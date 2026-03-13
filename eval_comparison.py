# -*- coding: utf-8 -*-
"""
Evaluation Comparison: Raw Data vs Processed Data (with CV)
Tests model performance with train/test split
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from fetch_coinlore import fetch_crypto_data
from volatility_pipeline import compute_conditional_volatility
from feature_engineering import build_features
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("EVALUATION: RAW DATA vs PROCESSED DATA (with Conditional Volatility)")
print("=" * 80)

# =====================================================================
# Approach 1: RAW DATA (without CV processing)
# =====================================================================
print("\n[APPROACH 1] Training with RAW DATA (without CV)...")

def build_features_raw(df):
    """Build features from raw data (no CV processing)"""
    df = df.copy()
    
    # Compute log returns
    df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # Create target
    df['target'] = (df['log_return'].shift(-1) > 0).astype(int)
    
    # Lag features (from returns only, no CV)
    df['return_lag1'] = df['log_return'].shift(1)
    df['return_lag2'] = df['log_return'].shift(2)
    
    # RSI from raw close prices
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['rsi_14'] = 100 - (100 / (1 + rs))
    df['rsi_slope'] = df['rsi_14'].diff()
    
    # Drop NaN
    df = df.dropna()
    
    feature_cols = ['return_lag1', 'return_lag2', 'rsi_14', 'rsi_slope']
    X = df[feature_cols]
    y = df['target']
    
    return X, y

try:
    # Fetch data
    df_raw = fetch_crypto_data('BTC')
    print(f"  ✓ Data fetched: {len(df_raw)} rows")
    
    # Build features
    X_raw, y_raw = build_features_raw(df_raw)
    print(f"  ✓ Features built: {X_raw.shape[0]} samples, {X_raw.shape[1]} features")
    print(f"    Features: {list(X_raw.columns)}")
    
    # Train/Test Split (80/20)
    X_train_raw, X_test_raw, y_train_raw, y_test_raw = train_test_split(
        X_raw, y_raw, test_size=0.2, random_state=42
    )
    print(f"  ✓ Train/Test split: {len(X_train_raw)} train, {len(X_test_raw)} test")
    
    # Train model
    model_raw = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        random_state=42,
        class_weight="balanced"
    )
    model_raw.fit(X_train_raw, y_train_raw)
    print(f"  ✓ Model trained")
    
    # Evaluate
    y_pred_raw = model_raw.predict(X_test_raw)
    y_pred_proba_raw = model_raw.predict_proba(X_test_raw)[:, 1]
    
    acc_raw = accuracy_score(y_test_raw, y_pred_raw)
    prec_raw = precision_score(y_test_raw, y_pred_raw, zero_division=0)
    rec_raw = recall_score(y_test_raw, y_pred_raw, zero_division=0)
    f1_raw = f1_score(y_test_raw, y_pred_raw, zero_division=0)
    auc_raw = roc_auc_score(y_test_raw, y_pred_proba_raw)
    
    results_raw = {
        'Approach': 'Raw Data (No CV)',
        'Accuracy': f'{acc_raw:.4f}',
        'Precision': f'{prec_raw:.4f}',
        'Recall': f'{rec_raw:.4f}',
        'F1-Score': f'{f1_raw:.4f}',
        'ROC-AUC': f'{auc_raw:.4f}',
        'Train Size': len(X_train_raw),
        'Test Size': len(X_test_raw)
    }
    
    print(f"  ✓ Evaluation completed")
    print(f"    Accuracy: {acc_raw:.4f}")
    print(f"    F1-Score: {f1_raw:.4f}")
    print(f"    ROC-AUC: {auc_raw:.4f}")
    print("✅ APPROACH 1 COMPLETED")
    
except Exception as e:
    print(f"❌ APPROACH 1 FAILED: {str(e)}")
    results_raw = None

# =====================================================================
# Approach 2: PROCESSED DATA (with CV)
# =====================================================================
print("\n[APPROACH 2] Training with PROCESSED DATA (with CV)...")

try:
    # Fetch data
    df_proc = fetch_crypto_data('BTC')
    print(f"  ✓ Data fetched: {len(df_proc)} rows")
    
    # Process with CV
    df_cv = compute_conditional_volatility(df_proc)
    print(f"  ✓ Conditional volatility computed: {len(df_cv)} rows")
    
    # Build features (with CV)
    X_proc, y_proc = build_features(df_cv)
    print(f"  ✓ Features built: {X_proc.shape[0]} samples, {X_proc.shape[1]} features")
    print(f"    Features: {list(X_proc.columns)}")
    
    # Train/Test Split (80/20)
    X_train_proc, X_test_proc, y_train_proc, y_test_proc = train_test_split(
        X_proc, y_proc, test_size=0.2, random_state=42
    )
    print(f"  ✓ Train/Test split: {len(X_train_proc)} train, {len(X_test_proc)} test")
    
    # Train model
    model_proc = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        random_state=42,
        class_weight="balanced"
    )
    model_proc.fit(X_train_proc, y_train_proc)
    print(f"  ✓ Model trained")
    
    # Evaluate
    y_pred_proc = model_proc.predict(X_test_proc)
    y_pred_proba_proc = model_proc.predict_proba(X_test_proc)[:, 1]
    
    acc_proc = accuracy_score(y_test_proc, y_pred_proc)
    prec_proc = precision_score(y_test_proc, y_pred_proc, zero_division=0)
    rec_proc = recall_score(y_test_proc, y_pred_proc, zero_division=0)
    f1_proc = f1_score(y_test_proc, y_pred_proc, zero_division=0)
    auc_proc = roc_auc_score(y_test_proc, y_pred_proba_proc)
    
    results_proc = {
        'Approach': 'Processed Data (with CV)',
        'Accuracy': f'{acc_proc:.4f}',
        'Precision': f'{prec_proc:.4f}',
        'Recall': f'{rec_proc:.4f}',
        'F1-Score': f'{f1_proc:.4f}',
        'ROC-AUC': f'{auc_proc:.4f}',
        'Train Size': len(X_train_proc),
        'Test Size': len(X_test_proc)
    }
    
    print(f"  ✓ Evaluation completed")
    print(f"    Accuracy: {acc_proc:.4f}")
    print(f"    F1-Score: {f1_proc:.4f}")
    print(f"    ROC-AUC: {auc_proc:.4f}")
    print("✅ APPROACH 2 COMPLETED")
    
except Exception as e:
    print(f"❌ APPROACH 2 FAILED: {str(e)}")
    results_proc = None

# =====================================================================
# Display Comparison Table
# =====================================================================
print("\n" + "=" * 80)
print("COMPARISON RESULTS")
print("=" * 80)

if results_raw and results_proc:
    comparison_df = pd.DataFrame([results_raw, results_proc])
    print("\n" + comparison_df.to_string(index=False))
    
    # Best performance
    print("\n" + "=" * 80)
    print("ANALYSIS:")
    print("=" * 80)
    
    acc_raw_float = float(results_raw['Accuracy'])
    acc_proc_float = float(results_proc['Accuracy'])
    
    if acc_proc_float > acc_raw_float:
        diff = (acc_proc_float - acc_raw_float) * 100
        print(f"✓ PROCESSED DATA (with CV) is BETTER")
        print(f"  - Accuracy improvement: +{diff:.2f}%")
        print(f"  - This shows that Conditional Volatility preprocessing helps model performance")
    elif acc_raw_float > acc_proc_float:
        diff = (acc_raw_float - acc_proc_float) * 100
        print(f"✓ RAW DATA is BETTER")
        print(f"  - Accuracy improvement: +{diff:.2f}%")
        print(f"  - CV preprocessing may be adding noise instead of signal")
    else:
        print(f"✓ SIMILAR PERFORMANCE")
        print(f"  - Both approaches have equivalent accuracy")
    
    print("\nRECOMMENDATIONS:")
    print("1. Implement proper train/test split in train_model.py (currently missing)")
    print("2. Add evaluation metrics to assess model generalization")
    print("3. Consider adding cross-validation for more robust evaluation")
    print("4. Based on performance, choose between RAW or PROCESSED data pipeline")

else:
    print("❌ Could not complete comparison due to errors")

print("\n" + "=" * 80)
