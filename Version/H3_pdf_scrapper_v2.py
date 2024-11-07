from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 변수 호출
from H2_url_scrapper import link_dict

# ChromeDriver 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저를 숨겨서 실행
chrome_service = Service("/opt/homebrew/bin/chromedriver")  # ChromeDriver 경로 지정

# PDF URL을 저장할 새로운 딕셔너리 생성
pdf_urls = {}

# 웹 드라이버 실행
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# link_dict의 모든 value에 대해 PDF URL 수집
for key, url in link_dict.items():
    try:
        driver.get(url)  # 현재 URL로 이동
        
        # Download PDF 버튼의 존재 여부 확인
        try:
            pdf_button = WebDriverWait(driver,25).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-bi-name="download-pdf"]'))
            )
            pdf_button.click()

            # 새 탭이 열리도록 대기
            time.sleep(10)

            # PDF URL 가져오기
            pdf_url = driver.current_url
            pdf_urls[key] = pdf_url if pdf_url else ""

        except Exception as e:
            pdf_urls[key] = "None"

    except Exception as e:
        pdf_urls[key] = "None"

# 드라이버 종료
driver.quit()

# 딕셔너리의 내용을 출력
print("######################## Target URL List  ####################################################")
for key, value in pdf_urls.items():
    print(f"{key}: {value}")
print(f"####################### Number of Targets ###############################################")
