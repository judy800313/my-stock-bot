import yfinance as yf
import pandas as pd
import requests
import os
import time

# ==========================================
# 1. 安全讀取：從 GitHub Secrets 抓取金鑰
# ==========================================
LINE_TOKEN = os.getenv('LINE_TOKEN')
USER_ID = os.getenv('USER_ID')

# ==========================================
# 2. 核心參數：定義 200 檔股票清單
# ==========================================
def get_stock_list():
    # 這裡列出關鍵股票，您可以依照此格式繼續增加代碼
    stocks = [
        "1101","1102","1210","1216","1301","1303","1319","1326","1402","1476",
        "1503","1504","1513","1519","1560","1590","1605","1717","1722","1723",
        "2002","2301","2303","2308","2317","2330","2337","2352","2357","2382",
        "2409","2412","2454","2603","2609","2610","2618","2881","2882","3008",
        "3037","3231","3481","4938","5871","6505","9904"
        # 提示：在此括號內加入更多代碼，記得用引號與逗號隔開
    ]
    # 自動補上 .TW 並去除重複
    return sorted(list(set([s + ".TW" for s in stocks])))

# ==========================================
# 3. 掃描與計算邏輯
# ==========================================
def run_scanner():
    target_stocks = get_stock_list()
    hit_list = []
    
    print(f"🕵️ 啟動雲端掃描任務，共計 {len(target_stocks)} 檔...")

    try:
        # 💡 使用批次下載：一次請求所有股票，防止 GitHub IP 被封鎖
        # 抓取 15 天資料以確保有足夠的 K 線計算 7 日高點
        all_data = yf.download(target_stocks, period="15d", group_by='ticker', progress=False)
        
        for symbol in target_stocks:
            try:
                # 取得該股 DataFrame 並移除無效值
                df = all_data[symbol].dropna()
                
                # 確保數據量足夠
                if len(df) < 10:
                    continue

                # 取得今日收盤價
                curr_price = float(df['Close'].iloc[-1])
                # 取得前 7 個交易日的「盤中最高點」基準 (不含今日)
                past_high_reference = float(df['High'].iloc[-8:-1].max())

                # 條件 1：今日收盤價 ≧ 過去 7 日最高點
                if curr_price >= past_high_reference:
                    # 條件 2：計算黃金分割支撐位 0.764
                    support_target = curr_price * 0.764
                    hit_list.append(f"✅ {symbol} ({curr_price:.1f})\n   🎯 支撐 0.764: {support_target:.1f}")
            
            except Exception as e:
                # 單一股票錯誤不中斷整體運行
                continue
                
    except Exception as e:
        print(f"❌ 批次下載發生嚴重錯誤: {e}")

    # ==========================================
    # 4. 發送結果 (分批發送避免 LINE 訊息過長)
    # ==========================================
    if hit_list:
        print(f"🎉 掃描完成，符合條件共 {len(hit_list)} 檔。")
        for i in range(0, len(hit_list), 15):
            chunk = hit_list[i:i+15]
            message = "🚩【每日台股新高追蹤報告】\n" + "----------------\n" + "\n".join(chunk)
            send_to_line(message)
    else:
        print("💡 今日掃描完畢，無股票符合 7 日新高條件。")

def send_to_line(msg):
    # 檢查是否有金鑰，防止 Secrets 沒設好導致程式崩潰
    if not LINE_TOKEN or not USER_ID:
        print("❌ 錯誤：未找到 LINE_TOKEN 或 USER_ID 環境變數。")
        return

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": msg}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"LINE 發送失敗: {response.text}")
    except Exception as e:
        print(f"發送請求時發生錯誤: {e}")

if __name__ == "__main__":
    # 稍微延遲執行，確保 GitHub 環境變數完全載入
    time.sleep(1)
    run_scanner()
