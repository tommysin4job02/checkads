from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import os
import json
import shutil


def google_ads_check_mobile(site_keywords, screenshot_dir="screenshots", result_file="results.txt"):
    """模擬手機搜尋廣告，滾到廣告位置截圖"""
    # 手機模擬配置
    mobile_emulation = {
        "deviceName": "iPhone X"  # 模擬 iPhone X 設備
    }

    # 瀏覽器配置
    PROXY="148.66.6.214:80"
    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument("--headless=new")  # 無頭模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=375,812")  # iPhone X 分辨率
    chrome_options.add_argument("--disable-application-cache")  # 禁用應用程序緩存
    chrome_options.add_argument("--incognito")  # 無痕模式
    chrome_options.add_argument("--disable-cache")  # 禁用瀏覽器快取
    chrome_options.add_argument("--no-sandbox")  # 避免某些環境權限問題
    chrome_options.add_argument("--disable-dev-shm-usage")  # 避免共享內存不足問題
    chrome_options.add_argument('--lang=zh_TW.UTF-8')
    
    # Proxy Setup
    webdriver.DesiredCapabilities.CHROME['proxy'] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "proxyType": "MANUAL",

    }

    webdriver.DesiredCapabilities.CHROME['acceptSslCerts']=True
    
    # 創建截圖文件夾
    if os.path.exists(screenshot_dir):
        shutil.rmtree(screenshot_dir)
    
    os.makedirs(screenshot_dir, exist_ok=True)

    # 啟動瀏覽器
    driver = webdriver.Chrome(options=chrome_options)
    base_url = "https://www.google.com/search?q="

    # 記錄檢查結果
    results = []
    execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results.append(f"執行時間: {execution_time}\n")

    for site, keywords in site_keywords.items():
        results.append(f"檢查目標網站: {site}\n")

        for keyword in keywords:
            print(f"正在搜索目標網站 '{site}' 的關鍵字: {keyword}")

            for attempt in range(1, 7):  # 最多嘗試 6 次
                print(f"  嘗試第 {attempt} 次...")
                driver.delete_all_cookies()  # 每次搜尋前清除 cookies 和快取
                driver.get(base_url + keyword)

                # 等待頁面加載
                time.sleep(2)

                # 查找廣告區塊
                ads = driver.find_elements(By.XPATH, "//div[@data-text-ad='1']")
                found = False

                for ad in ads[:4]:  # 檢查前 4 個廣告
                    _slot = ad.get_dom_attribute("data-ta-slot")
                    if _slot == "3":
                        results.append(f"  關鍵字: {keyword} 沒有出現於首四個廣告內")
                        print(f"  關鍵字: {keyword} 沒有出現於首四個廣告內")
                    _pos = ad.get_dom_attribute("data-ta-slot-pos")
                    if site in ad.text:
                        found = True
                        results.append(f"  關鍵字: {keyword}")
                        results.append(f"    找到廣告於Slot{_slot}-Pos{_pos} (嘗試第 {attempt} 次)")

                        # 滾動到廣告位置
                        driver.execute_script("arguments[0].scrollIntoView(true);", ad)
                        time.sleep(1)

                        # 截圖保存
                        screenshot_path = os.path.join(
                            screenshot_dir, f"{site}_{_slot}{_pos}_{keyword.replace(' ', '_')}_mobile.png"
                        )
                        driver.save_screenshot(screenshot_path)

                        results.append(f"    截圖保存位置: {screenshot_path}")
                        print(f"    關鍵字 '{keyword}' 找到目標網站 {site}於Slot{_slot}-Pos{_pos}，截圖已保存到 {screenshot_path}")
                        break

                if found:
                    break  # 如果找到，退出重試循環
                elif attempt < 6:
                    time.sleep(2)  # 每次重試間隔 2 秒

            if not found:
                results.append(f"  關鍵字: {keyword}")
                results.append(f"    未找到廣告 (已嘗試 6 次)")
                print(f"    關鍵字 '{keyword}' 未找到目標網站 {site} (已嘗試 6 次)")

        results.append("")  # 每個網站結果之間加空行

    # 關閉瀏覽器
    driver.quit()

    # 將結果保存到文件
    with open(result_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results) + "\n\n")

    print(f"檢查完成，結果已保存到 {result_file}")


# 使用範例：每個網站的關鍵字列表
site_keywords = {
    "www.paradise.com.hk": ["殯儀", "土葬","安息禮拜","綠色殯葬","遺體出口","天主教喪禮","喪禮"],
    "eternalhse.hk": ["殯儀", "院出","殯儀收費","道教喪禮","綠色殯葬","打齋","佛教喪禮","喪禮"],
    "gloryfuneral.com.hk": ["殯儀服務", "天主教喪禮","土葬","打齋","院出","遺體出口","基督教喪禮"],
    "memorialhse.com.hk": ["殯儀服務"]
}


google_ads_check_mobile(site_keywords)