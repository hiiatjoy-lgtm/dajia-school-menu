import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def direct_test():
    # ⚠️ 這裡我們直接塞入大甲國小「115年6月菜單」子網頁的真正公開網址
    # 如果未來要換月份，直接改這個網址最快、最不會出錯！
    target_url = "https://sites.google.com/tcps.tc.edu.tw/lunch/115%E5%B9%B46%E6%9C%A8%E8%8F%9C%E5%96%AE"
    
    file_keyword = "聯引"
    
    print(f"🚀 [直攻實驗] 正在讀取 6 月份專屬網頁: {target_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(target_url, headers=headers)
        print(f"📡 網頁連線狀態碼: {res.status_code} (200 代表成功讀取)")
        
        if res.status_code != 200:
            print("❌ 連線失敗，可能學校調整了網址。")
            return
            
        # 抓取原始碼中所有的 Google Drive / Sheets ID
        content = res.text
        drive_ids = re.findall(r'https://drive\.google\.com/file/d/([a-zA-Z0-9-_]+)', content)
        sheet_ids = re.findall(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', content)
        embed_ids = re.findall(r'docId=([a-zA-Z0-9-_]{20,})', content)
        
        all_ids = list(set(drive_ids + sheet_ids + embed_ids))
        print(f"ℹ️ 在 6 月網頁中發現了 {len(all_ids)} 個隱藏的檔案元件。")
        
        # 開始一個一個下載
        count = 1
        for file_id in all_ids:
            if len(file_id) < 20:
                continue
                
            # 這裡我們換個策略：不管名字了！只要有符合「Excel 或試算表格式」的元件，我們通通抓下來
            # 下載下來後，我們直接看檔案內容，這樣最快
            download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
            
            try:
                print(f"📥 正在嘗試下載第 {count} 個檔案 (ID: {file_id[:10]}...)...")
                file_data = requests.get(download_url, headers=headers).content
                
                # 暫存檔名
                output_name = f"test_file_{count}.xlsx"
                with open(output_name, "wb") as f:
                    f.write(file_data)
                print(f"🎉 成功下載第 {count} 個檔案，暫存為: {output_name}")
                count += 1
            except Exception as e:
                print(f"🔺 檔案 {file_id[:10]}... 無法直接下載: {e}")
                
        if count == 1:
            print("❌ 網頁內的所有隱藏元件都無法被轉換成 Excel 下載點。")
            
    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    direct_test()
