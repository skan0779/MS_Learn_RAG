# AICT Future TF 파견 프로젝트(2)
## [Project] RAG for MS Learn document

### Step 1 : scrap all MS product URL
### Step 2 : scrap all PDF URL for target MS product
### Step 3 : scrap all PDF Files from valid PDF URLs
### Step 4 : deploy RAG system from MS Azure AI Studio with GPT4

## [Flow]
#### Step 1 : run MS_Learn_URL_Scrapper_v2.py (지정한 MS Product에 관련된 document 파일이 있는 모든 url을 json 파일로 저장)
#### Step 2 : run MS_Learn_PDF_Scrapper_v2.py (pdf 파일의 url을 json 파일로 저장)
#### Step 2 : run MS_Learn_File_Scrapper_v4.py (다운로드 가능한 모든 pdf 파일을 저장)
