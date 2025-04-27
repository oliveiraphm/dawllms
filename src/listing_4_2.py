from dotenv import load_dotenv
import os
import openai
import argparse
import pandas as pd
import time
import re

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


client = openai.OpenAI()


def create_prompt(text, attributes):
    parts = []
    parts += ['Extract the following properties into a table:']
    parts += [','.join(attributes)]
    parts += [f'Text source: {text}']
    parts += [
        ('Mark the beginning of the table with <BeginTable> '
         'and the end with <EndTable>.'
         )
    ]
    parts += [
        ('Separate rows by newline symbols and separate '
         'field by pipe symbols (|).'
         )
    ]
    parts += [
        ('Omit the table header and insert values in '
         'the attribute order from above.'
         )
    ]
    parts += [
        ('Use the placeholder <NA> if the value '
         'for an attribute is not available.'
         )
    ]
    return '\n'.join(parts)

def call_llm(prompt):
    for nr_retries in range(1, 4):
        try:
            response = client.chat.completions.create(
                model = 'gpt-4o',
                messages=[{'role':'user', 'content':prompt}]
            )
            return response.choices[0].message.content
        except:
            time.sleep(nr_retries * 2)
    raise Exception('Cannot query OpenAI model!')

def post_process(raw_answer):
    table_text = re.findall(
        '<BeginTable>(.*)<EndTable>',
        raw_answer, re.DOTALL)[0]
    results = []
    for raw_row in table_text.split("\n"):
        if raw_row:
            row = raw_row.split("|")
            row = [field.strip() for field in row]
            row = [field for field in row if field]
            results.append(row)

    return results

def extract_rows(text, attributes):

    prompt = create_prompt(text, attributes)
    result_text = call_llm(prompt)
    result_rows = post_process(result_text)
    return result_rows

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str, help='Path to input file')
    parser.add_argument('attributes', type=str, help='Attribute list')
    args = parser.parse_args()

    input_df = pd.read_csv(args.file_path)
    attributes = args.attributes.split('|')
    extractions = []
    for text in input_df['text'].values:
        print(text)
        print(attributes)
        extractions += extract_rows(text, attributes)

    result_df = pd.DataFrame(extractions)
    result_df.columns = attributes
    result_df.to_csv('result.csv')