from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
from minio import Minio
import os
from sse_starlette.sse import EventSourceResponse
import asyncio

# FastiAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust this to match your frontend URL
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

class VideoURL(BaseModel):
    url: str

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

@app.post("/download")
async def download_audio(video: VideoURL, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_video, video.url)
    return {"message": "Download started"}

def process_video(url):
    # Download the audio
    file_path = youtube_to_m4a(url)
    upload_to_minio(file_path)

    # Send message to UI (implementation depends on your frontend setup)
    global task_complete
    task_complete = True

def upload_to_minio(file_path):
    bucket_name = "social-data"
    object_name = os.path.basename(file_path)
    
    minio_client.fput_object(bucket_name, object_name, file_path)
    os.remove(file_path)  # Clean up the local file after upload
    print("File uploaded successfully to MinIO")

@app.get("/status")
async def status_stream(request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            # Check if the task is complete
            if task_complete:
                yield {
                    "event": "message",
                    "data": "Audio file uploaded to MinIO"
                }
                break

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())