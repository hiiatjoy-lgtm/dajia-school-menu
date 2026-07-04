import os
import requests
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd
import matplotlib.pyplot as plt

# 設定支援中文的字型（防止圖片變亂碼）
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def is_last_workday_of_month():
    """【測試模式】強制放行，不檢查是否為月底平日"""
    return True

def get_next_month_strings():
    """獲取下個月的年份與月份中文字串"""
    today = datetime.date.today()
    if today.month == 12:
        next_month_date = datetime.date(today.year + 1, 1, 1)
    else:
        next_month_date = datetime.date(today.year, today.month + 1, 1)
    tw_year = next_month_date.year - 1911
    return f"{tw_year}年{next_month_date.month}月"

def convert_excel_to_image(excel_path, image_path):
    """將 Excel 菜單檔案轉換為清晰的 PNG 圖片"""
    print("🎨 正在將 Excel 菜單轉換為圖片...")
    try:
        # 讀取 Excel 檔案
        df = pd.read_excel(excel_path)
        # 清除全空的行列
        df = df.dropna(how='all').fillna('')
        
        # 建立 matplotlib 畫布
        fig, ax = plt.subplots(figsize=(10, 12), dpi=200)
        ax.axis('off')
        
        # 繪製表格
        table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)  # 放大表格格子寬度與高度
        
        # 美化表格外觀
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor('#2c3e50')  # 表頭深藍色
            else:
                cell.set_facecolor('#f8f9fa' if row % 2 == 0 else 'white') # 雙單行交替色
                
        plt.savefig(image_path, bbox_inches='tight')
        plt.close()
        print(f"🎉 圖片轉換成功！已儲存為 {image_path}")
    except Exception as e:
        print(f"❌ 轉圖失敗: {e}")

def run_scraper():
    if not is_last_workday_of_month():
        print("📅 今天不是當月的最後一個平日，跳過執行。")
        return

    # 🎯 測試模式：直接鎖定 115年6月 菜單
    target_month = "115年6月"
    print(f"🎯 [測試模式啟動] 開始抓取菜單目標：{target_month}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    base_url = "https://sites.google.com/tcps.tc.edu.tw/lunch/%E7%87%9F%E9%A4%8A%E5%8D%88%E9%A4%90%E8%8F%9C%E5%96%AE"
    
    try:
        res = requests.get(base_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 在首頁尋找目標月份的子網頁連結
        sub_page_url = None
        for a_tag in soup.find_all('a', href=True):
            if target_month in a_tag.text or target_month in a_tag['href']:
                href = a_tag['href']
                sub_page_url = href if href.startswith('http') else f"https://sites.google.com{href}"
                break
                
        if not sub_page_url:
            print(f"⚠️ 在首頁沒找到 {target_month} 的專屬選單網頁，嘗試直接拼接網址...")
            sub_page_url = f"https://sites.google.com/tcps.tc.edu.tw/lunch/{target_month}%E8%8F%9C%E5%96%AE"

        print(f"📡 進入月份子網頁: {sub_page_url}")
        sub_res = requests.get(sub_page_url, headers=headers, timeout=15)
        
        # 2. 搜尋 Google Drive 下載點或試算表 ID
        drive_links = re.findall(r'https://docs\.google\.com/spreadsheets/d/[\w-]+', sub_res.text)
        
        if not drive_links:
            print("❌ 無法在網頁中自動解析出 Google 試算表連結。")
            return
            
        drive_links = list(set(drive_links))
        print(f"🔍 找到 {len(drive_links)} 個雲端檔案，準備篩選...")
        
        # 3. 精準篩選
        selected_url = None
        for link in drive_links:
            export_url = f"{link}/export?format=xlsx"
            test_res = requests.get(export_url, headers=headers, timeout=10)
            
            if test_res.content[:2] == b'PK':
                with open("temp.xlsx", "wb") as tmp:
                    tmp.write(test_res.content)
                
                try:
                    xl = pd.ExcelFile("temp.xlsx")
                    sheet_names = "".join(xl.sheet_names)
                    if "聯引" in sheet_names and "素食" not in sheet_names:
                        selected_url = export_url
                        break
                except:
                    pass
                    
        if not selected_url:
            print("💡 啟用大甲國小標準聯引渠道下載...")
            selected_url = "https://docs.google.com/spreadsheets/d/1U4M_0_SgIcl3mCH70Z7GjC1kE9MshLpE1YF-A_ZpZsc/export?format=xlsx"

        # 4. 真正下載檔案並儲存
        print("📥 正在下載最終確認的 menu.xlsx...")
        final_res = requests.get(selected_url, headers=headers)
        with open("menu.xlsx", "wb") as f:
            f.write(final_res.content)
        print("🎉 menu.xlsx 下載成功！")
        
        # 5. 觸發轉圖
        convert_excel_to_image("menu.xlsx", "menu.png")
        
        if os.path.exists("temp.xlsx"): os.remove("temp.xlsx")
        
    except Exception as e:
        print(f"💥 發生錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
