import pandas as pd
import requests
import os
import sys
import time

# 從 GitHub Secrets 讀取設定
LINE_TOKEN = os.getenv('LINE_TOKEN')
USER_ID = os.getenv('USER_ID')
FINMIND_TOKEN = os.getenv('FINMIND_TOKEN')

def send_line(msg):
    """發送訊息到 LINE"""
    if not LINE_TOKEN or not USER_ID:
        print("❌ 錯誤：找不到 LINE 設定")
        return
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": msg}]}
    try:
        r = requests.post(url, headers=headers, json=payload)
        print(f"📡 LINE 回傳: {r.status_code}")
    except Exception as e:
        print(f"❌ LINE 發送失敗: {e}")

def get_stock_data(stock_id):
    """從 FinMind 抓取資料"""
    url = "https://api.finmindtrade.com/api/v4/data"
    # 抓取最近 30 天的資料
    start_date = (pd.Timestamp.now() - pd.Timedelta(days=30)).strftime('%Y-%m-%d')
    
    parameter = {
        "dataset": "TaiwanStockPrice",
        "data_id": stock_id,
        "start_date": start_date,
        "token": FINMIND_TOKEN,
    }
    try:
        r = requests.get(url, params=parameter, timeout=15)
        data = r.json()
        if data.get('msg') == 'success' and data.get('data'):
            return pd.DataFrame(data['data'])
    except:
        pass
    return pd.DataFrame()

def main():
    # 你的 200 檔股票清單
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

    try:
        group_idx = int(sys.argv[1])
    except:
        group_idx = 1

    size = 50 # 每一組跑 50 檔
    target = all_list[(group_idx-1)*size : group_idx*size]
    
    if not target: return

    print(f"🚀 FinMind 掃描啟動：第 {group_idx} 組")
    send_line(f"🤖 機器人切換 FinMind 成功！開始掃描第 {group_idx} 組...")

    hit_list = []
    for s in target:
        try:
            df = get_stock_data(s)
            if df.empty or len(df) < 10:
                continue
            
            # FinMind 欄位：close 為收盤價，max 為最高價
            curr = df['close'].iloc[-1]
            past_high = df['max'].iloc[-8:-1].max()
            
            if curr >= past_high:
                hit_list.append(f"✅ {s}: {curr:.2f} (支撐: {curr*0.764:.2f})")
            
            print(f"🔎 掃描完成: {s}")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ {s} 發生錯誤: {e}")

    if hit_list:
        send_line(f"🚩【第 {group_idx} 組篩選報告】\n" + "\n".join(hit_list))
    else:
        send_line(f"💡 第 {group_idx} 組掃描完畢，今日無符合條件標的。")

if __name__ == "__main__":
    main()
