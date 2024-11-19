import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import os

# 개인 설정
service = "azure"
date = "2024-11-07"
download_directory = "/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG/URL"

# 파일 불러오기
url_file_name = f"url_{service}_{date}.json"
load_directory = "/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG/URL"
url_file_path = os.path.join(load_directory, url_file_name)
with open(url_file_name, "r") as f:
    leaf_urls = json.load(f)

# 드라이버 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_service = Service("/opt/homebrew/bin/chromedriver")
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# PDF URL 변수
PDF_URL_LIST = []
pdf_url_set = set()  # 중복을 방지하기 위한 집합

# PDF URL 함수
def collect_pdf_url(url):
    driver.get(url)
    try:
        pdf_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-bi-name="download-pdf"]'))
        )
        pdf_button.click()
        time.sleep(5)
        pdf_url = driver.current_url
        if pdf_url not in pdf_url_set:
            pdf_url_set.add(pdf_url)
            PDF_URL_LIST.append(pdf_url)
            print("Adding   : ", pdf_url)
    except Exception:
        pass

# PDF URL 작동
for url in leaf_urls:
    print("Visiting : ", url)
    try:
        collect_pdf_url(url)
    except Exception as e:
        continue
driver.quit()

# 파일 저장
current_date = datetime.now().strftime("%Y-%m-%d") 
pdf_file_name = f"pdf_{service}_{current_date}.json"
pdf_file_path = os.path.join(download_directory, pdf_file_name)
with open(pdf_file_path, "w") as f:
    json.dump(PDF_URL_LIST, f, indent=4)

# 결과 출력
print("######################## PDF URL List  ########################################################")
for pdf_url in PDF_URL_LIST:
    print(pdf_url)
print(f"####################### Number of Unique URLs : {len(PDF_URL_LIST)} ###################################################")
