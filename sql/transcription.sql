CREATE TABLE transcriptions (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    audio_file_name VARCHAR(255) NOT NULL,
    transcription TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

