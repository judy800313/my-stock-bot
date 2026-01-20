import yfinance as yf
import pandas as pd
import requests
import os
import sys

# 從 GitHub Secrets 讀取設定
LINE_TOKEN = os.getenv('LINE_TOKEN')
USER_ID = os.getenv('USER_ID')

def send_line(msg):
    """發送訊息到 LINE"""
    if not LINE_TOKEN or not USER_ID:
        print("❌ 錯誤：找不到 LINE_TOKEN 或 USER_ID")
        return
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": msg}]}
    try:
        r = requests.post(url, headers=headers, json=payload)
        print(f"📡 LINE 回傳狀態碼: {r.status_code}")
    except Exception as e:
        print(f"❌ LINE 發送失敗: {e}")

def get_all_stocks():
    """定義 200 檔股票清單"""
    all_list = [
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

def main():
    try:
        group_idx = int(sys.argv[1])
    except:
        group_idx = 1
    
    stocks = get_all_stocks()
    size = 50
    start = (group_idx - 1) * size
    end = group_idx * size
    target = stocks[start:end]
    
    if not target:
        print(f"第 {group_idx} 組無股票")
        return

    print(f"🚀 開始掃描第 {group_idx} 組...")
    send_line(f"🤖 機器人啟動：正在掃描第 {group_idx} 組股票...")

    try:
        # 批量下載數據
        data = yf.download(target, period="15d", threads=True, progress=False)
        hit_list = []
        
        for s in target:
            try:
                # 正確提取下載後的資料
                if isinstance(data.columns, pd.MultiIndex):
                    df_close = data['Close'][s].dropna()
                    df_high = data['High'][s].dropna()
                else:
                    df_close = data['Close'].dropna()
                    df_high = data['High'].dropna()

                if len(df_close) < 10: continue
                
                curr = df_close.iloc[-1]
                past_high = df_high.iloc[-8:-1].max()
                
                if curr >= past_high:
                    hit_list.append(f"✅ {s}: {curr:.2f} (支撐: {curr*0.764:.2f})")
            except:
                continue

        if hit_list:
            send_line(f"🚩【第 {group_idx} 組報告】\n" + "\n".join(hit_list))
        else:
            send_line(f"💡 第 {group_idx} 組掃描完畢，目前無標的。")

    except Exception as e:
        print(f"❌ 下載錯誤: {e}")
        send_line(f"⚠️ 第 {group_idx} 組運行失敗: {e}")

if __name__ == "__main__":
    main()
