def run_scanner(group_idx):
    all_stocks = get_all_stocks()
    size = 50 
    start = (group_idx - 1) * size
    end = group_idx * size
    target_stocks = all_stocks[start:end]
    
    if not target_stocks: return

    hit_list = []
    print(f"🚀 [抗封鎖掃描] 第 {group_idx} 組 ({len(target_stocks)} 檔)...")

    # --- 關鍵改動：增加請求偽裝 ---
    for symbol in target_stocks:
        try:
            # 增加 proxy 參數或更換抓取方式
            stock = yf.Ticker(symbol)
            # 使用 fast_info 或是調整 history 參數
            df = stock.history(period="10d", interval="1d", proxy=None) 
            
            if df.empty or len(df) < 5:
                # 如果被鎖定，嘗試換一種方式
                time.sleep(1.5)
                continue

            curr_price = float(df['Close'].iloc[-1])
            past_high = float(df['High'].iloc[-8:-1].max())

            if curr_price >= past_high:
                support = curr_price * 0.764
                hit_list.append(f"✅ {symbol} ({curr_price:.2f})\n   🎯 支撐 0.764: {support:.2f}")
            
            # 延長間隔時間，讓 Yahoo 覺得你不是機器人
            time.sleep(1.2) 
            
        except Exception as e:
            if "Rate limited" in str(e):
                print(f"🛑 觸發限制，暫停 5 秒...")
                time.sleep(5)
            print(f"⚠️ {symbol} 跳過: {e}")

    if hit_list:
        send_to_line(f"🚩【台股報告-第 {group_idx} 組】\n----------------\n" + "\n".join(hit_list))
    else:
        # 強制發送一則掃描完畢的訊息，確認連線是通的
        send_to_line(f"💡 第 {group_idx} 組掃描完畢，今日無達標股票。")
