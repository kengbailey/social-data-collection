drop table if exists youtube_audio ;
--
CREATE TABLE youtube_audio (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    author_name VARCHAR(255),
    channel_id VARCHAR(255),
    channel_url VARCHAR(2048),
    upload_date DATE,
    s3_path VARCHAR(255),
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
