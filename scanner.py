import yfinance as yf
import pandas as pd
import requests
import os
import json
import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Files
daily_file = "daily_rs.json"
weekly_file = "weekly_portfolio.json"

# Stock universe (can expand later)
stocks = [
    "WAAREEENER.NS","OLECTRA.NS","JBMA.NS","MMTC.NS","NTPCGREEN.NS",
    "CHENNPETRO.NS","ADANIPOWER.NS","DCMSHRIRAM.NS","PREMIERENE.NS","JPPOWER.NS"
]

# ---------------------------
# LOAD OLD DATA
# ---------------------------
def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return []

old_daily = load_data(daily_file)
old_weekly = load_data(weekly_file)

results = []

# ---------------------------
# FETCH DATA
# ---------------------------
for stock in stocks:
    try:
        data = yf.download(stock, period="1mo", progress=False)

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

# ---------------------------
# SORT
# ---------------------------
results = sorted(results, key=lambda x: x[1], reverse=True)

top10 = results[:10]
top5 = results[:5]

today = datetime.datetime.now().weekday()

# ---------------------------
# DAILY MESSAGE
# ---------------------------
daily_list = [x[0] for x in top10]

added = list(set(daily_list) - set(old_daily))
removed = list(set(old_daily) - set(daily_list))
stable = list(set(daily_list).intersection(set(old_daily)))

daily_msg = "📊 RSM AI High Score Stocks\n\nTop 10 Today:\n\n"

for stock, score in top10:
    daily_msg += f"{stock} — {round(score,2)}% 🚀\n"

if added:
    daily_msg += "\n➕ NEW ENTRIES\n"
    for s in added:
        daily_msg += f"{s}\n"

if removed:
    daily_msg += "\n➖ REMOVED\n"
    for s in removed:
        daily_msg += f"{s}\n"

if stable:
    daily_msg += "\n🔁 STABLE\n"
    for s in stable:
        daily_msg += f"{s}\n"

# ---------------------------
# WEEKLY MESSAGE (FRIDAY ONLY)
# ---------------------------
weekly_msg = ""

if today == 4:  # Friday

    weekly_list = [x[0] for x in top5]

    add_w = list(set(weekly_list) - set(old_weekly))
    remove_w = list(set(old_weekly) - set(weekly_list))
    hold_w = list(set(weekly_list).intersection(set(old_weekly)))

    weekly_msg = "\n\n📊 RSM WEEKLY PORTFOLIO\n\nSelected Stocks:\n\n"

    for stock in weekly_list:
        weekly_msg += f"{stock}\n"

    if add_w:
        weekly_msg += "\n➕ ADD\n"
        for s in add_w:
            weekly_msg += f"{s}\n"

    if remove_w:
        weekly_msg += "\n➖ REMOVE\n"
        for s in remove_w:
            weekly_msg += f"{s}\n"

    if hold_w:
        weekly_msg += "\n🔁 HOLD\n"
        for s in hold_w:
            weekly_msg += f"{s}\n"

# ---------------------------
# FINAL MESSAGE
# ---------------------------
final_message = daily_msg + weekly_msg

# ---------------------------
# TELEGRAM
# ---------------------------
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, data={"chat_id": CHAT_ID, "text": final_message})

print(final_message)

# ---------------------------
# SAVE DATA
# ---------------------------
with open(daily_file, "w") as f:
    json.dump(daily_list, f)

if today == 4:
    with open(weekly_file, "w") as f:
        json.dump([x[0] for x in top5], f)
