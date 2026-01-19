import yfinance as yf
import requests
import os

# 1. 從保險箱拿鑰匙
line_token = os.environ['LINE_TOKEN']
user_id = os.environ['USER_ID']

def get_all_tw_stocks():
    # 這裡列出你最想追蹤的清單，例如：
    # 0050成份股、熱門權值股或是你有興趣的代號
    # (因為全台股 1000 多檔跑起來會很久，我們先設定熱門的，你可以自己增加)
    return ["2330.TW", "2317.TW", "2454.TW", "2303.TW", "2881.TW", "2882.TW", "2603.TW", "0050.TW", "0056.TW"]

def check_stock_and_notify():
    stock_list = get_all_tw_stocks()
    hit_stocks = [] # 用來存符合條件的股票

    print(f"開始掃描 {len(stock_list)} 檔股票...")

    for symbol in stock_list:
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="1y") # 檢查過去一年的高點
            
            if len(df) < 20: continue # 資料太少就跳過

            current_price = df['Close'].iloc[-1]
            history_high = df['High'].iloc[:-1].max()

            # 判斷是否創新高
            if current_price >= history_high:
                magic_number = current_price * 0.764
                hit_stocks.append(f"📈 {symbol}\n   收盤：{current_price:.2f} → 目標：{magic_number:.2f}")
        except:
            print(f"{symbol} 抓取失敗")

    # 3. 整合訊息發送
    if hit_stocks:
        result_msg = "\n🌟【今日台股創新高名單】🌟\n" + "\n".join(hit_stocks)
    else:
        result_msg = "今日掃描清單中，沒有股票創新高。"

    # 發送 LINE
    headers = {"Authorization": f"Bearer {line_token}", "Content-Type": "application/json"}
    payload = {"to": user_id, "messages": [{"type": "text", "text": result_msg}]}
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)

if __name__ == "__main__":
    check_stock_and_notify()
