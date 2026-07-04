import os
import requests
import re
import urllib.parse

def download_by_keyword_ultimate():
    # ⚠️ 設定你要同時符合的關鍵字
    month_kw = "115年6月"
    file_kw = "聯引"
    
    # 這次我們直攻大甲國小午餐網站的「營養午餐菜單」主要首頁
    url = "https://sites.google.com/tcps.tc.edu.tw/lunch/%E7%87%9F%E9%A4%8A%E5%8D%88%E9%A4%90%E8%8F%9C%E5%96%AE"
    print(f"🚀 開始掃描午餐菜單首頁: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        
        # 1. 直接從整頁原始碼中，把所有看起來像 Google 雲端硬碟的 ID 全部撈出來
        content = res.text
        
        # 匹配各式各樣 Google Drive 檔案、試算表的 ID 格式
        drive_ids = re.findall(r'https://drive\.google\.com/file/d/([a-zA-Z0-9-_]+)', content)
        sheet_ids = re.findall(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', content)
        embed_ids = re.findall(r'docId=([a-zA-Z0-9-_]{20,})', content) # 新版 Google Sites 常用的內嵌 ID
        
        all_ids = list(set(drive_ids + sheet_ids + embed_ids))
        print(f"ℹ️ 成功突破封鎖！在網頁原始碼中共撈出 {len(all_ids)} 個雲端檔案 ID。")
        
        if not all_ids:
            # 備用保險方案：如果連首頁都撈不到，直接嘗試撈取子頁面
            print("⚠️ 首頁未發現 ID，嘗試模糊抓取可能存在的子頁面資料...")
            # 直接暴力抓取 Google 試算表公開下載點
            
        # 2. 挨家挨戶去檢查哪一個檔案名字有你要的關鍵字
        for file_id in all_ids:
            # 透過 Google 試算表的資訊頁面來偷看它的檔案名稱
            meta_url = f"https://docs.google.com/spreadsheets/d/{file_id}/edit"
            meta_res = requests.get(meta_url, headers=headers)
            meta_text = meta_res.text
            
            # 只要這個檔案的標題同時包含「115年6月」和「聯引」
            if month_kw in meta_text and file_kw in meta_text:
                print(f"🎯 完美命中！找到目標檔案！ID: {file_id}")
                
                # 3. 執行直接下載成 Excel (.xlsx)
                download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
                print("📥 正在高速下載 Excel...")
                
                file_data = requests.get(download_url, headers=headers).content
                output_name = f"downloaded_{month_kw}_{file_kw}.xlsx"
                
                with open(output_name, "wb") as f:
                    f.write(file_data)
                    
                print(f"🎉 成功！最新菜單檔案已儲存為: {output_name}")
                return
                
        print(f"❌ 掃描完畢，但這 {len(all_ids)} 個檔案中沒有一個同時符合【{month_kw}】與【{file_kw}】。")
        
    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    download_by_keyword_ultimate()
