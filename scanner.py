import yfinance as yf
import pandas as pd
import requests
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# File to store yesterday data
file_name = "portfolio.json"

# Load old data
if os.path.exists(file_name):
    with open(file_name, "r") as f:
        old_list = json.load(f)
else:
    old_list = []

# Stock universe (you can later expand to Nifty 500)
stocks = [
    "WAAREEENER.NS","OLECTRA.NS","JBMA.NS","MMTC.NS","NTPCGREEN.NS",
    "CHENNPETRO.NS","ADANIPOWER.NS","DCMSHRIRAM.NS","PREMIERENE.NS","JPPOWER.NS"
]

results = []

for stock in stocks:
    try:
        data = yf.download(stock, period="1mo", progress=False)

        # Fix multi index
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.dropna()

        if len(data) < 6:
            continue

        close = data["Close"]

        latest = float(close.iloc[-1])
        old = float(close.iloc[-6])

        score = ((latest - old) / old) * 100

        results.append((stock.replace(".NS",""), score))

    except:
        continue

# Sort
results = sorted(results, key=lambda x: x[1], reverse=True)

top10 = results[:10]

new_list = [x[0] for x in top10]

# ----------------------------
# COMPARISON LOGIC
# ----------------------------
added = list(set(new_list) - set(old_list))
removed = list(set(old_list) - set(new_list))
stable = list(set(new_list).intersection(set(old_list)))

# ----------------------------
# MESSAGE FORMAT
# ----------------------------
message = "📊 RSM AI High Score Stocks\n\nTop 10 Today:\n\n"

for stock, score in top10:
    message += f"{stock} — {round(score,2)}% 🚀\n"

# NEW ENTRIES
if added:
    message += "\n➕ NEW ENTRIES\n"
    for s in added:
        message += f"{s}\n"

# REMOVED
if removed:
    message += "\n➖ REMOVED\n"
    for s in removed:
        message += f"{s}\n"

# STABLE
if stable:
    message += "\n🔁 STABLE\n"
    for s in stable:
        message += f"{s}\n"

# ----------------------------
# SEND TELEGRAM
# ----------------------------
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, data={"chat_id": CHAT_ID, "text": message})

print(message)

# ----------------------------
# SAVE TODAY DATA
# ----------------------------
with open(file_name, "w") as f:
    json.dump(new_list, f)
