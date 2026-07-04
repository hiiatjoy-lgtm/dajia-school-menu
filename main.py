import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 大甲國小營養午餐網頁首頁
BASE_URL = "https://sites.google.com/tcps.tc.edu.tw/lunch"
URL = f"{BASE_URL}/%E7%87%9F%E9%A4%8A%E5%8D%88%E9%A4%90%E8%8F%9C%E5%96%AE"

def download_menu_by_keyword(keyword="115年6月"):
    print(f"==========================================")
    print(f"🚀 開始偵測網頁，尋找關鍵字: 【{keyword}】")
    print(f"==========================================")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(URL, headers=headers)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ 網頁連線失敗: {e}")
        return None

    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 1. 找出網頁上所有的超連結，並印出來除錯
    links = soup.find_all('a')
    print(f"ℹ️ 在首頁共找到 {len(links)} 個連結。")
    
    sub_page_url = None
    
    for link in links:
        href = link.get('href', '')
        text = link.get_text().strip()
        decoded_href = urllib.parse.unquote(href)
        
        # 如果連結文字或網址包含月份關鍵字 (例如 115年6月)
        if keyword in text or keyword in decoded_href:
            print(f"🎯 找到符合月份的子網頁連結: 文字【{text}】-> 網址【{href}】")
            if href.startswith('/'):
                sub_page_url = "https://sites.google.com" + href
            else:
                sub_page_url = href
            break

    # 如果在首頁找不到月份，試著直接拼接常見的 Google Sites 網址結構
    if not sub_page_url:
        print(f"⚠️ 首頁未直接發現連結，嘗試直接拼接子網頁網址...")
        sub_page_url = f"{BASE_URL}/%E{keyword}菜單" 
        # 範例: https://sites.google.com/tcps.tc.edu.tw/lunch/115年6月菜單

    print(f"📂 正在進入子網頁嘗試抓取實際檔案: {sub_page_url}")
    
    try:
        sub_res = requests.get(sub_page_url, headers=headers)
        sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
        sub_links = sub_soup.find_all('a')
        
        target_file_url = None
        # 在子網頁中尋找含有「聯引」或 Google Drive 的下載連結
        for sub_link in sub_links:
            s_href = sub_link.get('href', '')
            s_text = sub_link.get_text().strip()
            s_decoded = urllib.parse.unquote(s_href)
            
            print(f"  [偵測到子網頁連結] 文字: {s_text} | 網址: {s_href[:60]}...")
            
            if "drive.google.com" in s_href or "docs.google.com" in s_href:
                target_file_url = s_href
                print(f"✨ 成功捕捉到 Google 雲端硬碟元件！")
                break
    except Exception as e:
        print(f"❌ 讀取子網頁失敗: {e}")
        return None

    if not target_file_url:
        print(f"❌ 無法在網頁中解析出 Excel 檔案的直接下載點。")
        return None

    # 2. 轉換為直接下載連結
    if "drive.google.com" in target_file_url and "/file/d/" in target_file_url:
        file_id = target_file_url.split("/file/d/")[1].split("/")[0]
        download_url = f"https://docs.google.com/uc?export=download&id={file_id}"
    else:
        download_url = target_file_url

    # 3. 下載檔案
    print(f"📥 開始下載目標 Excel...")
    file_res = requests.get(download_url, headers=headers)
    local_filename = f"downloaded_{keyword}.xlsx"
    with open(local_filename, "wb") as f:
        f.write(file_res.content)
        
    print(f"🎉 檔案下載成功，儲存於: {local_filename}")
    return local_filename

if __name__ == "__main__":
    # 先測試抓取 115年6月 的菜單
    download_menu_by_keyword("115年6月")
