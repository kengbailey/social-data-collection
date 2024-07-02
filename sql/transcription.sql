
drop table if exists audio_transcriptions ;
--
CREATE TABLE audio_transcriptions (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(255),
    audio_id INT,
    transcription TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

