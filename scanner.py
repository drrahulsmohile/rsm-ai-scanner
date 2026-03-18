import yfinance as yf
import pandas as pd
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

stocks = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "SBIN.NS","LT.NS","ITC.NS","AXISBANK.NS","HCLTECH.NS"
]

results = []

for stock in stocks:
    try:
        data = yf.download(stock, period="3mo", progress=False)

        # Fix MultiIndex issue
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.dropna()

        if len(data) < 20:
            print(f"{stock} skipped (less data)")
            continue

        close = data["Close"]

        latest_price = float(close.iloc[-1])
        old_price = float(close.iloc[-20])

        if old_price == 0:
            continue

        percent_change = ((latest_price - old_price) / old_price) * 100

        print(f"{stock}: {percent_change}")

        results.append((stock, percent_change))

    except Exception as e:
        print(f"Error in {stock}: {e}")

print("Final Results:", results)

# Sorting
results = sorted(results, key=lambda x: x[1], reverse=True)

top_10 = results[:10]

# Message
if len(top_10) == 0:
    message = "⚠️ No valid stocks found today"
else:
    message = "📊 RSM AI High Score Stocks\n\nTop 10 Today:\n\n"
    for stock, score in top_10:
        message += f"{stock} — {round(score,2)}% 🚀\n"

# Telegram
if BOT_TOKEN and CHAT_ID:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=payload)
    print(response.text)

print(message)
