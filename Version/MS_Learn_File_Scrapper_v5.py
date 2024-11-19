from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os

# 변수 설정
service = "azure"
date = "2024-11-07"
download_directory = f"/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG/PDF/{service}"

# 파일 불러오기
pdf_file_name = f"pdf_{service}_{date}.json"
load_directory = "/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG/URL"
pdf_file_path = os.path.join(load_directory, pdf_file_name)
with open(pdf_file_path, "r") as f:
    pdf_urls = json.load(f)

# 드라이버 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
})
chrome_service = Service("/opt/homebrew/bin/chromedriver")
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# 다운로드 대기 함수
def wait_for_download(timeout=90):
    start_time = time.monotonic()
    while True:
        time.sleep(5)
        files = os.listdir(download_directory)
        download_complete = all(file.endswith(".pdf") and not file.endswith(".crdownload") for file in files)
        if download_complete:
            return True
        if time.monotonic() - start_time > timeout:
            return False

# 다운로드 함수
def download_pdf(url):
    driver.get(url)
    download_started = False

    # 첫 번째 페이지 유형
    try:
        first_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'cr-icon-button#download[iron-icon="cr:file-download"]'))
        )
        first_button.click()
        download_started = True
    except Exception as e:
        pass

    # 두 번째 페이지 유형
    if not download_started:
        try:
            second_button = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-bi-name="download-pdf"]'))
            )
            second_button.click()
            download_started = True
        except Exception as e:
            pass

    # 다운로드가 완료 대기
    if download_started:
        if not wait_for_download(timeout=90):
            print("Moving to next URL")

# 다운로드 실행
for pdf_url in pdf_urls:
    print(f"Visiting: {pdf_url}")
    download_pdf(pdf_url)
driver.quit()

# 결과 출력
print(f"####################################### Download Complete ################################################")
