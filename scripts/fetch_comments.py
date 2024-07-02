from googleapiclient.discovery import build
import psycopg2
from datetime import datetime

# Initialize API key and video ID
API_KEY = 'AIzaSyDlokwxbeONWQloqemW2GqILztqBtZBmBs'

# Build the YouTube client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Establish a connection to the database
conn = psycopg2.connect(
    database="social-data", 
    user='syran', 
    password='sk8erb01', 
    host='192.168.8.116')
cur = conn.cursor()

# Fetch topLevel comments only
def get_video_comment_data(service, **kwargs):
    comment_data = []  # List to hold tuples for batch insert
    
    results = service.commentThreads().list(**kwargs).execute()
    
    while results:
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            videoId = item['snippet']['topLevelComment']['snippet']['videoId']
            publishedAt = item['snippet']['topLevelComment']['snippet']['publishedAt']
            authorDisplayName = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comment_data.append((videoId, authorDisplayName, comment, publishedAt))

        # Check if there are more pages
        if 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = service.commentThreads().list(**kwargs).execute()
        else:
            break

    return comment_data

if __name__ == '__main__':


    VIDEO_ID = 'uvsNJ9k9zdc'
    video_comments = get_video_comment_data(youtube, part='snippet', videoId=VIDEO_ID, textFormat='plainText')
    if video_comments:
        sql = '''INSERT INTO youtube_comments(video_id, author, text, published_at) VALUES (%s, %s, %s, %s)'''
        cur.executemany(sql, [(comment[0], comment[1], comment[2], datetime.strptime(comment[3], '%Y-%m-%dT%H:%M:%SZ')) for comment in video_comments])
        conn.commit()

    cur.close()
    conn.close()

    # fin
    print("inserted ", len(video_comments), " comments")
