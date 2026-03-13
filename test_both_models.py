#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("TESTING BOTH MODELS")
print("=" * 70)

# Test 1: Direction Model
print("\n[1] Testing DIRECTION MODEL (57.34% accuracy)...")
data_direction = {
    "ticker": "BTC",
    "model_type": "direction"
}
response = requests.post(f"{BASE_URL}/predict", data=data_direction)
if response.status_code == 200:
    content = response.text
    if "Error" in content:
        print("    [X] ERROR FOUND:")
        if "Error:" in content:
            error_msg = content.split("Error:")[1].split("<")[0].strip()
            print(f"       {error_msg}")
    else:
        has_predictions = "UP" in content or "DOWN" in content
        has_confidence = "Confidence" in content or "confidence" in content
        has_model_info = "57.34" in content or "Direction Model" in content
        
        print(f"    [OK] Status: {response.status_code}")
        print(f"    [OK] Has predictions: {has_predictions}")
        print(f"    [OK] Shows model info: {has_model_info}")
else:
    print(f"    [X] Status: {response.status_code} (ERROR)")

# Test 2: Price Model  
print("\n[2] Testing PRICE MODEL (7.07% MAPE error)...")
data_price = {
    "ticker": "BTC",
    "model_type": "price"
}
response = requests.post(f"{BASE_URL}/predict", data=data_price)
if response.status_code == 200:
    content = response.text
    if "Error" in content:
        print("    [X] ERROR FOUND:")
        if "Error:" in content:
            error_msg = content.split("Error:")[1].split("<")[0].strip()
            print(f"       {error_msg}")
    else:
        has_predictions = "$" in content or "Price" in content
        has_model_info = "7.07" in content or "Price Model" in content
        
        print(f"    [OK] Status: {response.status_code}")
        print(f"    [OK] Has predictions: {has_predictions}")
        print(f"    [OK] Shows model info: {has_model_info}")
else:
    print(f"    [X] Status: {response.status_code} (ERROR)")

print("\n" + "=" * 70)
print("[OK] TESTING COMPLETE")
print("=" * 70)
print("\nSummary:")
print("  Direction Model: Predicts UP/DOWN based on price direction")
print("  Price Model:     Predicts future prices (5-day forecast)")
print("\nBoth models available at: http://localhost:5000/predict")

