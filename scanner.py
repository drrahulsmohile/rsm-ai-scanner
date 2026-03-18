import yfinance as yf
import pandas as pd
import requests
import os

# Telegram credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Stock list (can expand later)
stocks = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "SBIN.NS","LT.NS","ITC.NS","AXISBANK.NS","HCLTECH.NS"
]

results = []

for stock in stocks:
    try:
        data = yf.download(stock, period="3mo", progress=False)

        # Safety check
        if data is None or len(data) < 20:
            continue

        # Momentum calculation (last close vs 20-day ago)
        latest_price = data["Close"].iloc[-1]
        old_price = data["Close"].iloc[-20]

        if old_price == 0:
            continue

        percent_change = ((latest_price - old_price) / old_price) * 100

        results.append((stock, percent_change))

    except Exception as e:
        print(f"Error in {stock}: {e}")

# Remove invalid values
results = [r for r in results if r[1] is not None]

# Sort descending
results = sorted(results, key=lambda x: float(x[1]), reverse=True)

# Top 10
top_10 = results[:10]

# Format message
message = "📊 RSM AI High Score Stocks\n\nTop 10 Today:\n\n"

for stock, score in top_10:
    message += f"{stock} — {round(score,2)}% 🚀\n"

# Send to Telegram
if BOT_TOKEN and CHAT_ID:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)
else:
    print("Telegram credentials missing")

# Print for logs
print(message)



