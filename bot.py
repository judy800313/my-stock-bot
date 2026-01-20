import yfinance as yf
import requests
import os
import time
import pandas as pd

line_token = os.environ.get('LINE_TOKEN')
user_id = os.environ.get('USER_ID')

def check_stock_and_notify():
    # 測試名單
    stock_list = ["1303.TW", "2330.TW", "2317.TW", "2454.TW", "2603.TW"]
    hit_stocks = []

    print(f"🚀 開始掃描，共 {len(stock_list)} 檔")

    for symbol in stock_list:
        try:
            # 使用更穩定的單筆下載
            df = yf.download(symbol, period="15d", interval="1d", progress=False)
            
            if df.empty or len(df) < 10:
                print(f"⚠️ {symbol}: 資料不足")
                continue

            # 💡 關鍵修正：處理新版 yfinance 可能出現的 MultiIndex
            if isinstance(df.columns, pd.MultiIndex):
                close_prices = df['Close'][symbol]
                high_prices = df['High'][symbol]
            else:
                close_prices = df['Close']
                high_prices = df['High']

            # 取得最新價格與前 7 日高點 (不含最後一筆)
            curr_price = float(close_prices.iloc[-1])
            # 取倒數第 2 筆到第 8 筆的最大值
            recent_high = float(high_prices.iloc[-8:-1].max())

            print(f"DEBUG: {symbol} 現價:{curr_price:.2f} / 7日高點:{recent_high:.2f}")

            if curr_price >= recent_high:
                magic_number = curr_price * 0.764
                hit_stocks.append(f"✅ {symbol} ({curr_price:.1f})\n   🎯 0.764: {magic_number:.1f}")
            
            time.sleep(1)
        except Exception as e:
            print(f"ERROR {symbol}: {str(e)}")

    if hit_stocks:
        send_to_line("🚩【新高報告】\n" + "\n".join(hit_stocks))
    else:
        send_to_line("掃描完畢，今日無人達標。")

def send_to_line(message):
    try:
        headers = {"Authorization": f"Bearer {line_token}", "Content-Type": "application/json"}
        payload = {"to": user_id, "messages": [{"type": "text", "text": message}]}
        requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
        print("訊息已傳送！")
    except:
        print("LINE 發送失敗")

if __name__ == "__main__":
    check_stock_and_notify()
