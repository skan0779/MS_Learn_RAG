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
service = "microsoft-cloud"
date = "2024-11-07"

# 파일 불러오기
pdf_file_name = f"pdf_{service}_{date}.json"
with open(pdf_file_name, "r") as f:
    pdf_urls = json.load(f)

# 기본 설정
download_directory = f"/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG/PDF/{service}"
chrome_options = Options()
chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
})
chrome_service = Service("/opt/homebrew/bin/chromedriver")
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# PDF 다운로드 함수
def download_pdf(url):
    driver.get(url)
    initial_files = set(os.listdir(download_directory))
    downloaded = False

    # 첫 번째 유형의 다운로드 버튼을 찾고 클릭
    try:
        first_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'cr-icon-button#download[iron-icon="cr:file-download"]'))
        )
        first_button.click()
        downloaded = wait_for_download(initial_files)

    except Exception:
        pass

    # 첫 번째 버튼으로 다운로드가 완료되지 않은 경우 두 번째 버튼을 시도
    if not downloaded:
        try:
            second_button = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-bi-name="download-pdf"]'))
            )
            second_button.click()
            wait_for_download(initial_files)

        except Exception:
            pass

def wait_for_download(initial_files):
    # 다운로드가 시작될 때까지 기다림
    download_started = False
    while not download_started:
        time.sleep(2)
        current_files = set(os.listdir(download_directory))
        # 새로운 파일이 생성되는지 확인 (다운로드가 시작되었음을 의미)
        download_started = any(
            file.endswith(".crdownload") or file.endswith(".pdf") for file in current_files - initial_files
        )
        if download_started:
            print("Download started.")
    
    # 다운로드가 완료될 때까지 대기
    download_complete = False
    while not download_complete:
        time.sleep(5)
        current_files = set(os.listdir(download_directory))
        
        # 현재 다운로드 중인 파일 목록 확인 (임시 파일이 남아 있는지)
        downloading_files = [file for file in current_files - initial_files if file.endswith(".crdownload")]
        
        # 모든 파일이 .pdf로 바뀌었고 임시 파일이 없다면 다운로드 완료
        download_complete = len(downloading_files) == 0 and all(
            file.endswith(".pdf") for file in current_files - initial_files
        )
        
        if download_complete:
            print("Download completed.")
            return True
        else:
            print("Waiting for download to complete...")

    return False

# 각 URL에 대해 PDF 다운로드 실행
for pdf_url in pdf_urls:
    print(f"Visiting: {pdf_url}")
    download_pdf(pdf_url)
driver.quit()

# 결과 출력
print(f"####################################### Download Complete ################################################")
