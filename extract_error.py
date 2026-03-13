#!/usr/bin/env python3
import requests
import re

BASE_URL = "http://localhost:5000"

# Test Direction Model and extract error
data = {"ticker": "BTC", "model_type": "direction"}
response = requests.post(f"{BASE_URL}/predict", data=data)
html = response.text

# Find error message between "Error:" tags
error_match = re.search(r'Error:\s*([^<]+)', html)
if error_match:
    error_msg = error_match.group(1).strip()
    print(f"ERROR FOUND: {error_msg}")
else:
    # Try finding error in different format
    if "<h4>Error" in html or "❌" in html:
        error_section = html[html.find("Error"):html.find("Error")+500]
        print("Error section found:")
        print(error_section)
    else:
        # Check if there's any content after the form
        if "results" in html.lower() or "prediction" in html.lower():
            idx = html.find("<h3>")
            if idx > 0:
                print(html[idx:idx+1500])
        else:
            print("No error found - checking for specific text...")
            if "Traceback" in html:
                traceback_start = html.find("Traceback")
                print(html[traceback_start:traceback_start+1000])
