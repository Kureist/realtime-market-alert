import requests
import time
import datetime


ASSET_ID = "bitcoin"
VS_CURRENCY = "usd"
API_BASE_URL = "https://api.coingecko.com/api/v3"
CHECK_INTERVAL_SECONDS = 60  
API_BASE_URL = "https://api.coingecko.com/api/v3"
API_PARAMS = {
    "ids": ASSET_ID,
    "vs_currencies": VS_CURRENCY
}
API_URL = f"{API_BASE_URL}/simple/price"

def get_price():
    try:
        response = requests.get(API_URL, params=API_PARAMS)
        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status() 
        data = response.json()
        return data[ASSET_ID][VS_CURRENCY]
    except requests.exceptions.RequestException as e:
        # Handle network-related errors, e.g., connection timeout.
        print(f"API Request Error: {e}")
        return None

def calculate_percentage_change(old_price, new_price):
    if old_price == 0:
        raise ValueError("Old price cannot be zero for percentage change calculation.")
    change = ((new_price - old_price) / old_price) * 100
    return change

if __name__ == "__main__":
    print("--- Realtime Market Fluctuation Alert Tool ---")
    print(f"Fetching the first price for {ASSET_ID.capitalize()}.")
    last_price = get_price()

    if last_price is None:
        print("Could not fetch initial price. Please check your connection or the API status.")
    else:
        print(f"Initial price for {ASSET_ID.capitalize()} is ${last_price}. Starting monitoring loop...")
        
        try:
            while True:
                time.sleep(CHECK_INTERVAL_SECONDS)

                # Get the new current price.
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                current_price = get_price()

                if current_price is None:
                    print(f"[{current_time}] Could not fetch new price. Skipping this check.")
                    continue

                # Calculate the percentage change.
                try:
                    percentage_change = calculate_percentage_change(last_price, current_price)
                    
                    #    :,.2f formats the price with commas and 2 decimal places.
                    #    :+.2f formats the change to always show a + or - sign.
                    print(f"[{current_time}] Price: ${current_price:,.2f} | Change: {percentage_change:+.2f}%")

                    last_price = current_price

                except ValueError as e:
                    print(f"[{current_time}]  Calculation Error: {e}")

        except KeyboardInterrupt:
            # 6. Handle Ctrl+C gracefully.
            print("\n Monitoring stopped by user. Exiting.")