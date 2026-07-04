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
            # 確保抓下來的是真正的二進位試算表檔案，而不是網頁 HTML
            if res.status_code == 200 and len(res.content) > 5000 and b"html" not in res.content[:200]:
                output_name = f"downloaded_6month_file_{count}.xlsx"
                with open(output_name, "wb") as f:
                    f.write(res.content)
                print(f"🎉 [成功] 已成功下載檔案，儲存為: {output_name}")
                return True
        except:
            continue
    return False

def run_ultimate_frame_scraper():
    # 直攻大甲國小 6 月份菜單網頁
    target_url = "https://sites.google.com/tcps.tc.edu.tw/lunch/115%E5%B9%B46%E6%9C%A8%E8%8F%9C%E5%96%AE"
    include_keyword = "聯引"
    exclude_keyword = "素食"
    
    print(f"🌐 [啟動解密] Playwright 正在強行突破 Google Sites 內嵌框架...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=headers['User-Agent'])
        
        try:
            # 載入網頁並等待
            page.goto(target_url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(6000) # 給內嵌元件充足的時間解密
            
            # 📦 關鍵突破：把主網頁以及內部「所有的 iframe 框架」的原始碼全部撈出來拼在一起！
            print("🔍 正在進行全框架（Frames）深層掃描...")
            combined_html = page.content()
            
            for frame in page.frames:
                try:
                    combined_html += "\n" + frame.content()
                except:
                    continue
                    
            browser.close()
            
            # 從大雜燴原始碼中精準撈取 Google 雲端的所有 ID 特徵
            drive_ids = re.findall(r'drive\.google\.com/file/d/([a-zA-Z0-9-_]+)', combined_html)
            sheet_ids = re.findall(r'docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', combined_html)
            viewer_ids = re.findall(r'docs\.google\.com/[a-zA-Z0-9-_]+/d/([a-zA-Z0-9-_]+)', combined_html)
            resource_ids = re.findall(r'docId=([a-zA-Z0-9-_]+)', combined_html)
            
            all_ids = list(set(drive_ids + sheet_ids + viewer_ids + resource_ids))
            print(f"ℹ️ [解密成功] 在深層內嵌沙盒中一共挖掘出 {len(all_ids)} 個隱藏的雲端物件 ID。")
            
            count = 1
            import requests
            for file_id in all_ids:
                if len(file_id) < 20:
                    continue
                
                # 請求 Google 獲取該物件的標題資訊
                test_url = f"https://docs.google.com/spreadsheets/d/{file_id}/edit"
                try:
                    meta_res = requests.get(test_url, headers=headers, timeout=10)
                    meta_text = meta_res.text
                    decoded_meta = urllib.parse.unquote(meta_text)
                    
                    # 排除素食
                    if exclude_keyword in meta_text or exclude_keyword in decoded_meta:
                        print(f"⏭️ [過濾] 發現包含【{exclude_keyword}】，自動跳過。")
                        continue
                    
                    # 包含聯引 或是 無法讀取標題但長度吻合的（採取保險試抓）
                    if include_keyword in meta_text or include_keyword in decoded_meta or "Google Docs" in meta_text:
                        print(f"🎯 [命中] 發現目標雲端元件！ID: {file_id[:12]}...")
                        if download_file(file_id, count, headers):
                            count += 1
                except:
                    # 無法讀取中介資料時，強制盲抓測試
                    if download_file(file_id, count, headers):
                        count += 1
            
            if count == 1:
                print("❌ 穿透了所有框架，但未在 Google Drive 元件中發現符合篩選條件的試算表。")
                
        except Exception as e:
            print(f"💥 自動化中斷: {e}")

if __name__ == "__main__":
    run_ultimate_frame_scraper()
