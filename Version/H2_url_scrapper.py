import requests
from bs4 import BeautifulSoup

# URL 설정
url = "https://learn.microsoft.com/en-us/azure/"

# 페이지 요청
response = requests.get(url)
if response.status_code == 200:
    # 페이지 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # <div id="product-cards"> 안의 <a class="card-title has-external-link-indicator stretched-link"> 태그 찾기
    product_cards = soup.find('div', id="product-cards")
    if product_cards:
        links = product_cards.find_all('a', class_="card-title has-external-link-indicator stretched-link")
        
        # href와 다음 텍스트를 딕셔너리에 저장
        link_dict = {}
        for link in links:
            href = link.get('href')
            text = link.get_text(strip=True)
            if href and text and not href.startswith("/en-us/"):
                link_dict[text] = url + href

    else:
        # print("Could not find the specified <div> with id='product-cards'.")
        pass
else:
    # print("Failed to retrieve the page.")
    pass