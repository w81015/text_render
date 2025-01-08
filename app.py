from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def setup_driver():
    """設置 Selenium 瀏覽器配置"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 無頭模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

@app.route('/scrape', methods=['POST'])
def scrape():
    """接收請求並爬取 Google 搜尋結果"""
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({'error': '缺少查詢參數'}), 400

    try:
        driver = setup_driver()
        url = f"https://www.google.com/search?q={query}"
        driver.get(url)

        # 爬取搜尋結果標題和網址
        results = []
        elements = driver.find_elements(By.CSS_SELECTOR, "div.yuRUbf a")
        for elem in elements[:10]:  # 只抓前 10 個結果
            title = elem.find_element(By.TAG_NAME, "h3").text
            link = elem.get_attribute("href")
            results.append({"title": title, "link": link})

        driver.quit()
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
