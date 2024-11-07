from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
# 변수호출
from H2_url_scrapper import link_dict

url = "https://learn.microsoft.com/en-us/azure/app-service/"

# ChromeDriver 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저를 숨겨서 실행
chrome_service = Service("/opt/homebrew/bin/chromedriver")  # ChromeDriver 경로 지정

# 웹 드라이버 실행
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
driver.get(url)

# Download PDF 버튼을 찾고 클릭
try:
    # 버튼이 로드될 때까지 잠시 대기
    time.sleep(2)
    
    # Download PDF 버튼 찾기
    pdf_button = driver.find_element(By.CSS_SELECTOR, 
        'button[data-bi-name="download-pdf"]')
    pdf_button.click()

    # 새 탭이 열리도록 대기
    time.sleep(2)

    # PDF URL 가져오기
    pdf_url = driver.current_url
    print(pdf_url)
    
finally:
    # 드라이버 종료
    driver.quit()
