import yfinance as yf
import requests
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 🔥 Stock List (you can expand later)
stocks = [
    "WAAREEENER.NS","OLECTRA.NS","JBMA.NS","MMTC.NS",
    "NTPCGREEN.NS","CHENNPETRO.NS","ADANIPOWER.NS",
    "DCMSHRIRAM.NS","PREMIERENE.NS","JPPOWER.NS"
]

results = []

# -------------------------------
# FETCH DATA SAFELY
# -------------------------------
for stock in stocks:
    try:
        data = yf.download(stock, period="5d", progress=False)

        if data.empty:
            continue

        close_prices = data['Close'].dropna()

        if len(close_prices) < 2:
            continue

        ret = ((close_prices.iloc[-1] / close_prices.iloc[0]) - 1) * 100

        results.append((stock.replace(".NS",""), round(ret, 2)))

    except Exception as e:
        continue

# -------------------------------
# SORT TOP 10
# -------------------------------
results = sorted(results, key=lambda x: x[1], reverse=True)[:10]

# -------------------------------
# LOAD YESTERDAY DATA
# -------------------------------
old_stocks = []

if os.path.exists("daily_rs.json"):
    try:
        with open("daily_rs.json", "r") as f:
            old_stocks = json.load(f)
    except:
        old_stocks = []

# -------------------------------
# FIND NEW ENTRIES
# -------------------------------
today_stocks = [x[0] for x in results]

new_entries = [stock for stock in today_stocks if stock not in old_stocks]

# -------------------------------
# SAVE TODAY DATA
# -------------------------------
with open("daily_rs.json", "w") as f:
    json.dump(today_stocks, f)

# -------------------------------
# CREATE TELEGRAM MESSAGE
# -------------------------------
message = "📊 RSM AI High Score Stocks\n\nTop 10 Today:\n\n"

if results:
    for stock, score in results:
        message += f"{stock} — {score}% 🚀\n"
else:
    message += "⚠️ No valid stocks found today\n"

# Add New Entries Section
if new_entries:
    message += "\n➕ NEW ENTRIES\n"
    for stock in new_entries:
        message += f"{stock}\n"

# -------------------------------
# SEND TELEGRAM MESSAGE
# -------------------------------
try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})
except:
    pass
