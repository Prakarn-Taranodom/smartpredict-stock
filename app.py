from flask import Flask, render_template, request, jsonify
from fetch_coinlore import fetch_crypto_data
from crypto_stats import get_crypto_stats
from volatility_pipeline import compute_conditional_volatility
from feature_engineering import build_features, create_target, add_lag_features
from train_model import predict_next_n_days_prices, train_rf
from data_preparation_platform import prepare_platform_data, get_crypto_platforms, get_platform_cryptos, prepare_crypto_data_for_clustering
from clustering_module import (
    DTWKMeansClustering,
    EuclideanKMeansClustering,
    compute_elbow_curve,
    compute_cluster_visualization_data,
    get_cluster_statistics,
    detect_elbow_point,
    compute_cluster_metrics
)

import pandas as pd
import numpy as np

app = Flask(__name__)

# =================================================
# Helper Functions for Feature Building
# =================================================
def build_features_raw(df):
    """Build features from raw data (no CV processing)"""
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
    return X, y, df  # Return df too so it has log_return for predictions

# =================================================
# INDEX
# =================================================
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# =================================================
# PREDICT (with model selection)
# =================================================
@app.route("/predict", methods=["GET", "POST"])
def predict():
    result = None
    ticker = None
    model_type = None
    model_info = None

    if request.method == "POST":
        ticker = request.form.get("ticker", "").upper()
        model_type = request.form.get("model_type", "raw")  # "raw" or "cv"

        if not ticker:
            return render_template("predict.html", error="Please enter a crypto symbol")

        try:
            df = fetch_crypto_data(ticker)
            
            # Choose model based on user selection
            if model_type == "direction":
                # Use RAW DATA model - Best for direction prediction (57.34% accuracy)
                X, y, df = build_features_raw(df)
                model, metrics, _ = train_rf(X, y, return_only_model=False)
                model_info = {
                    "type": "Raw Data Model",
                    "purpose": "Direction Prediction (UP/DOWN)",
                    "accuracy": f"{metrics['accuracy']:.4f}",
                    "f1_score": f"{metrics['f1']:.4f}",
                    "roc_auc": f"{metrics['roc_auc']:.4f}",
                    "note": "Best for predicting market direction"
                }
                
            else:  # model_type == "price"
                # Use WITH CV model - Best for price prediction (7.07% MAPE error)
                df_cv = compute_conditional_volatility(df)
                X, y = build_features(df_cv)
                model, metrics, _ = train_rf(X, y, df=df, return_only_model=False)
                model_info = {
                    "type": "CV-Processed Model",
                    "purpose": "Price Prediction Accuracy",
                    "accuracy": f"{metrics['accuracy']:.4f}",
                    "mape": f"{metrics['mape']:.2f}%" if metrics.get('mape') else "N/A",
                    "roc_auc": f"{metrics['roc_auc']:.4f}",
                    "note": "Best for accurately predicting price movement"
                }
                df = df_cv
            
            predicted_prices, preds, probs = predict_next_n_days_prices(
                model, X, df, n=5
            )

            last_date = pd.to_datetime(df.index[-1])
            future_dates = [
                (last_date + pd.Timedelta(days=i + 1)).strftime("%Y-%m-%d")
                for i in range(5)
            ]

            dates = pd.to_datetime(df.index).strftime("%Y-%m-%d").tolist()
            prices = df["Close"].round(2).tolist()
            if "cv" in df.columns:
                cv_values = df["cv"].round(4).tolist()
            else:
                cv_values = [None] * len(prices)
            
            importance = (
                pd.Series(model.feature_importances_, index=X.columns)
                .sort_values(ascending=False)
            )
            
            # Get crypto stats
            crypto_stats = get_crypto_stats(ticker)

            result = {
                "ticker": ticker,
                "model_type": model_type,
                "model_info": model_info,
                "crypto_stats": crypto_stats,
                "predictions": [
                    {
                        "date": d,
                        "prediction": "UP" if p == 1 else "DOWN",
                        "probability": round(float(prob), 4),
                        "predicted_price": round(float(price), 2),
                    }
                    for d, p, prob, price in zip(
                        future_dates, preds, probs, predicted_prices
                    )
                ],
                "dates": dates,
                "prices": prices,
                "cv": cv_values,
                "feat_items": list(
                    zip(
                        importance.index.tolist(),
                        importance.values.round(4).tolist(),
                    )
                ),
            }

        except Exception as e:
            return render_template("predict.html", error=str(e), ticker=ticker, model_type=model_type)

    return render_template("predict.html", result=result, ticker=ticker, model_type=model_type)


# =================================================
# CLUSTER ENTRY
# =================================================
@app.route("/cluster", methods=["GET", "POST"])
def cluster():
    return render_template("cluster.html")


