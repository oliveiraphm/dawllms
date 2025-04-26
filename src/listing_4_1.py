from dotenv import load_dotenv
import os
import openai
import argparse
import pandas as pd
import time

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


client = openai.OpenAI()

def create_prompt(text):

    task = 'Is the sentiment positive or negative?'
    answer_format = 'Answer ("Positive"/"Negative")'
    return f'{text}\n{task}\n{answer_format}:'

def call_llm(prompt):

    for nr_retries in range(1, 4):
        try:
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {'role':'user', 'content':'prompt'}
                ]
            )
            return response.choices[0].message.content
        
        except:
            time.sleep(nr_retries * 2)
        raise Exception('Cannot query OpenAI model!')
    
def classify(text):

    prompt = create_prompt(text)
    label = call_llm(prompt)
    return label

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str, help='Path to input file')
    args = parser.parse_args()

    df = pd.read_csv(args.file_path)
    df['class'] = df['text'].apply(classify)
    statistics = df['class'].value_counts()
    print(statistics)
    df.to_csv('result.csv')

    