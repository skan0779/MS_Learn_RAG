from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import deque
import json
import datetime

# 개인 설정
    # Azure : azure
    # Microsoft Industry Clouds : industry
    # Microsoft Cloud : microsoft-cloud
    # Microsoft Copliot : copilot
    # Microsoft Copliot Studio : microsoft-copilot-studio
    # OpenAPI : openapi
service = "azure"
start_url = f"https://learn.microsoft.com/en-us/{service}/"

# ChromeDriver 설정
chrome_options = Options()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--disable-gpu") 
chrome_options.add_argument("--no-sandbox") 
# chrome_options.add_argument("--disable-dev-shm-usage") 
chrome_service = Service("/opt/homebrew/bin/chromedriver")
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# 변수 설정
visited_urls = set()
target_url = deque()
leaf_urls = set()

# 링크 추가 함수
def add_links_to_queue(url):
    driver.get(url)
    try:
        try:
            product_cards = WebDriverWait(driver, 1).until( 
                EC.presence_of_element_located((By.ID, "product-cards"))
            )
            links = product_cards.find_elements(By.TAG_NAME, "a")
        except Exception:
            leaf_urls.add(url)
            print("Adding   : ", url)
            return
        has_child_links = False
        for link in links:
            next_url = link.get_attribute("href")
            if next_url and next_url not in visited_urls:
                target_url.append(next_url)
                visited_urls.add(next_url)
                has_child_links = True
        if not has_child_links:
            leaf_urls.add(url)
            print("Adding   : ", url)
    except Exception as e:
        leaf_urls.add(url)
        print("Adding   : ", url)

# 링크 추가 실행
target_url.append(start_url)
visited_urls.add(start_url)
while target_url:
    current_url = target_url.popleft()
    print("Visiting : ", current_url)
    try:
        add_links_to_queue(current_url)
    except Exception as e:
        continue
driver.quit()

# 파일 저장
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
file_name = f"url_{service}_{current_date}.json"
with open(file_name, "w") as f:
    json.dump(list(leaf_urls), f)

# 결과 출력
print("######################## Target URL List ########################################################")
for url in sorted(leaf_urls):
    print(url)
print(f"####################### Number of Targets : {len(leaf_urls)} ###################################################")
