import os
import duckdb
# from langchain.llms import Ollama
from langchain_community.llms import Ollama
from summary import *
from bdd import *


models = [
    # "qwen2:7b-instruct-q5_K_M",
    # "granite-code:20b-instruct-q8_0",
    # "phi3:14b-medium-128k-instruct-q5_K_M",
    # "llama3:8b-instruct-fp16",
    # "codestral:22b-v0.1-f16",
    # "codestral:22b-v0.1-q5_K_M",
    # "mistral:7b-instruct-v0.3-fp16",
    # "mixtral:latest",
    # "gemma:2b-instruct-v1.1-fp16",
    # "llava-llama3:8b-v1.1-fp16",
    # "phi3:14b-medium-4k-instruct-f16",
    # "starcoder2:3b-fp16",
    # "starcoder2:7b-fp16",
    # "starcoder2:15b-q6_K",
    "gemma:7b-instruct-v1.1-fp16",
    "dolphin-llama3:8b-256k-v2.9-fp16",
    "dolphin-llama3:8b-v2.9-fp16",
    "command-r:latest",
    "phi3:3.8b-mini-instruct-4k-fp16",
    "codestral:latest",
    "deepseek-coder-v2:16b-lite-instruct-q5_K_M"
]

for model in models:
        
    # llm
    llm = Ollama(
        base_url="http://192.168.8.116:11434",
        model=model,
        # temperature=0, 
    )
    print(model)

    # download vids
    # urls = ['https://www.youtube.com/watch?v=gKtXtMryLYE']
    # Utils.youtube_to_m4a(urls)

    # m4a to text
    # directory="./data/"
    # for filename in os.listdir(directory):
    #     if filename.endswith(".m4a"):
    #         file_path = os.path.join(directory, filename)
    #         print(f"Processing file: {file_path}")  # 

    #         text = Utils.m4a_to_text(file_path)

    #         Utils.insert_video_transcription(file_path, text, "testing123...")

    #     print("done ", filename)

    # # get transcripts
    conn = duckdb.connect('data/database.db')
    query = "SELECT * FROM video_transcription"
    df = conn.execute(query).fetchdf()
    transcriptions = df['transcription'].tolist()
    conn.close()
    print(f"Transcriptions: {len(transcriptions)}")

    # # summarize
    summaries = []
    summarizer = MapReduceDocSummarizer(llm=llm)
    for transcription in transcriptions:
        summary = summarizer.summary(transcription)
        summaries.append(summary["output_text"])
        print("done")


    # # log analysis 
    for summary in summaries:
        Utils.insert_llm_analysis(transcriptions[0], 
                                    str(llm), 
                                    summary, 
                                    "", f"Notes: testing123 amit aip 2000//50")
        print("Inserted summary!")