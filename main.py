import os
import requests
import re
import urllib.parse
import json

def ultimate_google_sites_scraper():
    month_keyword = "115年6月"
    file_keyword = "聯引"
    
    # 這是大甲國小午餐菜單的主網頁
    base_url = "https://sites.google.com/tcps.tc.edu.tw/lunch/%E7%87%9F%E9%A4%8A%E5%8D%88%E9%A4%90%E8%8F%9C%E5%96%AE"
    print(f"🚀 [第一階段] 正在掃描主要網頁...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(base_url, headers=headers)
        res.raise_for_status()
        
        # 1. 關鍵突破：尋找 Google Sites 的內嵌網頁資料區塊
        # Google 會把整個網站的結構包在一個特定的 JavaScript 變數或 JSON 欄位中
        html_content = res.text
        
        # 尋找所有可能的子網頁路徑（模糊搜尋 115年6月 的網址編碼）
        print("🔍 正在解析網頁內的隱藏結構...")
        
        # 2. 如果沒抓到子網頁，我們直接用強力的萬用手法：
        # 既然是 Google 試算表，我們直接用正則表達式把整頁網頁（含子網頁）只要有出現過的 Google ID 通通打包
        # 這是最暴力的作法，不管是內嵌、按鈕、連結，只要在記憶體裡出現過就抓
        
        # 直接抓取主要頁面與潛在子頁面
        urls_to_check = [base_url]
        
        # 嘗試拼湊可能的正確子網頁網址（處理編碼問題）
        encoded_month = urllib.parse.quote(month_keyword)
        urls_to_check.append(f"https://sites.google.com/tcps.tc.edu.tw/lunch/{encoded_month}%E8%8F%9C%E5%96%AE")
        urls_to_check.append(f"https://sites.google.com/tcps.tc.edu.tw/lunch/{encoded_month}")
        
        all_found_ids = []
        
        for url in urls_to_check:
            print(f"📡 正在深挖網址: {url}")
            try:
                sub_res = requests.get(url, headers=headers)
                if sub_res.status_code == 200:
                    text = sub_res.text
                    # 擷取所有可能是 Google Drive / Sheets 的 ID (長度通常在 25-50 個字元之間的英數與符號組合)
                    ids = re.findall(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', text)
                    ids += re.findall(r'https://drive\.google\.com/file/d/([a-zA-Z0-9-_]+)', text)
                    ids += re.findall(r'"docId"\s*:\s*"([a-zA-Z0-9-_]+)"', text)
                    ids += re.findall(r'docId=([a-zA-Z0-9-_]+)', text)
                    all_found_ids.extend(ids)
            except:
                continue
                
        all_found_ids = list(set(all_found_ids))
        print(f"ℹ️ 總共撈出 {len(all_found_ids)} 個隱藏的 Google 雲端物件。")
        
        # 3. 挨個去跟 Google 伺服器驗證，哪一個是「115年6月」而且有「聯引」
        for file_id in all_found_ids:
            if len(file_id) < 20: # 太短的不是真正的 ID
                continue
                
            # 藉由讀取公開的 export 或 edit 頁面來判定檔案標題
            test_url = f"https://docs.google.com/spreadsheets/d/{file_id}/edit"
            try:
                meta_res = requests.get(test_url, headers=headers)
                meta_text = meta_res.text
                
                # 同時比對網頁標題或內容是否包含關鍵字
                if file_keyword in meta_text:
                    print(f"🎯 成功匹配！找到符合關鍵字【{file_keyword}】的雲端檔案 (ID: {file_id})")
                    
                    # 4. 直接下載成 Excel (.xlsx)
                    download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
                    print("📥 正在下載...")
                    
                    file_data = requests.get(download_url, headers=headers).content
                    output_name = f"downloaded_{month_keyword}_{file_keyword}.xlsx"
                    
                    with open(output_name, "wb") as f:
                        f.write(file_data)
                        
                    print(f"🎉 檔案成功儲存為: {output_name}")
                    return
            except:
                continue
                
        print("❌ 搜尋完畢，未找到完全符合條件的檔案。")
        
    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    ultimate_google_sites_scraper()
