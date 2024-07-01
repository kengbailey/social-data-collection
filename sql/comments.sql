CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    comment_id VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    text TEXT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);