import argparse
import openai
import re
import scipy.io.wavfile
import sounddevice
import sqlite3
import time
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


client = openai.OpenAI()

def get_structure(data_path):
    with sqlite3.connect(data_path) as connection:
        cursor = connection.cursor()
        cursor.execute("select sql from sqlite_master where type='table';")
        table_rows = cursor.fetchall()
        table_ddls = [r[0] for r in table_rows]
        return '\n'.join(table_ddls)
    
def record(output_path):
    sample_rate = 44100
    nr_frames = 5 * sample_rate
    recording = sounddevice.rec(nr_frames, samplerate=sample_rate, channels=1)
    sounddevice.wait()
    scipy.io.wavfile.write(output_path, sample_rate, recording)

def transcribe(audio_path):

    with open(audio_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            file = audio_file, model='whisper-1')
        return transcription.text
    
def create_prompt(description, question):

    parts = []
    parts += ['Database:']
    parts += [description]
    parts += ['Translate this question into SQL query:']
    parts += [question]
    parts += ['SQL Query:']
    return '\n'.join(parts)


def call_llm(prompt):

    for nr_retries in range(1, 4):
        try:
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {'role':'user', 'content':prompt}
                    ]
                )
            return response.choices[0].message.content
        except:
            time.sleep(nr_retries * 2)
    raise Exception('Cannot query OpenAI model!')


def process_query(data_path, query):

    with sqlite3.connect(data_path) as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        table_rows = cursor.fetchall()
        table_strings = [str(r) for r in table_rows]
        return '\n'.join(table_strings)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('dbpath', type=str, help='Path to SQLite data')
    args = parser.parse_args()

    data_structure = get_structure(args.dbpath)
    
    while True:
        
        user_input = input('Press enter to record (type quit to quit).')
        if user_input == 'quit':
            break
        
        audio_path = 'question.wav'
        record(audio_path)
        question = transcribe(audio_path)
        print(f'Question: {question}')
        
        prompt = create_prompt(data_structure, question)
        answer = call_llm(prompt)
        query = re.findall('```sql(.*)```', answer, re.DOTALL)[0]
        print(f'SQL: {query}')

        try:    
            answer = process_query(args.dbpath, query)
            print(f'Answer: {answer}')
        except:
            print('Error processing query! Try to reformulate.')