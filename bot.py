import yfinance as yf
import requests
import os  # 👈 這是新增的，用來讀取保險箱裡的秘密

# --- 從 GitHub 的秘密保險箱領取寶藏 ---
line_token = os.environ['LINE_TOKEN']
user_id = os.environ['USER_ID']
stock_symbol = "2330.TW" 

def check_stock_and_notify():
    # 1. 讓機器人用眼睛看股價
    stock = yf.Ticker(stock_symbol)
    df = stock.history(period="2y") 
    
    # 檢查是否有資料
    if df.empty:
        print("抓不到資料喔！")
        return

    current_price = df['Close'].iloc[-1] 
    history_high = df['High'].iloc[:-1].max() 
    
    # 2. 機器人的腦袋判斷是否創新高
    if current_price >= history_high:
        magic_number = current_price * 0.764
        msg = f"\n🌟 股票 {stock_symbol} 創新高囉！\n今日收盤：{current_price:.2f}\n🎯 0.764 目標價：{magic_number:.2f}"
        
        # 3. 透過對講機傳給你
        headers = {
            "Authorization": f"Bearer {line_token}", 
            "Content-Type": "application/json"
        }
        payload = {
            "to": user_id, 
            "messages": [{"type": "text", "text": msg}]
        }
        requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
        print("訊息已傳送！")
    else:
        # 為了讓你知道機器人有在上班，沒創新高時我們讓他在 log 紀錄一下
        print(f"今天沒創新高。目前：{current_price:.2f}，高點：{history_high:.2f}")

# 執行
if __name__ == "__main__":
    check_stock_and_notify()
