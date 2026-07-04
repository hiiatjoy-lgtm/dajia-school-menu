import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

def test_and_download():
    # ⚠️ 1. 直接指定你要測試的月份與關鍵字
    month_keyword = "115年6月"
    file_keyword = "聯引"
    
    # 2. 學校 Google Sites 的標準子網頁命名規律
    target_page_url = f"https://sites.google.com/tcps.tc.edu.tw/lunch/{urllib.parse.quote(month_keyword)}%E8%8F%9C%E5%96%AE"
    print(f"🚀 直攻目標子網頁: {target_page_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(target_page_url, headers=headers)
        if res.status_code == 404:
            print("❌ 找不到該月份的網頁，請檢查月份關鍵字是否輸入正確（例如：115年6月）。")
            return
            
        # 3. 關鍵突破：直接搜尋網頁原始碼裡面的所有 Google Drive 檔案 ID
        # Google 內嵌元件會把 ID 藏在網址或 data 屬性裡
        content_str = res.text
        
        # 我們要在原始碼中找出所有含有 drive.google.com/file/d/ 或 spreadsheets/d/ 的字串
        import re
        # 尋找 Google Drive 檔案 ID 的正規表示式
        drive_ids = re.findall(r'https://drive\.google\.com/file/d/([a-zA-Z0-9-_]+)', content_str)
        sheet_ids = re.findall(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', content_str)
        
        # 合併所有找到的 ID
        all_ids = list(set(drive_ids + sheet_ids))
        print(f"ℹ️ 在網頁原始碼中偵測到 {len(all_ids)} 個潛在的 Google 雲端檔案。")
        
        if not all_ids:
            print("❌ 無法從網頁解析出任何雲端檔案 ID。")
            return

        # 4. 逐一比對檔案名稱是否符合「聯引」
        # 透過 Google Drive API 的公開節點去抓取檔案名稱
        for file_id in all_ids:
            meta_url = f"https://docs.google.com/spreadsheets/d/{file_id}/edit"
            meta_res = requests.get(meta_url, headers=headers)
            
            # 檢查這個檔案的標題是否包含「聯引」
            if file_keyword in meta_res.text or file_keyword in urllib.parse.unquote(meta_res.text):
                print(f"🎯 命中目標！找到同時符合 【{month_keyword}】與【{file_keyword}】的檔案！")
                
                # 5. 執行直接下載
                download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
                print("📥 開始高速下載 Excel 檔案...")
                
                file_data = requests.get(download_url, headers=headers).content
                output_name = f"downloaded_{month_keyword}_{file_keyword}.xlsx"
                
                with open(output_name, "wb") as f:
                    f.write(file_data)
                    
                print(f"🎉 成功！檔案已存為: {output_name}")
                return
                
        print(f"❌ 雖然找到了雲端檔案，但沒有一個名稱含有【{file_keyword}】。")

    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    test_and_download()
