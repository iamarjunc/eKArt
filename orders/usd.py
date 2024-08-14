import requests
from forex_python.converter import CurrencyRates

# Create an object of the CurrencyRates class
c = CurrencyRates()

try:
    # Check if API is working and returning data
    usd_to_inr = c.get_rate('USD', 'INR')
    print(f"Current USD to INR rate: {usd_to_inr}")
except requests.exceptions.RequestException as e:
    print("Request failed:", e)
except requests.exceptions.JSONDecodeError as e:
    print("JSON decode error:", e)
except Exception as e:
    print("An error occurred:", e)
