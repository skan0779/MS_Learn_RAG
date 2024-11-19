import os
import PyPDF2
import tiktoken

# 개인 설정
data_path = "/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG/PDF"
new_folder = "/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG/Preprocessed_PDF"
max_file_size_mb = 500
max_tokens = 5000000
model = "cl100k_base"
                                
# 폴더 생성
if not os.path.exists(new_folder):
    os.makedirs(new_folder)

# 토큰 계산 함수
def count_tokens(text):
    encoding = tiktoken.get_encoding(model)
    tokens = encoding.encode(text)
    return len(tokens)

# PDF 분할 함수
def split_pdf(file_path, split_by_tokens=False):
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        # 파일 크기에 따른 분할수 계산
        num_splits = int(os.path.getsize(file_path) / (1024 * 1024) // max_file_size_mb) + 1
        split_size = max(1, num_pages // num_splits)
        part = 1

        for start_page in range(0, num_pages, split_size):
            end_page = min(start_page + split_size, num_pages)
            writer = PyPDF2.PdfWriter()
            
            # 페이지 단위로 추가
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            # 파일 저장
            split_file_name = os.path.join(new_folder, f"{base_name}_part{part}.pdf")
            with open(split_file_name, "wb") as split_file:
                writer.write(split_file)
            
            # 분할된 파일의 크기 및 토큰 개수 검사
            split_file_size_mb = os.path.getsize(split_file_name) / (1024 * 1024)
            split_file_text = ""
            with open(split_file_name, "rb") as sf:
                split_reader = PyPDF2.PdfReader(sf)
                for page in split_reader.pages:
                    split_file_text += page.extract_text() or ""
            token_count = count_tokens(split_file_text)
            print(f"Created: {split_file_name} - Size: {split_file_size_mb:.2f} MB, Tokens: {token_count}")
            
            # 분할수 재조정
            if split_file_size_mb > max_file_size_mb or token_count > max_tokens:
                print(f"Warning: {split_file_name} exceeds limits. Adjusting split size.")
                split_pdf(split_file_name, split_by_tokens=True)
                os.remove(split_file_name)
            part += 1

# 파일 분류 및 분할
for file_name in os.listdir(data_path):
    file_path = os.path.join(data_path, file_name)
    
    if os.path.isfile(file_path) and file_name.lower().endswith('.pdf'):
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_size_mb > max_file_size_mb:
            split_pdf(file_path)
        else:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "".join([page.extract_text() or "" for page in reader.pages])
                token_count = count_tokens(text)
                
                if token_count > max_tokens:
                    split_pdf(file_path, split_by_tokens=True)
                else:
                    new_file_path = os.path.join(new_folder, file_name)
                    with open(file_path, "rb") as original_file, open(new_file_path, "wb") as new_file:
                        new_file.write(original_file.read())
                    print(f"Copied: {new_file_path}")

