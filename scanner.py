import yfinance as yf
import requests
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 🔥 Stock List
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

        ret = float(((close_prices.iloc[-1] / close_prices.iloc[0]) - 1) * 100)

        results.append((stock.replace(".NS",""), round(ret, 2)))

    except:
        continue

# -------------------------------
# CLEAN + SORT
# -------------------------------
results = [x for x in results if isinstance(x[1], float)]
results = sorted(results, key=lambda x: x[1], reverse=True)[:10]

# -------------------------------
# LOAD OLD DATA
# -------------------------------
old_stocks = []

if os.path.exists("daily_rs.json"):
    try:
        with open("daily_rs.json", "r") as f:
            old_stocks = json.load(f)
    except:
        old_stocks = []

# -------------------------------
# TODAY DATA
# -------------------------------
today_stocks = [x[0] for x in results]

# -------------------------------
# NEW ENTRIES
# -------------------------------
new_entries = [stock for stock in today_stocks if stock not in old_stocks]

# -------------------------------
# RANK CHANGE TRACKER
# -------------------------------
rank_changes = []

if old_stocks:
    for i, stock in enumerate(today_stocks):
        if stock in old_stocks:
            old_rank = old_stocks.index(stock) + 1
            new_rank = i + 1

            if new_rank < old_rank:
                rank_changes.append(f"⬆ {stock}: {old_rank} → {new_rank}")
            elif new_rank > old_rank:
                rank_changes.append(f"⬇ {stock}: {old_rank} → {new_rank}")

# -------------------------------
# SAVE TODAY DATA
# -------------------------------
with open("daily_rs.json", "w") as f:
    json.dump(today_stocks, f)

# -------------------------------
# CREATE MESSAGE
# -------------------------------
message = "📊 RSM AI High Score Stocks\n\nTop 10 Today:\n\n"

if results:
    for stock, score in results:
        message += f"{stock} — {score}% 🚀\n"
else:
    message += "⚠️ No valid stocks found today\n"

# NEW ENTRIES
if new_entries:
    message += "\n➕ NEW ENTRIES\n"
    for stock in new_entries:
        message += f"{stock}\n"

# RANK CHANGES
if rank_changes:
    message += "\n📈 RANK CHANGES\n"
    for change in rank_changes:
        message += change + "\n"

# -------------------------------
# SEND TELEGRAM
# -------------------------------
try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})
except:
    pass
