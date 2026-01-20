import yfinance as yf
import pandas as pd
import requests
import os
import sys
import time
import random

LINE_TOKEN = os.getenv('LINE_TOKEN')
USER_ID = os.getenv('USER_ID')

def send_line(msg):
    if not LINE_TOKEN or not USER_ID:
        print("❌ 錯誤：找不到 LINE_TOKEN 或 USER_ID")
        return
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": msg}]}
    try:
        r = requests.post(url, headers=headers, json=payload)
        print(f"📡 LINE 回傳: {r.status_code}")
    except Exception as e:
        print(f"❌ LINE 發送失敗: {e}")

def get_all_stocks():
    #   all_list = [
        "1101","1102","1210","1216","1301","1303","1319","1326","1402","1476",
        "1503","1504","1513","1519","1560","1590","1605","1717","1722","1723",
        "2002","2301","2303","2308","2317","2330","2337","2352","2357","2382",
        "2409","2412","2454","2603","2609","2610","2618","2881","2882","3008",
        "3037","3231","3481","4938","5871","6505","9904","2449","2451","3034",
        "3035","3711","6415","2344","2360","2376","2377","2379","2383","2385",
        "2408","2439","2458","3006","3017","3023","3036","3044","3189","3227",
        "3406","3443","3532","3533","3583","3653","3661","4739","4919","4958",
        "4961","4967","4968","5234","5269","5274","6176","6205","6213","6239",
        "6271","6414","6446","6472","6510","6515","6531","6533","6643","6669",
        "2605","2606","2615","2633","2634","2637","2801","2809","2812","2834",
        "2880","2883","2884","2885","2886","2887","2888","2889","2890","2891",
        "2892","2897","5876","5880","6005","9910","9914","9917","9921","9933",
        "9941","9945","1103","1304","1305","1308","1310","1312","1314","1434",
        "1440","1444","1477","1514","1522","1536","1707","1710","1711","1720",
        "1802","1904","2006","2014","2023","2027","2101","2103","2105","2106",
        "2201","2204","2206","2312","2313","2323","2324","2340","2345","2347",
        "2351","2353","2354","2355","2356","2367","2368","2371","2392","2393",
        "2401","2404","2419","2421","2455","2474","2480","2492","2498","2501",
        "2504","2511","2542","2548","2607","2707","2723","2727","2903","2912"
    ]
    return sorted(list(set([s + ".TW" for s in all_list])))

def run_scanner(group_idx):
    stocks = get_all_stocks()
    size = 20 # 降低每組數量，提高成功率
    start = (group_idx - 1) * size
    end = group_idx * size
    target = stocks[start:end]
    
    if not target: return

    print(f"🚀 啟動掃描第 {group_idx} 組 (抗封鎖模式)...")
    send_line(f"🤖 掃描開始 (第 {group_idx} 組)")

    hit_list = []
    
    # 建立一個偽裝的 Session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    for s in target:
        try:
            ticker = yf.Ticker(s, session=session)
            # 抓取歷史資料
            df = ticker.history(period="1mo")
            
            if df.empty or len(df) < 10:
                print(f"⚠️ {s} 無資料 (可能被擋)")
                continue
                
            curr = df['Close'].iloc[-1]
            past_high = df['High'].iloc[-8:-1].max()
            
            if curr >= past_high:
                hit_list.append(f"✅ {s}: {curr:.2f} (支撐: {curr*0.764:.2f})")
            
            print(f"🔎 已檢查 {s}")
            # 關鍵：加入隨機延遲，模仿真人操作
            time.sleep(random.uniform(2, 5)) 
            
        except Exception as e:
            print(f"❌ {s} 發生錯誤: {e}")
            time.sleep(10) # 報錯就停久一點

    if hit_list:
        send_line(f"🚩【符合條件】\n" + "\n".join(hit_list))
    else:
        send_line(f"💡 第 {group_idx} 組檢查完畢，今日無符合條件標的。")

if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_scanner(idx)
