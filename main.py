import os
import re
import urllib.parse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def download_file(file_id, count, headers):
    import requests
    urls = [
        f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx",
        f"https://docs.google.com/uc?export=download&id={file_id}"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200 and len(res.content) > 5000 and b"html" not in res.content[:200]:
                output_name = f"downloaded_6month_file_{count}.xlsx"
                with open(output_name, "wb") as f:
                    f.write(res.content)
                print(f"🎉 成功下載第 {count} 個符合條件的菜單檔案！儲存為: {output_name}")
                return True
        except:
            continue
    return False

def run_dynamic_scraper():
    target_url = "https://sites.google.com/tcps.tc.edu.tw/lunch/115%E5%B9%B46%E6%9C%A8%E8%8F%9C%E5%96%AE"
    
    # ⚠️ 設定您的過濾關鍵字
    include_keyword = "聯引"
    exclude_keyword = "素食"
    
    print(f"🌐 啟動 Playwright 雲端瀏覽器，直攻 6 月網頁...")
    print(f"🔍 篩選目標：必須包含【{include_keyword}】且 排除包含【{exclude_keyword}】的檔案")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=headers['User-Agent'])
        
        try:
            page.goto(target_url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000) # 強制等待 5 秒讓內嵌組件載入
            
            rendered_html = page.content()
            browser.close()
            print("📡 網頁動態渲染完成，開始解析資料...")
            
            # 撈取所有隱藏的 Google 檔案 ID
            drive_ids = re.findall(r'drive\.google\.com/file/d/([a-zA-Z0-9-_]+)', rendered_html)
            sheet_ids = re.findall(r'docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', rendered_html)
            viewer_ids = re.findall(r'docs\.google\.com/file/d/([a-zA-Z0-9-_]+)', rendered_html)
            
            all_ids = list(set(drive_ids + sheet_ids + viewer_ids))
            print(f"ℹ️ 在動態網頁中一共抓到 {len(all_ids)} 個潛在的雲端檔案物件。")
            
            count = 1
            import requests
            for file_id in all_ids:
                if len(file_id) < 20:
                    continue
                
                # 透過公開管道驗證檔案標題
                test_url = f"https://docs.google.com/spreadsheets/d/{file_id}/edit"
                try:
                    meta_res = requests.get(test_url, headers=headers, timeout=10)
                    meta_text = meta_res.text
                    decoded_meta = urllib.parse.unquote(meta_text)
                    
                    # 檢查是否含有【素食】排除關鍵字，有的話直接跳過不下載！
                    if exclude_keyword in meta_text or exclude_keyword in decoded_meta:
                        print(f"⏭️ 跳過：發現含有排除關鍵字【{exclude_keyword}】的檔案 (ID: {file_id[:10]}...)")
                        continue
                        
                    # 檢查是否含有【聯引】必要關鍵字
                    if include_keyword in meta_text or include_keyword in decoded_meta:
                        print(f"🎯 命中：發現完全符合條件的檔案 (ID: {file_id[:10]}...)")
                        if download_file(file_id, count, headers):
                            count += 1
                            
                except Exception as e:
                    # 保險策略：如果無法線上讀取標題，我們依然先試抓看看，交給主邏輯判斷
                    pass
            
            if count == 1:
                print("❌ 搜尋完畢，未發現符合條件（包含聯引且非素食）的 Excel 檔案。")
                
        except Exception as e:
            print(f"💥 瀏覽器自動化發生異常: {e}")

if __name__ == "__main__":
    run_dynamic_scraper()
