from minio import Minio
import whisper
import psycopg2

import os
import openai
from openai import Whisper

# MinIO client setup
minio_client = Minio("192.168.8.116:9000",
    access_key="NFOMw4IwCgi1UZ9LYMoC",
    secret_key="ilGeAyVuFPMuehANtq2g345wwDMGYG2YevQIIK8v",
    secure=False,
)

# Establish a connection to the database
conn = psycopg2.connect(
    database="social-data", 
    user='syran', 
    password='sk8erb01', 
    host='192.168.8.116')
cur = conn.cursor()

# TODO
def transcribe_audio_local(file_path, model_name='base.en'):
    model = whisper.load_model(model_name)
    result = model.transcribe(file_path)
    return result


# TODO
def transcribe_audio(file):
    # Load your API key from an environment variable
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Initialize the Whisper client
    whisper = Whisper()

    try:
        # Transcribe the audio file
        transcript = whisper.transcribe(file)

        return transcript['text']

    except Exception as e:
        print("An error occurred:", str(e))


# TODO
def log_to_db(result):
    cur.execute("INSERT INTO whisper (text, language, words, duration, timestamp) VALUES (%s, %s, %s, %s, %s)",
        (result['text'], result['language'], result['words'], result['duration'], result['timestamp']))
    conn.commit()
    print("Inserted into DB")


if __name__ == "__main__":
    # fetch audio
    file_path = '/Users/syran/Documents/GitHub/social-data-collection/scripts/data/test.m4a'

    # transcribe audio
    result = transcribe_audio(file_path)

    # store in database
    print(result)