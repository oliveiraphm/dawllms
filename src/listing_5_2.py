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

def get_structure(data_path):

    with sqlite3.connect(data_path) as connection:
        cursor = connection.cursor()
        cursor.execute("select sql from sqlite_master where type = 'table';")
        table_rows = cursor.fetchall()
        table_ddls = [r[0] for r in table_rows]
        return '\n'.join(table_ddls)
    
def create_prompt(description, question):
    
    parts = []
    parts += ['Database:']
    parts += [description]
    parts += ['Translate this question into SQL query:']
    parts += [question]
    return '\n'.join(parts)

def call_llm(prompt):
    for nr_retries in range(1, 4):
        try:
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[ {'role':'user', 'content':prompt}
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
        user_input = input('Enter question:')
        if user_input == 'quit':
            break

        prompt = create_prompt(data_structure, user_input)
        answer = call_llm(prompt)
        query = re.findall('```sql(.*)```', answer, re.DOTALL)[0]
        print(f'SQL: {query}')

        try: 
            result = process_query(args.dbpath, query)
            print(f'Result: {result}')
        except:
            print('Error processing query! Try to reformulate.')