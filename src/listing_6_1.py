from dotenv import load_dotenv
import openai
import os
import argparse
import time
import re
import sqlite3

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

client = openai.OpenAI()

def analyze_image(image_url, question):
    
    for nr_retries in range(1, 4):
        
        try:
            response = client.chat.completions.create(
                model = 'gpt-4o',
                messages = [
                    {'role':'user', 'content':[
                        {'type':'text', 'text':question},
                        {'type':'image_url', 'image_url':{'url':image_url}}
                    ]}
                ]
            )
            return response.choices[0].message.content
        except:
            time.sleep(nr_retries * 2)
    raise Exception('Cannot query OpenAI model!')

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('imageurl', type=str, help='URL to image')
    parser.add_argument('question', type=str, help='Question about image')
    args = parser.parse_args()

    answer = analyze_image(args.imageurl, args.question)
    print(answer)