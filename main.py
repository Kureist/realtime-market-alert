import requests
import time
import datetime
import json
import math
import sys


def load_config():
    CONFIG_FILE = "config.json"
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ CONFIG ERROR: '{CONFIG_FILE}' not found.")
        print(f"Please copy 'config.example.json' to '{CONFIG_FILE}' and configure it.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ CONFIG ERROR: '{CONFIG_FILE}' contains invalid JSON.")
        sys.exit(1)
        
    # Validate that all required keys are present
    required_keys = [
        "discord_webhook_url", 
        "asset_ids", 
        "vs_currency", 
        "check_interval_seconds", 
        "alert_threshold_percent"
    ]
    
    missing_keys = [key for key in required_keys if key not in config or not config[key]]
    
    if missing_keys:
        print(f"❌ CONFIG ERROR: Missing or empty keys in '{CONFIG_FILE}': {', '.join(missing_keys)}")
        sys.exit(1)
        
    # Specific check for the placeholder URL
    if "PASTE_YOUR_WEBHOOK_URL_HERE" in config["discord_webhook_url"]:
        print(f"❌ CONFIG ERROR: Please replace the placeholder in 'discord_webhook_url' in '{CONFIG_FILE}'.")
        sys.exit(1)
        
    return config

def get_price():
    try:
        response = requests.get(API_URL, params=API_PARAMS)
        response.raise_for_status() 
        data = response.json()
        # Return the entire data dict for all assets
        return data
    except requests.exceptions.RequestException as e:
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

    config = load_config()
    DISCORD_WEBHOOK_URL = config["discord_webhook_url"]
    ASSET_IDS = config["asset_ids"]
    VS_CURRENCY = config["vs_currency"]
    CHECK_INTERVAL_SECONDS = config["check_interval_seconds"]
    ALERT_THRESHOLD_PERCENT = config["alert_threshold_percent"]

    API_BASE_URL = "https://api.coingecko.com/api/v3"
    assets_string = ','.join(ASSET_IDS)
    API_PARAMS = {
        "ids": assets_string,
        "vs_currencies": VS_CURRENCY
    }
    API_URL = f"{API_BASE_URL}/simple/price"

    print("--- Realtime Market Fluctuation Alert Tool ---")
    print(f"Fetching the first prices for {', '.join(ASSET_IDS)}.")
    
    # Store last prices for all assets
    last_prices = {}
    initial_data = get_price()

    if initial_data is None:
        print("Could not fetch initial prices. Please check your connection or the API status.")
        sys.exit(1)
    
    # Initialize last_prices for each asset
    for asset_id in ASSET_IDS:
        if asset_id in initial_data and VS_CURRENCY in initial_data[asset_id]:
            last_prices[asset_id] = initial_data[asset_id][VS_CURRENCY]
            print(f"Initial price for {asset_id.capitalize()}: ${last_prices[asset_id]:,.2f}")
        else:
            print(f"❌ Could not fetch initial price for {asset_id}")
            sys.exit(1)
    
    print("Starting monitoring loop...")
    
    try:
        while True:
            time.sleep(CHECK_INTERVAL_SECONDS)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_data = get_price()

            if current_data is None:
                print(f"[{current_time}] Could not fetch new prices. Skipping check.")
                continue

            # Check each asset
            for asset_id in ASSET_IDS:
                if asset_id not in current_data or VS_CURRENCY not in current_data[asset_id]:
                    print(f"[{current_time}] Could not fetch price for {asset_id}. Skipping.")
                    continue
                
                current_price = current_data[asset_id][VS_CURRENCY]
                last_price = last_prices[asset_id]

                try:
                    percentage_change = calculate_percentage_change(last_price, current_price)
                    
                    if abs(percentage_change) >= ALERT_THRESHOLD_PERCENT:
                        alert_message = (
                            f"🚨 **{asset_id.capitalize()} Price Alert!** 🚨\n"
                            f"> Price changed by **`{percentage_change:+.2f}%`** in the last {CHECK_INTERVAL_SECONDS}s!\n"
                            f"> **Old Price:** `${last_price:,.2f}`\n"
                            f"> **New Price:** `${current_price:,.2f}`"
                        )
                        
                        print(f"[{current_time}] 🔔 {asset_id.upper()} THRESHOLD EXCEEDED! Change: {percentage_change:+.2f}%")
                        send_discord_alert(alert_message)
                    else:
                        print(f"[{current_time}] {asset_id.capitalize()}: ${current_price:,.2f} | Change: {percentage_change:+.2f}% (No alert)")
                    
                    # Update last_price for this asset
                    last_prices[asset_id] = current_price

                except ValueError as e:
                    print(f"[{current_time}] ❌ Calculation Error for {asset_id}: {e}")        
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user. Exiting.")