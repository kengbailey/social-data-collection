from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
from minio import Minio
from operator import attrgetter
import tempfile
import whisper

import os


# FastiAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MinIO client setup
minio_client = Minio("192.168.8.116:9000",
    access_key="NFOMw4IwCgi1UZ9LYMoC",
    secret_key="ilGeAyVuFPMuehANtq2g345wwDMGYG2YevQIIK8v",
    secure=False,
)


####################
## Youtube to M4a
####################

class VideoURL(BaseModel):
    url: str

# Endpoint - /download
@app.post("/download")
async def download_audio(video: VideoURL, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_video, video.url)
    return {"message": "Download started..."}

def process_video(url):
    file_path = youtube_to_m4a(url)
    upload_to_minio(file_path)

# Download the audio
def youtube_to_m4a(url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': './data/'+'%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # Return the filename of the downloaded file
    files = os.listdir('./data')
    return os.path.join('./data', files[-1])

# Upload to MinIO
def upload_to_minio(file_path):
    bucket_name = "social-data"
    object_name = os.path.basename(file_path)
    
    minio_client.fput_object(bucket_name, object_name, file_path)
    os.remove(file_path)  # Clean up the local file after upload
    print("File uploaded successfully to MinIO")

# Get latest downloads
@app.get("/get_latest")
async def get_latest_bucket_items():
    bucket_name = "social-data"
    try:
        items = get_latest_items(bucket_name)
        return {
            "bucket": bucket_name, 
            "items": [item._object_name for item in items],
            "items_last_modified": [item._last_modified for item in items]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_latest_items(bucket_name, num_items=5):
    objects = minio_client.list_objects(bucket_name)
    sorted_objects = sorted([obj for obj in objects], key=attrgetter('last_modified'), reverse=True)
    return sorted_objects[:num_items]


####################
## Audio To Text
####################

class AudioURL(BaseModel):
    s3_url: str

@app.post("/transcribe")
async def transcribe_audio(audio: AudioURL, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_video, audio.url)
    return {"message": "Download started..."}

def process_audio(url):
    # fetch audio from s3
    temp_file = fetch_s3_file(url)
    # transcribe audio
    transcribed_audio = transcribe_audio(temp_file)
    # log transcription to database
    # TODO: finish this function 

# Fetches a file from an S3 URL and saves it to a temporary directory
def fetch_s3_file(s3_url: str) -> str:
    # Extract bucket name and object key from the S3 URL
    bucket_name, object_key = s3_url[5:].split("/", 1)  

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = f"{temp_dir}/{object_key.split('/')[-1]}"
        minio_client.download_object(bucket_name, object_key, temp_file_path)
        return temp_file_path

# Transcribes an audio file locally using OpenAI Whisper.
def transcribe_audio(audio_file_path: str, model_name="base.en") -> str:
    model = whisper.load_model(model_name)
    audio = whisper.load_audio(audio_file_path)
    result = model.transcribe(audio)

    return result["text"]


