import yfinance as yf
import pandas as pd
import requests
import os
import time

# 讀取 Secrets
LINE_TOKEN = os.getenv('LINE_TOKEN')
USER_ID = os.getenv('USER_ID')

def get_stock_list():
    # 這是您的掃描清單
    stocks = [
        "1101","1102","1210","1216","1301","1303","1319","1326","1402","1476",
        "1503","1504","1513","1519","1560","1590","1605","1717","1722","1723",
        "2002","2301","2303","2308","2317","2330","2337","2352","2357","2382",
        "2409","2412","2454","2603","2609","2610","2618","2881","2882","3008",
        "3037","3231","3481","4938","5871","6505","9904"
    ]
    return sorted(list(set([s + ".TW" for s in stocks])))

def run_scanner():
    target_stocks = get_stock_list()
    hit_list = []
    
    # 這是關鍵的 Debug 訊息，如果在 Log 看到這行，代表新代碼生效了！
    print(f"🔥 [NEW CODE] 正在掃描 {len(target_stocks)} 檔股票...")

    try:
        # 使用批次下載
        all_data = yf.download(target_stocks, period="15d", group_by='ticker', progress=False)
        
        for symbol in target_stocks:
            try:
                df = all_data[symbol].dropna()
                if len(df) < 10: continue

                curr_price = float(df['Close'].iloc[-1])
                past_high = float(df['High'].iloc[-8:-1].max())

                if curr_price >= past_high:
                    support = curr_price * 0.764
                    hit_list.append(f"✅ {symbol} ({curr_price:.1f})\n   🎯 支撐 0.764: {support:.1f}")
            except:
                continue
                
    except Exception as e:
        print(f"❌ 下載出錯: {e}")

    if hit_list:
        print(f"🎉 發現 {len(hit_list)} 檔符合條件！")
        for i in range(0, len(hit_list), 15):
            send_to_line("🚩【台股新高報告】\n----------------\n" + "\n".join(hit_list[i:i+15]))
    else:
        print("💡 今日掃描完畢，無股票符合條件。")

def send_to_line(msg):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": msg}]}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    run_scanner()
