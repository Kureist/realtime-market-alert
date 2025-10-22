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
# --- Alerting Config ---
# !!! PASTE YOUR WEBHOOK URL HERE !!!
# This is a SECRET. Do NOT share it or commit it to GitHub.
DISCORD_WEBHOOK_URL = "!!! PASTE YOUR WEBHOOK URL HERE !!!"
ALERT_THRESHOLD_PERCENT = 0.01

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
def send_discord_alert(message):
    if DISCORD_WEBHOOK_URL == "!!! PASTE YOUR WEBHOOK URL HERE !!!":
        print("❌ DISCORD ALERT: Webhook URL is not set. Skipping alert.")
        return
    payload = {
        "content": message
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status() # Check for errors from Discord
        print("🚀 Discord Alert Sent Successfully!")
    except requests.exceptions.RequestException as e:
        print(f"❌ DISCORD ALERT: Failed to send alert. Error: {e}")

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

                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                current_price = get_price()

                if current_price is None:
                    print(f"[{current_time}] Could not fetch new price. Skipping check.")
                    continue

                try:
                    percentage_change = calculate_percentage_change(last_price, current_price)
                    
                    # --- The Core Alert Logic ---
                    # We use abs() to check the magnitude of the change (positive or negative).
                    if abs(percentage_change) >= ALERT_THRESHOLD_PERCENT:
                        
                        # --- 1. Construct the Alert Message ---
                        # We use 'f-strings' to format a rich message.
                        alert_message = (
                            f"🚨 **{ASSET_ID.capitalize()} Price Alert!** 🚨\n"
                            f"> Price changed by **`{percentage_change:+.2f}%`** in the last minute!\n"
                            f"> **Old Price:** `${last_price:,.2f}`\n"
                            f"> **New Price:** `${current_price:,.2f}`"
                        )
                        
                        # --- 2. Send the Alert ---
                        print(f"[{current_time}] 🔔 THRESHOLD EXCEEDED! Change: {percentage_change:+.2f}%")
                        send_discord_alert(alert_message)
                    
                    else:
                        # --- 3. If No Alert, Just Print a Quiet Log ---
                        print(f"[{current_time}] Price: ${current_price:,.2f} | Change: {percentage_change:+.2f}% (No alert)")
                    
                    # CRUCIAL: Update last_price for the next loop.
                    last_price = current_price

                except ValueError as e:
                    print(f"[{current_time}] ❌ Calculation Error: {e}")        
except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user. Exiting.")