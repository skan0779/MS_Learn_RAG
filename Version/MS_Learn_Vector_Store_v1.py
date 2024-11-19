import math
import time
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import AzureOpenAI

# 개인 설정
project_path = "/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG"
data_path = "/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG/Example"
assistant_name = "MS Learn Expert Assistant v3"
model_name = "gpt-4o-mini"
vs_name = "MS Learn Expert VS v3"
system_message = """
    You are a specialized assistant with in-depth knowledge in Microsoft technologies, trained to provide expert guidance on topics covered in MS Learn PDF documents.
    Your role is to assist users by drawing from specific details within these documents to answer questions about Azure, AI, cloud services, and other relevant Microsoft tools and best practices.
    Answer concisely, provide actionable insights, and cite concepts or recommendations directly related to the MS Learn materials wherever applicable.
    If a user query is outside the scope of these documents, politely inform the user of your focus on MS Learn content. 
    When generating your answer, please explain your thoughts in detail, step by step, using the content provided.
    If you don't know the answer, just say you don't know.
    Please answer in Korean.
"""
chunk_size = 1500
chunk_overlap = 100

# 로깅 설정
if not os.path.exists('logs'):
    os.makedirs('logs')

log_filename = f'{project_path}/logs/create_vector_store_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 메인 함수 정의
def main():
    # 환경변수 설정
    load_dotenv(dotenv_path=f"{project_path}/.env")

    # Clinet 생성
    client = AzureOpenAI(
        api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    # Assistant 생성
    assistant = client.beta.assistants.create(
        name = assistant_name,
        model = model_name,
        instructions = system_message,
        tools = [{"type": "file_search"}],
    )

    # Vector store 생성
    vector_store = client.beta.vector_stores.create(name = vs_name)
    logger.info(f"Created vector store with ID: {vector_store.id}")

    # 파일 준비
    folder_path = f'{data_path}'
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    file_streams = [open(path, "rb") for path in file_paths]

    # 파일 업로드
    def batch_upload_files(client, vector_store_id, file_streams, batch_size=2, delay=60, max_retries=3):
        while True:
            try:
                # Retrieve the initial state of the vector store
                vector_store = client.beta.vector_stores.retrieve(vector_store_id=vector_store_id)
                
                if vector_store.status != 'completed':
                    logger.info(f"Vector store is {vector_store.status}. Waiting for {delay} seconds...")
                    time.sleep(delay)
                    continue
                
                total_files = len(file_streams)
                upload_files = vector_store.file_counts.total
                remain_files = total_files - upload_files
                
                if remain_files <= 0:
                    logger.info("File Upload Complete.")
                    break
                
                num_batches = math.ceil(remain_files / batch_size)
                
                logger.info(f"Total files: {total_files}")
                logger.info(f"Files already uploaded: {upload_files}")
                logger.info(f"Remaining files to upload: {remain_files}")
                logger.info(f"Number of batches: {num_batches}")
                
                for i in range(num_batches):
                    start_idx = upload_files + (i * batch_size)
                    end_idx = min(upload_files + ((i + 1) * batch_size), total_files)
                    current_batch = file_streams[start_idx:end_idx]
                    
                    logger.info(f"\n Uploading batch {i+1}/{num_batches} (Files {start_idx+1} to {end_idx})")
                    
                    try:
                        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                            vector_store_id=vector_store_id, 
                            files=current_batch,
                            chunking_strategy={
                                "type": "static",
                                "static": {
                                    "max_chunk_size_tokens": chunk_size,
                                    "chunk_overlap_tokens": chunk_overlap
                                }
                            }
                        )
                        logger.info(f"Batch {i+1} upload complete. Status: {file_batch.status}")
                    except Exception as e:
                        logger.error(f"Error uploading batch {i+1}: {str(e)}")
                        logger.info(f"Waiting for {delay} seconds to check vector store status...")
                        time.sleep(delay)
                    
                    # Check vector store status after each batch
                    status_check_retries = 0
                    while status_check_retries < max_retries:
                        try:
                            vector_store = client.beta.vector_stores.retrieve(vector_store_id=vector_store_id)
                            if vector_store.status == 'completed':
                                logger.info(f"Vector store status after batch {i+1}: {vector_store.status}")
                                logger.info(f"Total files in vector store: {vector_store.file_counts.total}")
                                break
                            else:
                                logger.info(f"Vector store status is {vector_store.status}. Waiting for {delay} seconds...")
                                time.sleep(delay)
                        except Exception as e:
                            status_check_retries += 1
                            logger.error(f"Error checking vector store status: {str(e)}")
                            if status_check_retries >= max_retries:
                                raise
                            logger.info(f"Retrying status check in {delay} seconds... (Attempt {status_check_retries}/{max_retries})")
                            time.sleep(delay)
                
                logger.info("\n ################## All batches uploaded and processed ######################")
                break
            
            except Exception as e:
                logger.error(f"An error occurred during the upload process: {str(e)}")
                logger.info(f"Retrying the entire process in {delay} seconds...")
                time.sleep(delay)

    vector_store_id = vector_store.id
    batch_upload_files(client, vector_store_id, file_streams)

    # Assistant 업데이트
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    logger.info(f"Updated assistant {assistant.id} with vector store {vector_store_id}")

    # Stream 종료
    for file_stream in file_streams:
        file_stream.close()

# 메인 함수 실행
if __name__ == "__main__":
    main()

    # 백그라운드 실행 & 출력/로그 파일 저장 (optional)
    # nohup python create_vector_store.py > logs/console_output.log 2>&1 &


# assistant.id = asst_ivwlVIo2XBCqJ5Y0ddCRXdw0
# vector_store_id = vs_MozvP9dMUfttJqztYbTSwQBp
