from googleapiclient.discovery import build
import json
import sqlite3
import pandas as pd
import psycopg2
from datetime import datetime

# Initialize API key and video ID
API_KEY = 'AIzaSyDlokwxbeONWQloqemW2GqILztqBtZBmBs'
VIDEO_ID = 'kjtbpWS-EjI'

# Build the YouTube client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Establish a connection to the database
conn = psycopg2.connect(database="social-data", user='syran', password='sk8erb01', host='192.168.8.116')
cur = conn.cursor()

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

# Get comments (you can adjust the parameters as needed)
video_comments = get_video_comment_data(youtube, part='snippet', videoId=VIDEO_ID, textFormat='plainText', maxResults=10)

# Assuming video_comments is a list of tuples in the format (video_id, author, text, published_at)
if video_comments:
    sql = '''INSERT INTO youtube_comments(video_id, author, text, published_at) VALUES (%s, %s, %s, %s)'''
    cur.executemany(sql, [(comment[0], comment[1], comment[2], datetime.strptime(comment[3], '%Y-%m-%dT%H:%M:%SZ')) for comment in video_comments])
    conn.commit()

# Close the cursor and connection to so the server can allocate bandwidth to other requests
cur.close()
conn.close()

# fin
print("inserted ", len(video_comments), " comments")




###
# todo
# 1. create table for youtube audios that link to files in s3 location - DONE
# 2. create table for comments on those videos ... ALTER existing table - DONE

