from langchain_community.llms import Ollama
from dataclasses import dataclass
import psycopg2

# Ollama models
models = [
    'gemma2:27b-instruct-q5_K_M',
    'gemma2:9b-instruct-q5_K_M',
    'deepseek-coder-v2:16b-lite-instruct-q5_K_M',
    'qwen2:7b-instruct-q5_K_M',
    'granite-code:20b-instruct-q8_0',
    'llama3:8b-instruct-fp16',
    'phi3:14b-medium-128k-instruct-q5_K_M',
    'codestral:22b-v0.1-f16',
    'codestral:22b-v0.1-q5_K_M',
    'mistral:7b-instruct-v0.3-fp16',
    'mixtral:latest',
    'gemma:2b-instruct-v1.1-fp16',
    'llava-llama3:8b-v1.1-fp16',
    'phi3:14b-medium-4k-instruct-f16',
    'starcoder2:3b-fp16',
    'starcoder2:7b-fp16',
    'gemma:7b-instruct-v1.1-fp16',
    'starcoder2:15b-q6_K',
    'dolphin-llama3:8b-256k-v2.9-fp16',
    'dolphin-llama3:8b-v2.9-fp16',
    'command-r:latest',
    'phi3:3.8b-mini-instruct-4k-fp16',
    'codestral:latest',
    'llama3:70b'
]


# Establish a connection to the database
conn = psycopg2.connect(
    database="social-data", 
    user='syran', 
    password='sk8erb01', 
    host='192.168.8.116')
cur = conn.cursor()


@dataclass
class Comment:
    author: str
    text: str

# Fetch comments from database
def fetch_comments(video_id):
    postgreSQL_select_Query = "SELECT author, text FROM youtube_comments WHERE video_id=%s"
    cur.execute(postgreSQL_select_Query, (video_id,))
    comment_records = cur.fetchall()
    return [Comment(author=row[0], text=row[1]) for row in comment_records]
     

if __name__ == "__main__":

    # fetch comments from database
    video_id=''
    comments = fetch_comments(video_id)

    # set llm system message
    model = 'mistral:7b-instruct-v0.3-fp16'
    llm = Ollama(
            base_url="http://192.168.8.116:11434",
            model=model,
            # system=None,
            temperature=0.8, # 0-2
            top_k=40, # 0-100
            top_p=0.9, # 0-1
        )

    # process comments
    for comment in comments:
        result = llm.invoke("Tell me a joke")
        print(result)

    # cleanup
    cur.close()
    conn.close()