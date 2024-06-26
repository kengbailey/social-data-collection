import yt_dlp
import whisper
import duckdb
from datetime import datetime


class Utils:
    @staticmethod
    def youtube_to_m4a(url_list):
        """
        Downloads the audio from YouTube videos in the given URL list and saves them as M4A files.

        Args:
            url_list (list): A list of YouTube video URLs.

        Returns:
            None
        """
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': './data/'+'%(title)s.%(ext)s',
            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in url_list:
                error_code = ydl.download([url])

    @staticmethod
    def create_db():
        """
        Function to create the database and the llm_analysis table.
        """
        conn = duckdb.connect('./data/database.db')
        c = conn.cursor()

        # create sequence
        c.execute('''CREATE SEQUENCE IF NOT EXISTS id_seq_analysis START 1''')
        c.execute('''CREATE SEQUENCE IF NOT EXISTS id_seq_transcription START 1''')

        # Create ll_analysis table
        c.execute('''CREATE TABLE IF NOT EXISTS llm_analysis (
                    id INTEGER DEFAULT nextval('id_seq_analysis') primary key,
                    prompt_text TEXT NOT NULL,
                    llm_params TEXT NOT NULL,
                    output_text TEXT NOT NULL,
                    output_stats TEXT,
                    context TEXT,
                    date_created DATETIME DEFAULT CURRENT_TIMESTAMP)''')

        # Create episode transcripts table
        c.execute('''CREATE TABLE IF NOT EXISTS video_transcription (
                    id INTEGER default nextval('id_seq_transcription') primary key,
                    filename TEXT NOT NULL,
                    transcription TEXT NOT NULL,
                    url TEXT NOT NULL,
                    context TEXT,
                    date_created DATETIME DEFAULT CURRENT_TIMESTAMP
                    );''')

        conn.commit()
        conn.close()

    @staticmethod
    def m4a_to_text(m4a_file):
        """
        Transcribes the audio from an M4A file to text.

        Args:
            m4a_file (str): The path to the M4A file.

        Returns:
            str: The text transcription of the M4A file.
        """
        model = whisper.load_model("base.en")
        result = model.transcribe(m4a_file)
        return result["text"]

    @staticmethod
    def insert_video_transcription(filename, transcription, context):
        """
        Inserts a video transcription into the database.

        Args:
            filename (str): The name of the video file.
            transcription (str): The transcription of the video.
            url (str): The youtube url of the video.

        Returns:
            None
        """
        conn = duckdb.connect('./data/database.db')
        c = conn.cursor()
        sql = """INSERT INTO video_transcription (filename, transcription, url)
        VALUES (?, ?, ?)"""
        c.execute(sql, (filename, transcription, context))
        conn.commit()
        conn.close()

    @staticmethod
    def insert_llm_analysis(prompt_text, llm_params, output_text, output_stats=None, context=None):
        conn = None

        try:
            # Connect to the database and create a cursor object
            conn = duckdb.connect('data/database.db')
            c = conn.cursor()

            # Prepare and execute the SQL command
            c.execute("INSERT INTO llm_analysis (prompt_text, llm_params, output_text, output_stats, context) VALUES (?, ?, ?, ?, ?)",
                        (prompt_text, llm_params, output_text, output_stats, context))

            # Commit changes to the database
            conn.commit()

        except duckdb.Error as e:
            print(f"An error occurred: {e}")

        finally:
            if conn:
                # Close the connection
                conn.close()


if __name__ == "__main__":

    
    
    Utils.m4a_to_text