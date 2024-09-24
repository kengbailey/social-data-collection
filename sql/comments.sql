drop table if exists youtube_comments;
-- 
CREATE TABLE youtube_comments (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    text TEXT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 

DROP TABLE IF EXISTS youtube_comment_sentiments;

CREATE TABLE youtube_comment_sentiments (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER NOT NULL,
    sentiment_score NUMERIC(3, 2),
    sentiment_detected VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES youtube_comments(id) ON DELETE CASCADE
);