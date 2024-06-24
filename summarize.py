import duckdb
from langchain.llms import Ollama
from analysis import *
from bdd import *



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
    insert_llm_analysis(transcription, 
                                str(llm), 
                                '\n\n'.join(segment_summaries), 
                                "", f"Notes: ")