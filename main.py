import requests
import time
import datetime
import json
import math
import sys
import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Setup logging configuration with both file and console handlers"""
    # Create logs directory if it doesn't exist
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create logger
    logger = logging.getLogger('MarketAlert')
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    # File handler with rotation (max 5MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(
        'logs/market_alert.log',
        maxBytes=5*1024*1024,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def load_config():
    CONFIG_FILE = "config.json"
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(f"CONFIG ERROR: '{CONFIG_FILE}' not found.")
        print(f"❌ CONFIG ERROR: '{CONFIG_FILE}' not found.")
        print(f"Please copy 'config.example.json' to '{CONFIG_FILE}' and configure it.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"CONFIG ERROR: '{CONFIG_FILE}' contains invalid JSON.")
        print(f"❌ CONFIG ERROR: '{CONFIG_FILE}' contains invalid JSON.")
        sys.exit(1)
        
    # Validate that all required keys are present
    required_keys = [
        "discord_webhook_url", 
        "assets", 
        "vs_currency", 
        "check_interval_seconds"
    ]
    
    missing_keys = [key for key in required_keys if key not in config or not config[key]]
    
    if missing_keys:
        logger.error(f"CONFIG ERROR: Missing or empty keys: {', '.join(missing_keys)}")
        print(f"❌ CONFIG ERROR: Missing or empty keys in '{CONFIG_FILE}': {', '.join(missing_keys)}")
        sys.exit(1)
    
    # Validate assets structure
    if not isinstance(config["assets"], list) or len(config["assets"]) == 0:
        logger.error("CONFIG ERROR: 'assets' must be a non-empty list")
        print(f"❌ CONFIG ERROR: 'assets' must be a non-empty list in '{CONFIG_FILE}'.")
        sys.exit(1)
    
    for asset in config["assets"]:
        if "id" not in asset or "alert_threshold_percent" not in asset:
            logger.error("CONFIG ERROR: Each asset must have 'id' and 'alert_threshold_percent'")
            print(f"❌ CONFIG ERROR: Each asset must have 'id' and 'alert_threshold_percent' in '{CONFIG_FILE}'.")
            sys.exit(1)
        
    # Specific check for the placeholder URL
    if "PASTE_YOUR_WEBHOOK_URL_HERE" in config["discord_webhook_url"]:
        logger.error("CONFIG ERROR: Webhook URL placeholder not replaced")
        print(f"❌ CONFIG ERROR: Please replace the placeholder in 'discord_webhook_url' in '{CONFIG_FILE}'.")
        sys.exit(1)
    
    logger.info("Configuration loaded successfully")
    return config

def get_price():
    try:
        response = requests.get(API_URL, params=API_PARAMS)
        response.raise_for_status() 
        data = response.json()
        logger.debug(f"API request successful. Received data for {len(data)} assets")
        # Return the entire data dict for all assets
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request Error: {e}")
        print(f"API Request Error: {e}")
        return None

def send_discord_alert(message):
    if DISCORD_WEBHOOK_URL == "!!! PASTE YOUR WEBHOOK URL HERE !!!":
        logger.warning("DISCORD ALERT: Webhook URL is not set. Skipping alert.")
        print("❌ DISCORD ALERT: Webhook URL is not set. Skipping alert.")
        return
    payload = {
        "content": message
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status() # Check for errors from Discord
        logger.info("Discord alert sent successfully")
        print("🚀 Discord Alert Sent Successfully!")
    except requests.exceptions.RequestException as e:
        logger.error(f"DISCORD ALERT: Failed to send alert. Error: {e}")
        print(f"❌ DISCORD ALERT: Failed to send alert. Error: {e}")

def calculate_percentage_change(old_price, new_price):
    if old_price == 0:
        raise ValueError("Old price cannot be zero for percentage change calculation.")
    change = ((new_price - old_price) / old_price) * 100
    return change

if __name__ == "__main__":
    # Setup logging first
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("Starting Realtime Market Fluctuation Alert Tool")
    logger.info("=" * 50)

    config = load_config()
    DISCORD_WEBHOOK_URL = config["discord_webhook_url"]
    ASSETS = config["assets"]
    VS_CURRENCY = config["vs_currency"]
    CHECK_INTERVAL_SECONDS = config["check_interval_seconds"]

    # Create dictionaries for easy access
    ASSET_IDS = [asset["id"] for asset in ASSETS]
    ASSET_THRESHOLDS = {asset["id"]: asset["alert_threshold_percent"] for asset in ASSETS}

    API_BASE_URL = "https://api.coingecko.com/api/v3"
    assets_string = ','.join(ASSET_IDS)
    API_PARAMS = {
        "ids": assets_string,
        "vs_currencies": VS_CURRENCY
    }
    API_URL = f"{API_BASE_URL}/simple/price"

    logger.info(f"Monitoring assets: {', '.join(ASSET_IDS)}")
    logger.info(f"Check interval: {CHECK_INTERVAL_SECONDS} seconds")
    logger.info(f"Currency: {VS_CURRENCY.upper()}")
    
    print("--- Realtime Market Fluctuation Alert Tool ---")
    
    # Store last prices for all assets
    last_prices = {}
    initial_data = get_price()

    if initial_data is None:
        logger.error("Could not fetch initial prices. Exiting.")
        sys.exit(1)
    
    # Initialize last_prices for each asset
    for asset_id in ASSET_IDS:
        if asset_id in initial_data and VS_CURRENCY in initial_data[asset_id]:
            last_prices[asset_id] = initial_data[asset_id][VS_CURRENCY]
            logger.info(f"Initial price for {asset_id}: ${last_prices[asset_id]:,.2f} (Threshold: {ASSET_THRESHOLDS[asset_id]}%)")
        else:
            logger.error(f"Could not fetch initial price for {asset_id}")
            sys.exit(1)
    
    logger.info("Starting monitoring loop...")
    
    try:
        while True:
            time.sleep(CHECK_INTERVAL_SECONDS)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_data = get_price()

            if current_data is None:
                logger.warning("Could not fetch new prices. Skipping check.")
                continue

            # Check each asset
            for asset_id in ASSET_IDS:
                if asset_id not in current_data or VS_CURRENCY not in current_data[asset_id]:
                    logger.warning(f"Could not fetch price for {asset_id}. Skipping.")
                    continue
                
                current_price = current_data[asset_id][VS_CURRENCY]
                last_price = last_prices[asset_id]
                threshold = ASSET_THRESHOLDS[asset_id]

                try:
                    percentage_change = calculate_percentage_change(last_price, current_price)
                    
                    if abs(percentage_change) >= threshold:
                        alert_message = (
                            f"🚨 **{asset_id.capitalize()} Price Alert!** 🚨\n"
                            f"> Price changed by **`{percentage_change:+.2f}%`** in the last {CHECK_INTERVAL_SECONDS}s!\n"
                            f"> **Threshold:** `{threshold}%`\n"
                            f"> **Old Price:** `${last_price:,.2f}`\n"
                            f"> **New Price:** `${current_price:,.2f}`"
                        )
                        
                        logger.warning(f"{asset_id.upper()} THRESHOLD EXCEEDED! Change: {percentage_change:+.2f}% (Threshold: {threshold}%)")
                        send_discord_alert(alert_message)
                    else:
                        logger.debug(f"{asset_id}: ${current_price:,.2f} | Change: {percentage_change:+.2f}% (Threshold: {threshold}%)")
                    
                    # Update last_price for this asset
                    last_prices[asset_id] = current_price

                except ValueError as e:
                    logger.error(f"Calculation Error for {asset_id}: {e}")
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user. Exiting.")