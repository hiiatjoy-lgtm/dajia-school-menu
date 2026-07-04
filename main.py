import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# 大甲國小午餐菜單總首頁
MENU_HOME_URL = "https://sites.google.com/tcps.tc.edu.tw/lunch/%E7%87%9F%E9%A4%8A%E5%8D%88%E9%A4%90%E8%8F%9C%E5%96%AE"

def run_menu_scraper():
    # ⚠️ 設定要找尋的「月份網站關鍵字」與「檔案關鍵字」
    month_keyword = "115年6月"
    file_keyword = "聯引"
    
    print(f"==========================================")
    print(f"第一階段：正在總網頁中找尋【{month_keyword}】的菜單網站...")
    print(f"==========================================")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(MENU_HOME_URL, headers=headers)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ 無法連線至午餐菜單首頁: {e}")
        return

    soup = BeautifulSoup(res.text, 'html.parser')
    all_links = soup.find_all('a')
    
    target_month_url = None
    
    # 遍歷首頁所有超連結，找尋月份網站
    for link in all_links:
        href = link.get('href', '')
        text = link.get_text().strip()
        decoded_href = urllib.parse.unquote(href)
        
        # 只要連結文字或網址本身包含月份（如 115年6月）
        if month_keyword in text or month_keyword in decoded_href:
            print(f"🎯 成功找到【{month_keyword}】的網站連結！")
            print(f"   ➔ 顯示文字: {text}")
            
            if href.startswith('/'):
                target_month_url = "https://sites.google.com" + href
            else:
                target_month_url = href
            break

    # 如果首頁沒撈到月份網站，使用安全備用路徑直接前往子網頁
    if not target_month_url:
        print(f"⚠️ 首頁連結未直接顯露，改由路徑直接前往月份子網頁...")
        target_month_url = f"https://sites.google.com/tcps.tc.edu.tw/lunch/{urllib.parse.quote(month_keyword)}%E8%8F%9C%E5%96%AE"

    print(f"\n==========================================")
    print(f"第二階段：進入月份網站，找尋含有【{file_keyword}】的 xlsx 檔案...")
    print(f"導向網址: {target_month_url}")
    print(f"==========================================")
    
    try:
        month_res = requests.get(target_month_url, headers=headers)
        if month_res.status_code == 404:
            print(f"❌ 月份子網站回傳 404 找不到網頁，請確認【{month_keyword}】名稱是否與學校網站一致。")
            return
            
        month_soup = BeautifulSoup(month_res.text, 'html.parser')
        
        # 策略 A：尋找網頁上顯露出的所有實體 A 標籤連結
        month_links = month_soup.find_all('a')
        file_id = None
        
        for m_link in month_links:
            m_href = m_link.get('href', '')
            m_text = m_link.get_text().strip()
            m_decoded = urllib.parse.unquote(m_href)
            
            # 如果發現連結或文字同時含有「聯引」，且指向 Google 雲端
            if file_keyword in m_text or file_keyword in m_decoded:
                if "drive.google.com" in m_href or "docs.google.com" in m_href:
                    print(f"✨ 從網頁連結標籤中找到完全符合條件的檔案！")
                    print(f"   ➔ 檔案標題: {m_text}")
                    # 擷取 File ID
                    id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', m_href) or re.search(r'id=([a-zA-Z0-9-_]+)', m_href)
                    if id_match:
                        file_id = id_match.group(1)
                        break

        # 策略 B：如果策略 A 沒找到（通常是因為 Google 內嵌元件），則從整網頁原始碼進行深層搜尋
        if not file_id:
            print("ℹ️ 未從一般超連結找到檔案，啟動原始碼深層比對...")
            # 撈出原始碼中所有可能的 Google 文件/試算表 ID
            potential_ids = list(set(re.findall(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', month_res.text) + 
                                     re.findall(r'https://drive\.google\.com/file/d/([a-zA-Z0-9-_]+)', month_res.text) +
                                     re.findall(r'docId=([a-zA-Z0-9-_]{20,})', month_res.text)))
            
            print(f"ℹ️ 在該月份網頁背後共偵測到 {len(potential_ids)} 個隱藏雲端文件元件。")
            
            for pid in potential_ids:
                # 測試該雲端文件的標題
                test_meta_url = f"https://docs.google.com/spreadsheets/d/{pid}/edit"
                meta_res = requests.get(test_meta_url, headers=headers)
                if file_keyword in meta_res.text or file_keyword in urllib.parse.unquote(meta_res.text):
                    print(f"🎯 成功匹配隱藏元件！此檔案名稱含有【{file_keyword}】。")
                    file_id = pid
                    break
                    
        # 第三階段：執行檔案下載
        if file_id:
            download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
            print(f"📥 正在高速下載 Excel 檔案 (ID: {file_id})...")
            
            final_file_res = requests.get(download_url, headers=headers)
            output_filename = f"downloaded_{month_keyword}_{file_keyword}.xlsx"
            
            with open(output_filename, "wb") as f:
                f.write(final_file_res.content)
                
            print(f"🎉【測試成功】檔案已成功存入您的 GitHub 專案首域，檔名為: {output_filename}")
        else:
            print(f"❌ 遺憾，無法在【{month_keyword}】的網頁中定位出含有【{file_keyword}】的 xlsx 檔案。")
            
    except Exception as e:
        print(f"💥 程式執行期間發生異常: {e}")

if __name__ == "__main__":
    run_menu_scraper()
