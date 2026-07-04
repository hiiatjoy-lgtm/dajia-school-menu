import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 大甲國小營養午餐網頁
URL = "https://sites.google.com/tcps.tc.edu.tw/lunch/%E7%87%9F%E9%A4%8A%E5%8D%88%E9%A4%90%E8%8F%9C%E5%96%AE"

def download_menu_by_keyword(keyword="聯引"):
    print(f"正在進入大甲國小午餐網站，搜尋包含【{keyword}】的菜單檔案...")
    
    # 模擬瀏覽器發送請求，避免被 Google 阻擋
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(URL, headers=headers)
        res.raise_for_status()
    except Exception as e:
        print(f"網頁連線失敗: {e}")
        return None

    soup = BeautifulSoup(res.text, 'html.parser')
    target_url = None
    file_name = ""

    # 1. 搜尋網頁上所有的超連結
    links = soup.find_all('a')
    for link in links:
        href = link.get('href', '')
        text = link.get_text() # 連結顯示的文字
        
        # 轉址解碼，有時候中文會變成 %E8%81%AF%E5%BC%95 這種編碼
        decoded_href = urllib.parse.unquote(href)
        
        # 條件：連結網址或顯示文字中包含「聯引」，且是 Excel 相關連結
        if keyword in text or keyword in decoded_href:
            if "drive.google.com" in href or ".xlsx" in href:
                target_url = href
                file_name = text.strip() if text.strip() else f"{keyword}_menu.xlsx"
                break

    if not target_url:
        print(f"❌ 找不到包含關鍵字【{keyword}】的菜單檔案連結。")
        return None

    print(f"🎯 成功找到目標檔案！\n檔案名稱: {file_name}\n下載網址: {target_url}")

    # 2. 將 Google Drive 的預覽連結轉換為「直接下載連結」
    # 把 /file/d/XXXX/view 改成 /uc?export=download&id=XXXX
    if "drive.google.com" in target_url and "/file/d/" in target_url:
        file_id = target_url.split("/file/d/")[1].split("/")[0]
        download_url = f"https://docs.google.com/uc?export=download&id={file_id}"
    else:
        download_url = target_url

    # 3. 開始下載檔案
    print("正在下載檔案中...")
    file_res = requests.get(download_url, headers=headers)
    
    local_filename = f"downloaded_{keyword}.xlsx"
    with open(local_filename, "wb") as f:
        f.write(file_res.content)
        
    print(f"✨ 檔案已成功下載並儲存為: {os.path.abspath(local_filename)}")
    return local_filename

if __name__ == "__main__":
    # 執行下載
    excel_file = download_menu_by_keyword("聯引")
    
    if excel_file:
        # 接下來可以在這裡接續續上一次寫的「Excel 轉圖片」程式碼
        pass
