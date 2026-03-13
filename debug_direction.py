#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:5000"

# Test Direction Model and print actual HTML error
data = {"ticker": "BTC", "model_type": "direction"}
response = requests.post(f"{BASE_URL}/predict", data=data)

print("DIRECTION MODEL TEST RESPONSE:")
print("=" * 70)
print(response.text[:2000])  # Print first 2000 chars
print("=" * 70)
