import yfinance as yf
import requests
import os
import time
import pandas as pd
from datetime import datetime
import pytz

# =========================================================
# USER CONFIG
# =========================================================

MODE = "INTRADAY"
# INTRADAY : 今日「盤中曾」創 7 日新高（使用 day_high）
# CLOSE    : 目前價格站上 7 日新高（使用 last_price）

LOOKBACK_DAYS = 7
TZ = pytz.timezone("Asia/Taipei")

LINE_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("USER_ID")

# =========================================================
# STOCK LIST
# =========================================================

def get_tw_top_500():
    stocks = [
        "2330","2317","2454","2308","2412","2881","2882","2303","2891","3711",
        "2886","1301","1303","2408","1216","2884","2892","2002","2382","2885",
        "2101"
    ]
    return [s + ".TW" for s in stocks]

# =========================================================
# CORE LOGIC
# =========================================================

def detect_breakout(stock, df):
    fi = stock.fast_info

    last_price = fi.get("last_price")
    day_high = fi.get("day_high")

    if last_price is None:
        return None

    today = datetime.now(TZ).date()
    last_bar = df.index[-1].date()

    if last_bar >= today:
        recent_high = df["High"].iloc[-LOOKBACK_DAYS-1:-1].max()
    else:
        recent_high = df["High"].iloc[-LOOKBACK_DAYS:].max()

    if MODE == "INTRADAY":
        if day_high is None:
            return None
        hit = day_high >= recent_high
        trigger_price = day_high

    elif MODE == "CLOSE":
        hit = last_price >= recent_high
        trigger_price = last_price

    else:
        raise ValueError("MODE must be INTRADAY or CLOSE")

    if not hit:
        return None

    return {
        "symbol": stock.ticker,
        "trigger": trigger_price,
        "recent_high": recent_high,
        "magic": trigger_price * 0.764
    }

# =========================================================
# MAIN
# =========================================================

def run():
    stock_list = get_tw_top_500()
    hits = []

    print(f"🔍 Scanning {len(stock_list)} stocks | MODE={MODE}")

    for i, symbol in enumerate(stock_list):
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="10d")

            if len(df) < LOOKBACK_DAYS:
                continue

            result = detect_breakout(stock, df)
            if result:
                hits.append(
                    f"✅ {result['symbol']}\n"
                    f"   ▶ Trigger: {result['trigger']:.2f}\n"
                    f"   ⛰ Prev High: {result['recent_high']:.2f}\n"
                    f"   🎯 0.764: {result['magic']:.2f}"
                )

            if i % 25 == 0:
                time.sleep(0.5)

        except Exception as e:
            print(f"❌ {symbol} skipped: {e}")

    notify(hits, len(stock_list))

# =========================================================
# LINE NOTIFY
# =========================================================

def notify(hits, total):
    if not LINE_TOKEN or not USER_ID:
        print("⚠️ LINE_TOKEN or USER_ID not set")
        return

    if not hits:
        send_line("📭 Scan completed. No 7-day high detected.")
        return

    header = (
        f"🚩 7-Day High Alert\n"
        f"MODE: {MODE}\n"
        f"Scanned: {total}\n"
        f"Hits: {len(hits)}\n"
        f"----------------------"
    )

    for i in range(0, len(hits), 10):
        msg = header + "\n" + "\n\n".join(hits[i:i+10])
        send_line(msg)
        time.sleep(1)

def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, json=payload, timeout=10)

# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":
    run()
