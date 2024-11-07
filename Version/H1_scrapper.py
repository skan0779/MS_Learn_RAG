import requests
from bs4 import BeautifulSoup

# URL 설정
url = "https://learn.microsoft.com/en-us/docs/"

# STEP 1: 페이지 요청 및 파싱
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# STEP 2: <a class="bar-link has-inner-focus"> 태그에서 텍스트 추출
links = soup.find_all('a', class_='bar-link has-inner-focus')
text_data = [link.get_text(strip=True) for link in links]

# STEP 3: href 속성 추출
href_list = ["https://learn.microsoft.com" + link.get('href') for link in links if link.get('href') is not None]

# STEP 4: 텍스트와 href를 이차원 리스트로 결합
H1_list = [[text_data[i], href_list[i]] for i in range(min(len(text_data), len(href_list)))]

# 결과 출력
for H1 in H1_list:
    print(H1)