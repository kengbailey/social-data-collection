from datetime import datetime
from minio import Minio
import psycopg2
import yt_dlp
import os


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
    os.remove(file_path)  # cleanup

    print("File uploaded successfully to MinIO")
    return f"s3://{bucket_name}/{object_name}"

# Fetch video information
def get_video_info(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forcejson': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        
        # Convert upload_date from YYYYMMDD to YYYY-MM-DD
        upload_date_str = info['upload_date']        
        upload_date = datetime.strptime(upload_date_str, "%Y%m%d").date()
        
        video_info = {
            'video_id': info['id'],
            'title': info['title'],
            'author_name': info['uploader'],
            'channel_id': info['channel_id'],
            'channel_url': info['channel_url'],
            'upload_date': upload_date,
        }
        
        return video_info

# Log to databse
def log_to_db(video_info, s3_path):
    try:
        # Construct the SQL query
        query = """INSERT INTO youtube_audio (video_id, title, author_name, channel_id, channel_url, upload_date, s3_path) VALUES (%s, %s, %s, %s, %s, %s, %s);"""
        data = (video_info['video_id'], video_info['title'], video_info['author_name'], video_info['channel_id'], video_info['channel_url'], video_info['upload_date'], s3_path)

        # Execute the query
        cur.execute(query, data)

        # Commit your changes in the database
        conn.commit()
        print("Data logged successfully to PostgreSQL")

    except Exception as e:
        print(f"An error occurred while logging to the database: {e}")



if __name__ == "__main__":
    url = 'https://www.youtube.com/watch?v=uvsNJ9k9zdc'
    file_path = youtube_to_m4a(url)
    s3_path = upload_to_minio(file_path)
    video_info = get_video_info(url)
    log_to_db(video_info, s3_path)
    print("Done!")

