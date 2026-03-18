import yfinance as yf
import pandas as pd
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Nifty 500 sample list (can expand later)
stocks = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "SBIN.NS","LT.NS","ITC.NS","AXISBANK.NS","HCLTECH.NS"
]

# Nifty 500 Index (proxy)
nifty = yf.download("^CRSLDX", period="3mo", progress=False)

message = "📊 RSM AI High Score Stocks (Top 10)\n\n"

results = []

for stock in stocks:
    try:
        data = yf.download(stock, period="3mo", progress=False)

        if data.empty:
            continue

        rs = (data['Close'] / nifty['Close']) * 100
        score = ((rs.iloc[-1] / rs.iloc[0]) - 1) * 100

        results.append((stock.replace(".NS",""), round(score,2)))

    except:
        continue

# Sort by strength
results = sorted(results, key=lambda x: x[1], reverse=True)

top10 = results[:10]

for stock, score in top10:
    message += f"{stock} — {score}% 🚀\n"

# Send Telegram message
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, data={"chat_id": CHAT_ID, "text": message})

print(message)
