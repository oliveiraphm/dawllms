import argparse
import openai
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


client = openai.OpenAI()

def transcribe(audio_path):

    with open(audio_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            file = audio_file, model='whisper-1')
        return transcription.text

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('audiopath', type=str, help='Path to audio file')
    args = parser.parse_args()

    transcript = transcribe(args.audiopath)
    print(transcript)