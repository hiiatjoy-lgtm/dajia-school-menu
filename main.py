name: Auto Update Lunch Menu Image

on:
  schedule:
    # 每天定時在台灣時間下午 5:00 (UTC 9:00) 檢查一次
    - cron: '0 9 * * *'
  workflow_dispatch: # 保留手動按鈕，方便隨時測試

permissions:
  contents: write

jobs:
  build-and-run:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run Scraper and Convert to Image
      run: python main.py

    - name: Commit and Push Changes
      run: |
        git config --global user.name "github-actions[bot]"
        git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"
        
        # 🛠️ 關鍵修正：使用 -A 強制把所有產生的新檔案（包含 index.html）通通抓進來存檔
        git add -A
        
        git diff --quiet && git diff --staged --quiet || (git commit -m "Auto update menu and web files" && git push)
