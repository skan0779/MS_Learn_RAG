import os
import json
import time
from openai import AzureOpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv(dotenv_path = "/Users/skan/Desktop/AI_Prototyping_Team/MS_Azure_RAG/.env")

# Client 생성
client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
)

# Thread 생성
thread = client.beta.threads.create()

# Message 생성
message = client.beta.threads.messages.create(
    thread_id = thread.id,
    role = "user",
    content = "copliot 사용법을 간략히 설명해 주세요"
)

# Thread 실행
run = client.beta.threads.runs.create(
    thread_id = thread.id,
    assistant_id = "asst_ivwlVIo2XBCqJ5Y0ddCRXdw0"
)

# 실행 상태 체크
while run.status in ['queued', 'in_progress', 'cancelling']:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(
        thread_id = thread.id,
        run_id = run.id
    )
if run.status == 'completed':
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for message in messages:
        print(message.content)
elif run.status == 'requires_action':
    print("The assistant requires additional actions to complete.")
else:
    print(f"Run status: {run.status}")

