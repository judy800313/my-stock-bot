import yfinance as yf
import pandas as pd
import requests
import os
import time
import sys

LINE_TOKEN = os.getenv('LINE_TOKEN')
USER_ID = os.getenv('USER_ID')

def get_all_stocks():
    # 這裡放你全部的 90 檔或更多股票
    all_list = [
        "1101","1102","1210","1216","1301","1303","1319","1326","1402","1476",
        "1503","1504","1513","1519","1560","1590","1605","1717","1722","1723",
        "2002","2301","2303","2308","2317","2330","2337","2352","2357","2382",
        "2409","2412","2454","2603","2609","2610","2618","2881","2882","3008",
        "3037","3231","3481","4938","5871","6505","9904" 
        # ... 您可以繼續往後加到 90 檔
    ]
    return sorted(list(set([s + ".TW" for s in all_list])))

def run_scanner(group_idx):
    all_stocks = get_all_stocks()
    
    # 分組邏輯：每組 45 檔
    start = (group_idx - 1) * 45
    end = group_idx * 45
    target_stocks = all_stocks[start:end]
    
    if not target_stocks:
        print("💡 此組別無股票。")
        return

    hit_list = []
    print(f"🔥 [分流掃描] 第 {group_idx} 組，正在掃描 {len(target_stocks)} 檔股票...")

    for symbol in target_stocks:
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="15d")
            if len(df) < 10: continue

            curr_price = float(df['Close'].iloc[-1])
            past_high = float(df['High'].iloc[-8:-1].max())

            if curr_price >= past_high:
                support = curr_price * 0.764
                hit_list.append(f"✅ {symbol} ({curr_price:.2f})\n   🎯 支撐 0.764: {support:.2f}")
            time.sleep(0.8) # 稍微慢一點點更安全
        except Exception as e:
            print(f"⚠️ {symbol} 跳過: {e}")

    if hit_list:
        send_to_line(f"🚩【台股報告-第{group_idx}組】\n----------------\n" + "\n".join(hit_list))
    else:
        print(f"💡 第 {group_idx} 組掃描完畢，無符合條件股票。")

def send_to_line(msg):
    if not LINE_TOKEN: return
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": msg}]}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    # 從指令接收組別，預設為第 1 組
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_scanner(idx)
