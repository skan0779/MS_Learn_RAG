import os
import fitz
import tiktoken
from typing import List

# 개인 설정
folder_path = "/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG/PDF"
# model_name = "gpt-4"
model_name = "cl100k_base"
USD = 1405.45

# tiktoken 설정
encoding = tiktoken.get_encoding(model_name)

# 텍스트 토큰 수 계산 함수
def num_tokens_from_string(text: str) -> int:
    tokens = encoding.encode(text, disallowed_special=())
    return len(tokens)

# 파일의 각 페이지 토큰 수 계산 함수
def get_token_counts_from_pdf(file_path: str) -> List[int]:
    token_counts = []
    with fitz.open(file_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            page_text = page.get_text()
            token_count = num_tokens_from_string(page_text)
            token_counts.append(token_count)
    return token_counts

# 토큰 수 계산
file_paths = [
    os.path.join(folder_path, f)
    for f in os.listdir(folder_path)
    if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(folder_path, f))
]
all_token_counts = {}
for file_path in file_paths:
    file_name = os.path.basename(file_path)
    token_counts = get_token_counts_from_pdf(file_path)
    all_token_counts[file_name] = token_counts
    print(f"'{file_name}' : {sum(token_counts)} tokens")

# 파일 크기 계산
total_size_bytes = sum(
    os.path.getsize(os.path.join(folder_path, f))
    for f in os.listdir(folder_path)
    if f.lower().endswith(".pdf")
)
total_size_gb = total_size_bytes / (1024 ** 3)

# 비용 계산
total_tokens = sum(sum(counts) for counts in all_token_counts.values())
token_cost = total_tokens * (0.13/1000000) * USD
if total_size_gb <= 1:
    storage_cost = 0
else:
    extra_gb = total_size_gb - 1
    storage_cost = extra_gb * 0.1 * USD
cost = token_cost + storage_cost

# 결과 출력
print(f"""
      ########################### Calculate Complete ##############################
      Expected Token Cost: {token_cost:.2f} KRW
      Expected Storage Cost: {storage_cost:.2f} KRW
      Expected Total Cost: {cost:.2f} KRW
      #############################################################################
      """)