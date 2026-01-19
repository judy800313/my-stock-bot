import yfinance as yf
import requests
import os
import time
import pandas as pd

# 讀取金鑰
line_token = os.environ.get('LINE_TOKEN')
user_id = os.environ.get('USER_ID')

def get_tw_top_500():
    # 這裡放 500 檔，並且把 1303 放在最前面確保優先執行
    stocks = ["1303","3711","2317","2454","2308","2412","2881","2882","2303","2891","2330"]
    # ... (請自行加入之前的 500 檔代號)
    return [s + ".TW" for s in stocks]

def check_stock_and_notify():
    stock_list = get_tw_top_500()
    hit_stocks = []
    
    print(f"🚀 正式啟動 500 檔掃描...")

    for i, symbol in enumerate(stock_list):
        try:
            # 1. 抓取資料
            stock = yf.Ticker(symbol)
            df = stock.history(period="15d") # 多抓一點確保計算準確
            
            if df.empty or len(df) < 10: continue

            # 2. 判定價格 (今日收盤 vs 前6日最高)
            current_price = df['Close'].iloc[-1]
            recent_high = df['High'].iloc[-8:-1].max()

            # 3. 如果是 1303，強制印出 debug 資訊
            if "1303" in symbol:
                print(f"DEBUG 1303: 今日收盤={current_price}, 前7日高點={recent_high}")

            if current_price >= recent_high:
                magic_number = current_price * 0.764
                hit_stocks.append(f"✅ {symbol} ({current_price:.1f})\n   🎯 0.764: {magic_number:.1f}")
            
            # 避免被 Yahoo 擋
            if i % 30 == 0: time.sleep(1)
                
        except Exception as e:
            print(f"❌ {symbol} 出錯: {e}")

    # 4. 發送 LINE
    if hit_stocks:
        header = f"🚩【7日新高報告】\n符合數：{len(hit_stocks)} 檔\n"
        for i in range(0, len(hit_stocks), 15):
            chunk = hit_stocks[i : i + 15]
            send_to_line(header + "--------------\n" + "\n".join(chunk))
    else:
        send_to_line("今日掃描完成，無人創新高。")

def send_to_line(message):
    headers = {"Authorization": f"Bearer {line_token}", "Content-Type": "application/json"}
    payload = {"to": user_id, "messages": [{"type": "text", "text": message}]}
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)

if __name__ == "__main__":
    check_stock_and_notify()
