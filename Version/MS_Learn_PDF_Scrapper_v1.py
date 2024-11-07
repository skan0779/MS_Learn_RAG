from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from collections import deque

# ChromeDriver 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저를 숨겨서 실행
chrome_service = Service("/opt/homebrew/bin/chromedriver")  # ChromeDriver 경로 지정

# PDF URL 리스트와 방문 URL 큐 및 집합
PDF_URL_LIST = []
visited_urls = set()
target_url = deque()  # 큐를 사용해 순차적으로 URL을 방문

# 웹 드라이버 실행
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# 'product-cards' 내의 모든 링크를 큐에 추가하는 함수
def add_links_to_queue(url):
    driver.get(url)
    try:
        # 'product-cards' 내 모든 <a> 태그 href 수집하여 큐에 추가
        product_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "product-cards"))
        )
        links = product_cards.find_elements(By.TAG_NAME, "a")
        
        for link in links:
            next_url = link.get_attribute("href")
            if next_url and next_url not in visited_urls:
                target_url.append(next_url)
                visited_urls.add(next_url)
                print("Added to queue:", next_url)
    except Exception:
        print(f"No 'product-cards' div found or other error.")
        pass

# PDF 버튼을 클릭하고 PDF URL을 수집하는 함수
def collect_pdf_url():
    try:
        pdf_button = WebDriverWait(driver, 23).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-bi-name="download-pdf"]'))
        )
        pdf_button.click()
        
        # 새 탭이 열리도록 대기
        time.sleep(10)

        # PDF URL 가져오기
        pdf_url = driver.current_url
        PDF_URL_LIST.append(pdf_url)
        print("PDF URL added:", pdf_url)
    except Exception:
        print("No 'Download PDF' button found or other error.")
        pass

# 시작 URL의 모든 링크를 큐에 추가
start_url = "https://learn.microsoft.com/en-us/azure/networking/"
add_links_to_queue(start_url)

# 큐의 각 URL을 방문하고 PDF URL을 수집하거나 하위 링크를 추가
while target_url:
    current_url = target_url.popleft()
    driver.get(current_url)
    print("Visiting:", current_url)

    # PDF 버튼이 있으면 수집하고, 없으면 하위 링크를 큐에 추가
    try:
        pdf_button = driver.find_element(By.CSS_SELECTOR, 'button[data-bi-name="download-pdf"]')
        collect_pdf_url()
    except:
        add_links_to_queue(current_url)

# 드라이버 종료
driver.quit()

# 결과 출력
print("###########################################################################")
for pdf_url in PDF_URL_LIST:
    print(pdf_url)
