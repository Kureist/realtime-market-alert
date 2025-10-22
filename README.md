# Realtime Market Fluctuation Alert Tool

A simple, configurable Python tool to monitor real-time price fluctuations of financial assets (like cryptocurrencies) and send immediate alerts to Discord when volatility exceeds a set threshold.

This project was built from scratch as a guided learning exercise.

## Core Features

- **Real-time Price Fetching:** Connects to the CoinGecko API to get live asset prices.
- **Continuous Monitoring:** Runs in an infinite loop, checking the price at a user-defined interval.
- **Volatility Calculation:** Calculates the percentage change between the last checked price and the current price.
- **Threshold-Based Alerting:** Triggers an alert only if the price change (positive or negative) exceeds a custom percentage.
- **Discord Integration:** Sends a richly formatted alert message to a Discord channel via Webhook.
- **Fully Configurable:** All parameters (asset, currency, interval, thresholds, webhook URL) are managed in an external `config.json` file, requiring zero code changes to adapt.

## Technology Stack

- **Python 3**
- **Libraries:**
  - `requests`: For all HTTP communication (both GET for API data and POST for Discord alerts).
- **Configuration:**
  - `JSON`: For managing user configuration and separating secrets from code.
- **Environment:**
  - `venv`: For virtual environment management.
  - `requirements.txt`: For dependency tracking.

---

## Installation & Setup

Follow these steps to get the tool running on your own machine.

### 1. Prerequisites

- Python 3.7 or newer.
- `git` installed on your system.

### 2. Clone the Repository

Clone this project to your local machine:

```BASH
git clone https://github.com/YOUR_USERNAME/realtime-market-alert.git
cd realtime-market-alert
```
*(Remember to replace `YOUR_USERNAME` with your actual GitHub username!)*


### 3. Install Dependencies

Install the required Python libraries using the `requirements.txt` file:

```BASH
pip install -r requirements.txt
```

### 4. Create Your Configuration

This tool is configured via  `config.json`. A template is provided.

1.  **Create your config file** by copying the example:
    ```BASH
    cp config.example.json config.json
    ```
2.  **Get your Discord Webhook URL:**
    - Go to your Discord Server Settings > Integrations > Webhooks > New Webhook.
    - Copy the Webhook URL.
3.  **Edit `config.json`** with a text editor and fill in your values:

    ```JSON
    {
      "discord_webhook_url": "PASTE_YOUR_WEBHOOK_URL_HERE",
      "asset_id": "bitcoin",
      "vs_currency": "usd",
      "check_interval_seconds": 60,
      "alert_threshold_percent": 1.0
    }
    ```
    - `asset_id`: The ID of the asset from [CoinGecko](https://www.coingecko.com/en/api) (e.g., `ethereum`, `cardano`).
    - `vs_currency`: The currency to quote the price in (e.g., `eur`, `jpy`).

---

## Usage

Once your environment is activated and your `config.json` is ready, simply run the main script:

```BASH
python main.py
```

The tool will initialize and start the monitoring loop. You can leave this terminal window open.

To stop the tool, press `Ctrl + C` in the terminal.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.