# =================================================
# ✅ API: STOCK LIST (แก้ Unexpected token '<')
# =================================================
@app.route("/api/cryptos/<platform>")
def api_cryptos(platform):
    try:
        cryptos = get_platform_cryptos(platform)
        
        cryptos_by_category = {platform.title(): []}
        for crypto in cryptos:
            cryptos_by_category[platform.title()].append({
                "symbol": crypto['symbol'],
                "name": crypto['name']
            })

        return jsonify({
            "cryptos_by_category": cryptos_by_category,
            "total_cryptos": len(cryptos)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================================
# CLUSTER: Step 1 - Select Method
# =================================================
@app.route("/cluster/select-method/<platform>")
def cluster_select_method(platform):
    # Handle multiple platforms
    platforms_param = request.args.get('platforms', '')
    if platforms_param:
        # Multiple platforms selected
        return render_template("cluster_select_method.html", market='multi', platforms=platforms_param)
    else:
        # Single platform
        return render_template("cluster_select_method.html", market=platform)


# =================================================
# CLUSTER: Step 2 - Show Elbow Plot (รับ stocks)
# =================================================
@app.route("/cluster/elbow/<platform>")
def cluster_elbow(platform):
    method = request.args.get("method", "dtw")
    cryptos_param = request.args.get("cryptos", "")
    platforms_param = request.args.get("platforms", "")
    
    try:
        # Handle multiple platforms
        if platform == 'multi' and platforms_param:
            platforms = platforms_param.split(',')
            all_cryptos = []
            for p in platforms:
                p_cryptos = get_platform_cryptos(p)
                for c in p_cryptos:
                    c['platform'] = p.title()
                all_cryptos.extend(p_cryptos)
            
            cv_df = prepare_crypto_data_for_clustering(
                all_cryptos,
                window_days=60,
                include_platform=True
            )
        elif cryptos_param:
            selected_cryptos = cryptos_param.split(',')
            all_cryptos = get_platform_cryptos(platform)
            crypto_objs = [c for c in all_cryptos if c['symbol'] in selected_cryptos]
            for c in crypto_objs:
                c['platform'] = platform.title()
            cv_df = prepare_crypto_data_for_clustering(
                crypto_objs,
                window_days=60,
                include_platform=True
            )
        else:
            cv_df = prepare_platform_data(
                platform,
                window_days=60,
                include_platform=True
            )

        if len(cv_df) < 3:
            return render_template(
                "cluster_elbow.html",
                elbow_data={"error": "Not enough cryptos"},
                market=platform
            )

        X = cv_df.iloc[:, 1:-1].values

        elbow_data = compute_elbow_curve(
            X,
            k_range=range(2, min(10, len(X))),
            method=method
        )

        elbow_info = detect_elbow_point(
            elbow_data["inertia_values"],
            elbow_data["k_values"]
        )

        elbow_data.update(elbow_info)
        elbow_data["method"] = method
        elbow_data["cryptos"] = cryptos_param
        elbow_data["platforms"] = platforms_param

        return render_template(
            "cluster_elbow.html",
            elbow_data=elbow_data,
            market=platform
        )

    except Exception as e:
        return render_template(
            "cluster_elbow.html",
            elbow_data={"error": str(e)},
            market=platform
        )


# =================================================
# CLUSTER RESULT (รับ stocks parameter)
# =================================================
@app.route("/cluster/result/<platform>/<int:k>")
def cluster_result(platform, k):
    method = request.args.get("method", "dtw")
    cryptos_param = request.args.get("cryptos", "")
    platforms_param = request.args.get("platforms", "")

    try:
        # Handle multiple platforms
        if platform == 'multi' and platforms_param:
            platforms = platforms_param.split(',')
            all_cryptos = []
            for p in platforms:
                p_cryptos = get_platform_cryptos(p)
                for c in p_cryptos:
                    c['platform'] = p.title()
                all_cryptos.extend(p_cryptos)
            
            cv_df = prepare_crypto_data_for_clustering(
                all_cryptos,
                window_days=60,
                include_platform=True
            )
        elif cryptos_param:
            selected_cryptos = cryptos_param.split(',')
            all_cryptos = get_platform_cryptos(platform)
            crypto_objs = [c for c in all_cryptos if c['symbol'] in selected_cryptos]
            for c in crypto_objs:
                c['platform'] = platform.title()
            cv_df = prepare_crypto_data_for_clustering(
                crypto_objs,
                window_days=60,
                include_platform=True
            )
        else:
            cv_df = prepare_platform_data(
                platform,
                window_days=60,
                include_platform=True
            )

        if len(cv_df) < 3:
            return render_template(
                "cluster_result.html",
                result={"error": "Not enough cryptos for clustering"},
                market=platform,
                category_filter="all"
            )

        X = cv_df.iloc[:, 1:-1].values
        crypto_ids = cv_df["crypto_id"].values

        clustering = (
            DTWKMeansClustering(k)
            if method == "dtw"
            else EuclideanKMeansClustering(k)
        )

        labels = clustering.fit_predict(X)
        metrics = compute_cluster_metrics(X, labels, method=method)

        assignments_df = clustering.get_cluster_assignments(crypto_ids)
        assignments_df["category"] = cv_df["category"].values

        viz_pca = compute_cluster_visualization_data(X, labels, method="pca")
        cluster_stats = get_cluster_statistics(cv_df, labels)

        result = {
            "market": platform,
            "method": method,
            "optimal_k": k,
            "metrics": metrics,
            "assignments": assignments_df.to_dict("records"),
            "cluster_stats": cluster_stats,
            "viz_pca": viz_pca
        }

        return render_template(
            "cluster_result.html",
            result=result,
            market=platform,
            category_filter="all"
        )

    except Exception as e:
        return render_template(
            "cluster_result.html",
            result={"error": str(e)},
            market=platform,
            category_filter="all"
        )


# =================================================
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
