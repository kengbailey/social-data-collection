import duckdb
from langchain import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import Ollama
from langchain import PromptTemplate
import sqlite3
import pandas as pd
from datetime import datetime

import bdd

# Below is a transcript of a daily youtube show that covers the opening of the financial markets.
# The show is called the "Morning Open" and the presenter is named Amit.
map_prompt = """
Summarize the main points and their comprehensive explanations from below text, presenting them under appropriate headings. Use various Emoji to symbolize different sections, and format the content as a cohesive paragraph under each heading. Ensure the summary is clear, detailed, and informative, reflecting the executive summary style found in news articles. Avoid using phrases that directly reference 'the script provides' to maintain a direct and objective tone.
"{text}"
SUMMARY:
"""
map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])

# Below are segmented summaries of a daily youtube show that covers the opening of the financial markets.
# The show is called the "Morning Open" and the presenter is named Amit.
combine_prompt = """
Write a complete summary of the following text.
maintain a direct and objective tone.
"{text}"
SUMMARY:
"""
combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])

def segment_large_text(transcript, num_segments=4, overlap=20):

    part_size = len(transcript) // num_segments
    segments = [transcript[i: i + part_size] for i in range(0, len(transcript), part_size)]

    if len(segments) > num_segments:
        segments[-1] += ''.join(segments[num_segments:])
        del segments[num_segments:]

    return segments

def split_segment(segment):
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=4000, chunk_overlap=100)
    return text_splitter.create_documents([segment])

def summarize_segment(segment_docs, llm):
    summary_chain = load_summarize_chain(llm=llm,
                                         chain_type='map_reduce',
                                         map_prompt=map_prompt_template,
                                         combine_prompt=combine_prompt_template,
                                        )
    return summary_chain.run(segment_docs)




if __name__ == '__main__':


    # llm
    llm = Ollama(
        base_url="http://192.168.8.116:11434",
        model="mixtral",
        temperature=0, 
    )


    # get transcripts
    conn = duckdb.connect('data/database.db')
    query = "SELECT * FROM video_transcription where id=2"
    df = conn.execute(query).fetchdf()
    transcriptions = df['transcription'].tolist()
    conn.close()
    print(f"Transcriptions: {len(transcriptions)}")

    # summarize
    for transcription in transcriptions:
        segment_summaries = []
        segments = segment_large_text(transcription, num_segments=3)
        print(f"Segments: {len(segments)}")
     
        for i,segment in enumerate(segments):
            segment_docs = split_segment(segment)

            segment_summaries.append(summarize_segment(segment_docs))
            
            print(f"Segment {i+1} done")

        # log analysis 
        bdd.insert_llm_analysis(transcription, 
                                 str(llm), 
                                 '\n\n'.join(segment_summaries), 
                                 "", f"Notes: ")