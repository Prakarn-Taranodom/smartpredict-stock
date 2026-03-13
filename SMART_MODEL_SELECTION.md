# 🎯 Smart Model Selection Feature

## What's New

Updated **predict.html** and **app.py** to let users choose the **best model for their goal**:

### Two Models Available:

#### 1️⃣ **Direction Model** (Raw Data)
```
Goal: Predict market direction (UP/DOWN)
Accuracy: 57.34% ✅
F1-Score: 0.6554
ROC-AUC: 0.5308
Best For: Day traders who want to predict direction
```

#### 2️⃣ **Price Model** (With CV)
```
Goal: Predict accurate price levels
MAPE Error: 7.07% ✅
Best For: Price-level predictions and technical analysis
```

---

## How It Works

### Before (Old Approach)
```
User enters ticker → Fixed model (always CV-based)
```

### Now (Smart Selection)
```
User enters ticker ✅
User selects goal:
  ├─ 🎯 Predict Direction (UP/DOWN) → Uses Raw Data Model (57.34% accuracy)
  └─ 💰 Predict Price Levels → Uses With CV Model (7.07% error)
```

---

## User Interface Changes

### New Dropdown Selection

```html
<select name="model_type">
  <option value="direction">
    🎯 Direction Model (Best for UP/DOWN prediction - 57.34% accuracy)
  </option>
  <option value="price">
    💰 Price Model (Best for accurate price levels - 7.07% MAPE error)
  </option>
</select>
```

### Results Now Show

```
✅ Prediction Complete for BTC
Model Used: Raw Data Model / CV-Processed Model
Purpose: Direction Prediction / Price Prediction Accuracy
Accuracy: 0.5734 | ROC-AUC: 0.5308
Note: Best for predicting market direction / price movement
```

---

## Code Changes

### app.py Updates

**Added:**
- `build_features_raw()` - Feature builder for direction model
- Smart model selection logic based on `model_type` parameter
- Model info display with metrics and purpose

**Logic:**
```python
if model_type == "direction":
    # Use RAW DATA model (57.34% accuracy for predicting UP/DOWN)
    X, y = build_features_raw(df)
    model_info = {
        "type": "Raw Data Model",
        "purpose": "Direction Prediction (UP/DOWN)",
        "accuracy": "0.5734",
        "note": "Best for predicting market direction"
    }
else:  # model_type == "price"
    # Use WITH CV model (7.07% MAPE for accurate price levels)
    df_cv = compute_conditional_volatility(df)
    X, y = build_features(df_cv)
    model_info = {
        "type": "CV-Processed Model",
        "purpose": "Price Prediction Accuracy",
        "mape": "7.07%",
        "note": "Best for accurately predicting price movement"
    }
```

### predict.html Updates

**Added:**
- Model selection dropdown with descriptions
- Help text explaining each model
- Model info display in results

---

## Testing the Feature

### Run the app:
```bash
python app.py
```

### Test predictions:
1. Go to http://localhost:5000/predict
2. Enter ticker: **BTC**
3. Select model:
   - Option A: 🎯 Direction Model → Get direction predictions
   - Option B: 💰 Price Model → Get price-level predictions
4. Click "🔮 Predict Next 5 Days"

### Expected Results:

**For Direction Model:**
- Shows UP/DOWN predictions with 57.34% accuracy
- Uses simpler features (returns + RSI only)

**For Price Model:**
- Shows price predictions with 7.07% MAPE error
- Uses complex features (returns + RSI + CV features)

---

## Metrics Displayed

### Direction Model (Raw Data)
```
Accuracy:  0.5734 (57.34%)
Precision: 0.6591 (65.91%)
Recall:    0.6517 (65.17%)
F1-Score:  0.6554
ROC-AUC:   0.5308
```

### Price Model (With CV)
```
Accuracy:  0.4014 (40.14%)
MAE:       $4,600.98
RMSE:      $5,844.08
MAPE:      7.07%
ROC-AUC:   0.4127
```

---

## User Benefits

✅ **Choice**: Users pick the model that fits their needs  
✅ **Transparency**: Know which model is being used and why  
✅ **Better Results**: Each model is optimized for its purpose  
✅ **Education**: Learn about different prediction strategies  

---

## Files Modified

- ✅ [app.py](app.py) - Added model selection logic
- ✅ [templates/predict.html](templates/predict.html) - Added dropdown UI

## Files Created

- ✅ [eval_complete_metrics.py](eval_complete_metrics.py) - Full evaluation script

---

## What's Next?

Users can now:
1. Choose their prediction goal
2. Get the best model for that goal
3. See metrics showing why that model is best
4. Make informed decisions based on accuracy/MAPE

**Status**: ✅ Ready to use!
