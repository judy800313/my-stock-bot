import yfinance as yf
import requests
import os
import time
import pandas as pd

line_token = os.environ.get('LINE_TOKEN')
user_id = os.environ.get('USER_ID')

def check_stock_and_notify():
    # 測試清單：確保 1303 在最前面
    stock_list = ["1303.TW", "2330.TW", "2317.TW", "2454.TW", "2308.TW", "2881.TW", "2882.TW", "2303.TW", "2891.TW", "1216.TW"]
    
    hit_stocks = []
    print(f"🚀 開始執行 GitHub 端的正式掃描...")

    for symbol in stock_list:
        try:
            # 強制下載最新資料
            data = yf.download(symbol, period="10d", progress=False)
            if data.empty: continue

            # 取得最新價格與前 7 日高點
            today_price = float(data['Close'].iloc[-1])
            recent_high = float(data['High'].iloc[-8:-1].max())

            print(f"分析 {symbol}: 目前 {today_price} / 高點 {recent_high}")

            if today_price >= recent_high:
                magic_number = today_price * 0.764
                hit_stocks.append(f"✅ {symbol} ({today_price:.1f})\n   🎯 0.764: {magic_number:.1f}")
        except Exception as e:
            print(f"❌ {symbol} 錯誤: {e}")

    if hit_stocks:
        msg = "🚩【GitHub 直送報告】\n" + "\n".join(hit_stocks)
        send_to_line(msg)
    else:
        send_to_line("GitHub 執行完畢，無人創新高。")

def send_to_line(message):
    headers = {"Authorization": f"Bearer {line_token}", "Content-Type": "application/json"}
    payload = {"to": user_id, "messages": [{"type": "text", "text": message}]}
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)

if __name__ == "__main__":
    check_stock_and_notify()
