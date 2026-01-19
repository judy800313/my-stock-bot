import yfinance as yf
import requests
import os
import time

line_token = os.environ.get('LINE_TOKEN')
user_id = os.environ.get('USER_ID')

def check_stock_and_notify():
    # 測試名單，確保 1303 在裡面
    stock_list = ["1303.TW", "2330.TW", "2317.TW", "2454.TW", "2603.TW"]
    hit_stocks = []

    for symbol in stock_list:
        try:
            # 使用最新版 yfinance 的下載方式
            df = yf.download(symbol, period="10d", interval="1d", progress=False)
            
            if df.empty or len(df) < 5:
                print(f"{symbol} 無資料")
                continue

            # 新版 yfinance 抓回來的 Close 可能是 Series
            curr_price = float(df['Close'].iloc[-1])
            recent_high = float(df['High'].iloc[-8:-1].max())

            print(f"DEBUG: {symbol} 現價:{curr_price} / 高點:{recent_high}")

            if curr_price >= recent_high:
                magic_number = curr_price * 0.764
                hit_stocks.append(f"✅ {symbol} ({curr_price:.1f})\n   🎯 0.764: {magic_number:.1f}")
            
            time.sleep(1)
        except Exception as e:
            print(f"ERROR {symbol}: {e}")

    if hit_stocks:
        send_to_line("🚩【新高報告】\n" + "\n".join(hit_stocks))
    else:
        send_to_line("掃描完畢，今日無人達標。")

def send_to_line(message):
    headers = {"Authorization": f"Bearer {line_token}", "Content-Type": "application/json"}
    payload = {"to": user_id, "messages": [{"type": "text", "text": message}]}
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print("訊息已傳送！")

if __name__ == "__main__":
    check_stock_and_notify()
