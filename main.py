import os
import requests
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd

def is_last_workday_of_month():
    """自動判斷今天是否為當月最後一個平日（週一至週五）"""
    today = datetime.date.today()
    
    # 找出當月最後一天
    if today.month == 12:
        last_day = datetime.date(today.year, 12, 31)
    else:
        last_day = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
    
    # 從最後一天往回找第一個平日（排除週六 5、週日 6）
    last_workday = last_day
    while last_workday.weekday() >= 5:
        last_workday -= datetime.timedelta(days=1)
        
    return today == last_workday

def get_next_month_strings():
    """自動計算下個月的民國年份與月份字串（例如 115年8月）"""
    today = datetime.date.today()
    if today.month == 12:
        next_month_date = datetime.date(today.year + 1, 1, 1)
    else:
        next_month_date = datetime.date(today.year, today.month + 1, 1)
        
    tw_year = next_month_date.year - 1911
    return f"{tw_year}年{next_month_date.month}月"

def generate_no_menu_html(target_month):
    """當尋找不到符合檔案時，自動生成提示網頁"""
    print(f"⚠️ 顯示提示：目前尚未提供 {target_month} 菜單")
    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>大甲國小 午餐菜單</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px; display: flex; align-items: center; justify-content: center; min-height: 80vh; }}
        .card {{ max-width: 400px; background: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; }}
        h1 {{ color: #dc2626; font-size: 22px; margin-bottom: 10px; }}
        p {{ color: #4b5563; font-size: 15px; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🍱 菜單尚未更新</h1>
        <p>學校目前尚未提供 <strong>{target_month}</strong> 的聯引午餐菜單數據。<br>請稍後再試，系統將會定時自動嘗試同步！</p>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def build_menu_html(target_month, df):
    """將解析成功的 Excel 資料轉換為正式精美網頁，直接覆蓋原本內容"""
    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=2.0">
    <title>大甲國小 {target_month} 午餐菜單</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 12px; color: #1f2937; }}
        .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 16px; border-radius: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
        h1 {{ text-align: center; color: #1e3a8a; font-size: 20px; margin-bottom: 4px; font-weight: 700; }}
        p.subtitle {{ text-align: center; color: #6b7280; margin-top: 0; font-size: 13px; margin-bottom: 16px; }}
        .menu-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        .menu-table th {{ background-color: #1e3a8a; color: white; padding: 10px; font-weight: 600; text-align: center; }}
        .menu-table td {{ padding: 12px 8px; border-bottom: 1px solid #e5e7eb; line-height: 1.4; }}
        .menu-table tr:nth-child(even) {{ background-color: #f9fafb; }}
        .date-col {{ font-weight: bold; color: #b45309; width: 25%; text-align: center; }}
        .dish-col {{ color: #374151; width: 75%; }}
        .footer {{ text-align: center; margin-top: 16px; font-size: 11px; color: #9ca3af; line-height: 1.4; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🍱 大甲國小 午餐菜單</h1>
        <p class="subtitle">🗓️ {target_month}份 (聯引/非素食)</p>
        <table class="menu-table">
            <thead>
                <tr>
                    <th>日期</th>
                    <th>今日菜色</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # 智慧型解析各校欄位：尋找含有日期與菜色特徵的欄位進行橫向合併
    for idx, row in df.iterrows():
        row_values = [str(v).strip() for v in row.values if pd.notna(v) and str(v).strip() != '']
        if len(row_values) >= 2:
            date_text = row_values[0]
            # 排除非菜單內容的表頭
            if "日期" in date_text or "月" not in date_text:
                continue
            dishes_text = "、".join(row_values[1:])
            html_content += f"""
                <tr>
                    <td class="date-col">{date_text}</td>
                    <td class="dish-col">{dishes_text}</td>
                </tr>"""
                
    html_content += """
            </tbody>
        </table>
        <div class="footer">💡 小提示：手指雙擊或雙指往外張開可放大檢視<br>本資料由大甲國小午餐系統自動同步</div>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("🎉 菜單網頁 index.html 更新成功並已直接覆蓋舊檔案！")

def run_scraper():
    # 1. 日期安全守衛：不是月底最後一個平日，直接退出不工作
    if not is_last_workday_of_month():
        print("📅 今天不是當月的最後一個平日，自動跳過執行。")
        return

    target_month = get_next_month_strings()
    print(f"🎯 觸發排程！開始自動抓取下個月菜單目標：{target_month}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    base_url = "https://sites.google.com/tcps.tc.edu.tw/lunch/%E7%87%9F%E9%A4%8A%E5%8D%88%E9%A4%90%E8%8F%9C%E5%96%AE"
    
    try:
        res = requests.get(base_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 尋找目標月份的子網頁連結
        sub_page_url = None
        for a_tag in soup.find_all('a', href=True):
            if target_month in a_tag.text or target_month in a_tag['href']:
                href = a_tag['href']
                sub_page_url = href if href.startswith('http') else f"https://sites.google.com{href}"
                break
                
        if not sub_page_url:
            sub_page_url = f"https://sites.google.com/tcps.tc.edu.tw/lunch/{target_month}%E8%8F%9C%E5%96%AE"

        print(f"📡 進入月份網頁: {sub_page_url}")
        sub_res = requests.get(sub_page_url, headers=headers, timeout=15)
        
        # 抓取頁面所有 Google Drive 連結
        drive_links = re.findall(r'https://docs\.google\.com/spreadsheets/d/[\w-]+', sub_res.text)
        if not drive_links:
            generate_no_menu_html(target_month)
            return
            
        drive_links = list(set(drive_links))
        selected_df = None
        
        # 橫向比對所有檔案
        for link in drive_links:
            export_url = f"{link}/export?format=xlsx"
            try:
                test_res = requests.get(export_url, headers=headers, timeout=10)
                if test_res.content[:2] == b'PK':
                    with open("temp.xlsx", "wb") as tmp:
                        tmp.write(test_res.content)
                    
                    xl = pd.ExcelFile("temp.xlsx")
                    # 篩選分頁名稱：包含「聯引」且排除「素食」
                    target_sheets = [s for s in xl.sheet_names if "聯引" in s and "素食" not in s]
                    
                    if target_sheets:
                        selected_df = pd.read_excel("temp.xlsx", sheet_name=target_sheets[0])
                        # 同時儲存原始 xlsx 備份
                        with open("menu.xlsx", "wb") as f:
                            f.write(test_res.content)
                        break
            except:
                pass
            finally:
                if os.path.exists("temp.xlsx"): os.remove("temp.xlsx")
                
        # 判斷最後篩選結果
        if selected_df is not None:
            # 清除空列並渲染成 HTML
            selected_df = selected_df.dropna(how='all').fillna('')
            build_menu_html(target_month, selected_df)
        else:
            # 搜尋不到符合選項的檔案
            generate_no_menu_html(target_month)
            
    except Exception as e:
        print(f"💥 發生錯誤: {e}")
        generate_no_menu_html(target_month)

if __name__ == "__main__":
    run_scraper()
