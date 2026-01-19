import yfinance as yf
import requests
import os
import time

# 讀取金鑰
line_token = os.environ.get('LINE_TOKEN')
user_id = os.environ.get('USER_ID')

def check_stock_and_notify():
    # 這是測試清單，請確認 1303 在 2330 前面
    # 只要這個成功，我們就可以放心地貼入 500 檔清單
    stock_list = ["1303.TW", "2330.TW", "2317.TW", "2454.TW", "2603.TW", "2881.TW", "2303.TW"]
    
    hit_stocks = []
    print(f"🚀 啟動修復版掃描，清單共 {len(stock_list)} 檔")

    for symbol in stock_list:
        try:
            # 💡 使用 Ticker 模式搭配 history，這是最穩定的單筆抓取法
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="10d")
            
            if df.empty or len(df) < 8:
                print(f"⚠️ {symbol}: 抓不到足夠歷史資料")
                continue

            # 💡 關鍵修正：強制展開資料，避免 MultiIndex 抓錯
            # 取得最後一筆收盤價
            today_price = float(df['Close'].iloc[-1])
            # 取得「前 7 天」的最高價（排除今天最後一筆）
            recent_high = float(df['High'].iloc[-8:-1].max())

            # 在 Log 印出每一檔的判斷過程，讓我們監控
            print(f"分析 {symbol}: 今日收盤 {today_price:.2f} | 7日高點 {recent_high:.2f}")

            if today_price >= recent_high:
                magic_number = today_price * 0.764
                hit_stocks.append(f"✅ {symbol} ({today_price:.1f})\n   🎯 0.764: {magic_number:.1f}")
            
            # 稍微休息，避免被 Yahoo 擋
            time.sleep(1)
                
        except Exception as e:
            print(f"❌ {symbol} 發生錯誤: {e}")

    # 發送結果
    if hit_stocks:
        msg = "🚩【7日新高報告 - 正式修復】\n" + "\n".join(hit_stocks)
        send_to_line(msg)
    else:
        send_to_line("掃描完畢，無人符合 7 日新高。")

def send_to_line(message):
    headers = {"Authorization": f"Bearer {line_token}", "Content-Type": "application/json"}
    payload = {"to": user_id, "messages": [{"type": "text", "text": message}]}
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)

if __name__ == "__main__":
    check_stock_and_notify()
