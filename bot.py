import yfinance as yf
import requests
import os
import time

line_token = os.environ.get('LINE_TOKEN')
user_id = os.environ.get('USER_ID')

def check_stock_and_notify():
    # 我們先縮小範圍測試這 10 檔，包含 1303
    stock_list = ["1303.TW", "2317.TW", "2454.TW", "2330.TW", "2303.TW", "2881.TW", "2603.TW", "2382.TW", "3008.TW", "2409.TW"]
    
    hit_stocks = []
    print(f"🕵️ 啟動測試掃描，清單共 {len(stock_list)} 檔")

    for symbol in stock_list:
        try:
            # 💡 改用 download 並加入 threads=False 避免被擋
            data = yf.download(symbol, period="10d", interval="1d", progress=False, threads=False)
            
            if data.empty or len(data) < 5:
                print(f"⚠️ {symbol}: 抓不到資料，跳過")
                continue

            # 轉成浮點數避免格式錯誤
            # 注意：這裡使用 data.iloc[-1] 取得最後一筆
            current_price = float(data['Close'].iloc[-1])
            recent_high = float(data['High'].iloc[-7:-1].max())

            # 這是關鍵印出，請在 Actions 日誌看這行
            print(f"🔎 {symbol}: 現價 {current_price:.2f} | 7日高點 {recent_high:.2f}")

            if current_price >= recent_high:
                magic_number = current_price * 0.764
                hit_stocks.append(f"✅ {symbol} ({current_price:.1f})\n   🎯 0.764: {magic_number:.1f}")
            
            time.sleep(1) # 增加間隔，避免被 Yahoo 偵測為爬蟲
                
        except Exception as e:
            print(f"❌ {symbol} 發生錯誤: {e}")

    # 發送結果
    if hit_stocks:
        msg = "🚩【7日新高報告】\n" + "\n".join(hit_stocks)
        send_to_line(msg)
    else:
        send_to_line("掃描完畢，清單中無人符合 7 日新高。")

def send_to_line(message):
    headers = {"Authorization": f"Bearer {line_token}", "Content-Type": "application/json"}
    payload = {"to": user_id, "messages": [{"type": "text", "text": message}]}
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)

if __name__ == "__main__":
    check_stock_and_notify()
