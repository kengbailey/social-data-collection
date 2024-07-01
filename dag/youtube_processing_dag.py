# from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
# from airflow.operators.python import PythonVirtualenvOperator
# from datetime import datetime, timedelta
# from minio import Minio
# import psycopg2
# import yt_dlp
# import whisper
# from googleapiclient.discovery import build

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator

# You may still need these for DAG configuration
# from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'youtube_processing',
    default_args=default_args,
    description='Process YouTube videos',
    schedule_interval=timedelta(days=1),
)

def download_audio(**kwargs):
    video_id = kwargs['dag_run'].conf['video_id']
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'outtmpl': f'/tmp/{video_id}.%(ext)s'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
    
    # Upload to Minio
    minio_client = Minio("localhost:9000", access_key="WBWGBLoRn6gcylvk39bW", secret_key="nmVkJX34b5YJNglM114k0iuiL21fYvEPYVt9FSfR", secure=False)
    minio_client.fput_object("social-data", f"{video_id}.m4a", f"/tmp/{video_id}.m4a")
    
    return f"{video_id}.m4a"

def transcribe_audio(**kwargs):
    ti = kwargs['ti']
    audio_file = ti.xcom_pull(task_ids='download_audio')
    video_id = kwargs['dag_run'].conf['video_id']
    
    # Download from Minio
    minio_client = Minio("localhost:9000", access_key="WBWGBLoRn6gcylvk39bW", secret_key="nmVkJX34b5YJNglM114k0iuiL21fYvEPYVt9FSfR", secure=False)
    minio_client.fget_object("social-data", audio_file, f"/tmp/{audio_file}")
    
    model = whisper.load_model("base")
    result = model.transcribe(f"/tmp/{audio_file}")
    
    # Store in PostgreSQL
    conn = psycopg2.connect("dbname=social-data user=syran password=sk8erb01 host=localhost")
    cur = conn.cursor()
    cur.execute("INSERT INTO transcriptions (video_id, audio_file_name, transcription) VALUES (%s, %s, %s)",
                (video_id, audio_file, result['text']))
    conn.commit()
    cur.close()
    conn.close()

def fetch_comments(**kwargs):
    video_id = kwargs['dag_run'].conf['video_id']
    youtube = build('youtube', 'v3', developerKey='AIzaSyDlokwxbeONWQloqemW2GqILztqBtZBmBs')
    
    comments = []
    results = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText"
    ).execute()
    
    while results:
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'video_id': video_id,
                'comment_id': item['id'],
                'author': comment['authorDisplayName'],
                'text': comment['textDisplay'],
                'published_at': comment['publishedAt']
            })
        
        if 'nextPageToken' in results:
            results = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                pageToken=results['nextPageToken']
            ).execute()
        else:
            break
    
    # Store in PostgreSQL
    conn = psycopg2.connectconnect("dbname=social-data user=syran password=sk8erb01 host=localhost")
    cur = conn.cursor()
    for comment in comments:
        cur.execute("""
            INSERT INTO comments (video_id, comment_id, author, text, published_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (comment['video_id'], comment['comment_id'], comment['author'], comment['text'], comment['published_at']))
    conn.commit()
    cur.close()
    conn.close()

t1 = PythonVirtualenvOperator(
    task_id='download_audio',
    python_callable=download_audio,
    requirements=[
        'minio',
        'yt-dlp'
    ],
    system_site_packages=False,
    provide_context=True,
    dag=dag,
)

t2 = PythonVirtualenvOperator(
    task_id='transcribe_audio',
    python_callable=transcribe_audio,
    requirements=[
        'minio',
        'openai-whisper',
        'psycopg2-binary'
    ],
    system_site_packages=False,
    provide_context=True,
    dag=dag,
)

t3 = PythonVirtualenvOperator(
    task_id='fetch_comments',
    python_callable=fetch_comments,
    requirements=[
        'google-api-python-client',
        'psycopg2-binary'
    ],
    system_site_packages=False,
    provide_context=True,
    dag=dag,
)

t1 >> [t2, t3]