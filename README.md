# 📈 SmartPredict Stock

A stock market analysis and clustering web application built entirely through **vibe coding** - created without any prior web development experience or formal coding knowledge. This project demonstrates what's possible when you combine curiosity, AI assistance, and a willingness to learn by doing.

## 🎯 What This App Does

SmartPredict Stock is a comprehensive stock analysis tool that combines machine learning, time series analysis, and clustering algorithms to help users understand stock market patterns and volatility.

### Core Features

#### 1. **Stock Price Prediction**
- Predicts next 5 days of stock price movements (UP/DOWN)
- Uses **ARIMA-GARCH** model for volatility forecasting
- Employs **Random Forest** classifier for direction prediction
- Calculates **Conditional Volatility (CV)** as the primary feature
- Supports major indices: NASDAQ-100, SET-50, SET-100, S&P 500
- Works with cryptocurrencies (BTC-USD, ETH-USD, etc.)

#### 2. **Stock Clustering Analysis**
- Groups stocks based on volatility patterns using unsupervised learning
- Two clustering methods:
  - **DTW (Dynamic Time Warping)**: Captures time series shape similarity
  - **Euclidean Distance**: Standard point-to-point comparison
- Interactive **Elbow Plot** with automatic optimal K detection using Kneedle Algorithm
- Cluster evaluation metrics:
  - **Silhouette Score**: Measures cluster cohesion
  - **Davies-Bouldin Index**: Evaluates cluster separation
- PCA visualization for 2D cluster representation

#### 3. **Interactive Workflow**
- Multi-step clustering process:
  1. Select market (NASDAQ-100, SET-50, SET-100, S&P 500)
  2. Choose specific stocks or entire industries
  3. Select clustering method (DTW/Euclidean)
  4. View elbow plot with auto-detected optimal K
  5. Analyze clustering results with visualizations

## 🛠️ Tech Stack

### Backend
- **Flask** - Lightweight Python web framework
- **yfinance** - Real-time stock data fetching from Yahoo Finance
- **pandas & numpy** - Data manipulation and numerical computing

### Machine Learning & Statistics
- **scikit-learn** - Random Forest, KMeans, PCA, evaluation metrics
- **tslearn** - Time series clustering with DTW
- **statsmodels** - Statistical modeling and ARIMA
- **arch** - GARCH volatility modeling
- **pmdarima** - Automatic ARIMA parameter selection

### Frontend
- **Chart.js** - Interactive charts and visualizations
- **HTML/CSS/JavaScript** - Responsive UI with gradient designs
- **Bootstrap-inspired styling** - Custom CSS without frameworks

### Deployment
- **Gunicorn** - Production WSGI server
- **Render** - Cloud hosting platform (free tier)

## 🧠 How It Works

### Prediction Pipeline
1. **Data Fetching**: Download historical stock prices using yfinance
2. **Log Returns**: Calculate logarithmic returns for stationarity
3. **ARIMA Modeling**: Remove trend and seasonality from returns
4. **GARCH Modeling**: Extract conditional volatility from residuals
5. **Feature Engineering**: Create lag features, technical indicators
6. **Random Forest**: Train classifier on engineered features
7. **Prediction**: Forecast next 5 days with probability scores

### Clustering Pipeline
1. **Data Preparation**: Fetch stock data for selected market
2. **CV Calculation**: Compute conditional volatility for each stock
3. **Normalization**: Z-score standardization across stocks
4. **Elbow Analysis**: Test K=2 to K=9, calculate inertia
5. **Optimal K Detection**: Kneedle algorithm finds elbow point
6. **Clustering**: Apply DTW or Euclidean KMeans
7. **Evaluation**: Calculate Silhouette Score and Davies-Bouldin Index
8. **Visualization**: PCA reduction to 2D for plotting

## 💡 The Vibe Coding Story

This entire project was built through **vibe coding** - an experimental approach where someone with zero web development experience uses AI assistance to build a functional web application. 

### What is Vibe Coding?
- Learning by building, not studying first
- Using AI (like Amazon Q, ChatGPT) as a coding partner
- Iterative development: try → fail → fix → learn
- Focus on functionality over perfect code
- Embracing mistakes as learning opportunities

### Challenges Overcome
- Never used Flask before → Built full REST API
- No JavaScript knowledge → Created interactive UI
- No ML deployment experience → Integrated complex models
- No understanding of ARIMA/GARCH → Implemented volatility pipeline
- No clustering experience → Built DTW-based analysis tool

### Key Learnings
- Web frameworks aren't as scary as they seem
- AI can explain complex concepts in simple terms
- Breaking problems into small steps makes anything achievable
- Documentation + AI assistance = powerful combination
- Real projects teach more than tutorials

## 📊 Technical Highlights

### Conditional Volatility (CV)
Instead of using raw stock prices, this app uses **Conditional Volatility** as the primary feature:
- More stable than prices
- Captures market uncertainty
- Better for clustering similar risk profiles
- Derived from GARCH(1,1) model

### Kneedle Algorithm
Automatic elbow detection using geometric approach:
- Normalizes data to [0,1] range
- Calculates perpendicular distance from baseline
- Finds point with maximum distance
- More reliable than derivative methods

### DTW Clustering
Dynamic Time Warping allows:
- Alignment of time series with different phases
- Shape-based similarity matching
- Robust to temporal shifts
- Better for financial time series than Euclidean

## 🚀 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Visit
http://localhost:5000
```

## 📁 Project Structure

```
smartpredict_stock/
├── app.py                      # Flask routes and API endpoints
├── clustering_module.py        # Clustering algorithms and metrics
├── data_preparation.py         # Stock data fetching and preprocessing
├── volatility_pipeline.py      # ARIMA-GARCH CV calculation
├── feature_engineering.py      # ML feature creation
├── train_model.py              # Random Forest training
├── fetch_stock.py              # yfinance wrapper
├── technical_indicators.py     # TA indicators (RSI, MACD, etc.)
├── templates/                  # HTML templates
│   ├── index.html             # Landing page
│   ├── predict.html           # Prediction interface
│   ├── cluster.html           # Clustering workflow
│   ├── cluster_select_method.html
│   ├── cluster_elbow.html     # Elbow plot
│   └── cluster_result.html    # Results visualization
├── static/                     # Static assets
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎓 What I Learned

### Technical Skills
- Flask web framework and routing
- REST API design
- HTML/CSS/JavaScript basics
- Chart.js for data visualization
- Git version control
- Cloud deployment (Render)

### Data Science Skills
- Time series analysis (ARIMA, GARCH)
- Clustering algorithms (KMeans, DTW)
- Feature engineering for ML
- Model evaluation metrics
- Dimensionality reduction (PCA)

### Soft Skills
- Breaking complex problems into steps
- Reading documentation effectively
- Debugging with systematic approach
- Asking better questions to AI
- Persistence through errors

## 🤝 Contributing

This project welcomes contributions! Whether you're also learning or an expert, feel free to:
- Report bugs
- Suggest features
- Improve documentation
- Optimize code
- Share your vibe coding story

## 📝 License

MIT License - Feel free to use this project for learning or building your own tools.

## 🙏 Acknowledgments

- Built with assistance from **Amazon Q Developer**
- Stock data provided by **Yahoo Finance** via yfinance
- Inspired by the vibe coding movement
- Thanks to the open-source community for amazing libraries

---

**Note**: This is a learning project built through vibe coding. The predictions are for educational purposes only and should not be used for actual trading decisions. Always do your own research and consult financial advisors.

---

*"The best way to learn coding is to build something you're curious about, even if you don't know how yet."*
