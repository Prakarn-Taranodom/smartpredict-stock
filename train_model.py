from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, mean_absolute_error, mean_squared_error
import numpy as np
import pandas as pd

def calculate_regression_metrics(y_true, y_pred):
    """
    Calculate regression metrics for price prediction
    
    Args:
        y_true: Actual prices
        y_pred: Predicted prices
    
    Returns:
        Dictionary with MAE, RMSE, MAPE
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    return {
        'mae': mae,
        'rmse': rmse,
        'mape': mape
    }

def predict_prices_for_evaluation(model, X, df, n_test_samples=10):
    """
    Generate price predictions for evaluation on test data
    
    Args:
        model: Trained RandomForest model
        X: Features DataFrame
        df: Price DataFrame with OHLCV data
        n_test_samples: Number of predictions to generate
    
    Returns:
        Tuple of (predicted_prices, predicted_directions)
    """
    preds, probs = [], []
    predicted_prices = []
    
    # Use last n_test_samples for evaluation
    for i in range(n_test_samples):
        if i + 1 >= len(X):
            break
            
        X_current = X.iloc[-(n_test_samples-i):-(n_test_samples-i-1)].copy()
        
        p = model.predict(X_current)[0]
        prob = model.predict_proba(X_current)[0][1]
        
        preds.append(int(p))
        probs.append(prob)
    
    # Generate price projections
    last_price = df["Close"].iloc[-1]
    returns = df["log_return"].dropna()
    avg_daily_return = returns.mean()
    daily_volatility = returns.std()
    
    current_price = last_price
    for i in range(min(n_test_samples, len(preds))):
        expected_return = (
            avg_daily_return * probs[i]
            if preds[i] == 1
            else -avg_daily_return * (1 - probs[i])
        )
        expected_return += np.random.normal(0, daily_volatility * 0.5)
        current_price *= (1 + expected_return)
        predicted_prices.append(current_price)
    
    return np.array(predicted_prices), np.array(preds)

def train_rf(X, y, df=None, test_size=0.2, random_state=42, return_only_model=False):
    """
    Train RandomForest with proper train/test split and comprehensive evaluation.
    
    Args:
        X: Features
        y: Target variable (UP/DOWN classification)
        df: DataFrame with price data (for regression evaluation)
        test_size: Proportion of data to use for testing (default 0.2)
        random_state: Random seed for reproducibility
        return_only_model: If True, returns only model (for backward compatibility with app.py)
    
    Returns:
        If return_only_model=True: model (for backward compatibility)
        Otherwise: (model, metrics, train_test_data)
            - model: Trained RandomForest model
            - metrics: Dictionary with classification + regression metrics
            - train_test_data: Tuple of (X_train, X_test, y_train, y_test)
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        random_state=random_state,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)
    
    # Evaluate CLASSIFICATION metrics
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        # Classification metrics
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba),
        'train_size': len(X_train),
        'test_size': len(X_test)
    }
    
    # Evaluate REGRESSION metrics (if price data provided)
    if df is not None:
        try:
            # Generate estimated prices based on predictions
            last_price = df["Close"].iloc[-1]
            returns = df["log_return"].dropna()
            avg_daily_return = returns.mean()
            daily_volatility = returns.std()
            
            predicted_prices = []
            current_price = last_price
            
            for prob in y_pred_proba[:min(len(y_pred_proba), 10)]:
                expected_return = avg_daily_return * prob if prob > 0.5 else -avg_daily_return * (1 - prob)
                expected_return += np.random.normal(0, daily_volatility * 0.5)
                current_price *= (1 + expected_return)
                predicted_prices.append(current_price)
            
            # Get actual prices for comparison
            actual_prices = df["Close"].iloc[-(len(predicted_prices)):].values
            
            if len(predicted_prices) > 0 and len(actual_prices) > 0:
                regression_metrics = calculate_regression_metrics(actual_prices, np.array(predicted_prices))
                metrics.update({
                    'mae': regression_metrics['mae'],
                    'rmse': regression_metrics['rmse'],
                    'mape': regression_metrics['mape']
                })
        except Exception as e:
            metrics.update({
                'mae': None,
                'rmse': None,
                'mape': None,
                'regression_error': str(e)
            })
    else:
        metrics.update({
            'mae': None,
            'rmse': None,
            'mape': None
        })
    
    if return_only_model:
        return model
    
    return model, metrics, (X_train, X_test, y_train, y_test)

def predict_next_n_days_prices(model, X, df, n=5):
    preds, probs = [], []
    X_last = X.iloc[-1:].copy()

    for _ in range(n):
        p = model.predict(X_last)[0]
        prob = model.predict_proba(X_last)[0][1]

        preds.append(int(p))
        probs.append(round(prob, 4))

        X_last["return_lag2"] = X_last["return_lag1"]
        X_last["return_lag1"] = 0
        
        # Only update CV lags if they exist (for CV models)
        if "cv_lag1" in X_last.columns:
            X_last["cv_lag2"] = X_last["cv_lag1"]
            X_last["cv_lag1"] = 0

    last_price = df["Close"].iloc[-1]
    returns = df["log_return"].dropna()

    avg_daily_return = returns.mean()
    daily_volatility = returns.std()

    predicted_prices = []
    current_price = last_price

    for i in range(n):
        expected_return = (
            avg_daily_return * probs[i]
            if preds[i] == 1
            else -avg_daily_return * (1 - probs[i])
        )

        expected_return += np.random.normal(0, daily_volatility * 0.5)
        current_price *= (1 + expected_return)
        predicted_prices.append(round(current_price, 2))

    return predicted_prices, preds, probs
