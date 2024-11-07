from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import deque

# ChromeDriver 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_service = Service("/opt/homebrew/bin/chromedriver")

# 방문 URL 큐 및 집합
visited_urls = set()
target_url = deque()
leaf_urls = set()  # 중복 제거를 위해 set으로 변경

# 웹 드라이버 실행
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# 'product-cards' 내의 모든 링크를 큐에 추가하는 함수
def add_links_to_queue(url):
    driver.get(url)
    try:
        # 'product-cards' 내 모든 <a> 태그 href 수집하여 큐에 추가
        product_cards = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.ID, "product-cards"))
        )
        links = product_cards.find_elements(By.TAG_NAME, "a")
        
        # 하위 링크가 있으면 target_url에 추가
        has_child_links = False
        for link in links:
            next_url = link.get_attribute("href")
            if next_url and next_url not in visited_urls:
                target_url.append(next_url)
                visited_urls.add(next_url)
                has_child_links = True

        # 하위 링크가 없다면 최하위 URL로 간주하고 leaf_urls에 추가
        if not has_child_links:
            leaf_urls.add(url)
                
    except Exception:
        # 'product-cards'가 없으면 최하위 URL로 간주하고 leaf_urls에 추가
        leaf_urls.add(url)

# 시작 URL의 모든 링크를 큐에 추가
# start_url = "https://learn.microsoft.com/en-us/azure/"
start_url = "https://learn.microsoft.com/en-us/industry/"
# start_url = "https://learn.microsoft.com/en-us/azure/networking/"

add_links_to_queue(start_url)

# 큐의 각 URL을 방문하고 하위 링크를 추가                                                                    
while target_url:
    current_url = target_url.popleft()
    add_links_to_queue(current_url)

# 드라이버 종료
driver.quit()

# 결과 출력: 최하위 URL들만 출력 (중복 제거됨)
print("######################## Target URL List ########################################################")
for url in sorted(leaf_urls):
    print(url)
print(f"####################### Number of Targets : {len(leaf_urls)} ###################################################")

