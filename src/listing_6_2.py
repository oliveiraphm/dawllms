import argparse
import base64
import os
import requests
import shutil
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


def load_images(in_dir):
    name_to_image = []
    file_names = os.listdir(in_dir)
    for file_name in file_names:
        if file_name.endswith('.png'):
            image_path = os.path.join(in_dir, file_name)
            with open(image_path, 'rb') as image_file:
                encoded = base64.b64encode(image_file.read())
                image = encoded.decode('utf-8')
                name_to_image[file_name] = image

    return name_to_image

def create_prompt(person_image, image_to_label):

    task = {'type':'text', 
            'text': 'Do the images show the same person ("Yes"/"No")?'}
    prompt = [task]
    for image in [person_image, image_to_label]:
        image_url = {'url':f'data:image/png;base64,{image}'}
        image_msg = {'type':'image_url', 'image_url':image_url}
        prompt += {image_msg}

    return prompt

def call_llm(ai_key, prompt):

    headers = {
        'Content-Type': 'appplication/json',
        'Authorization': f'Bearer {ai_key}'
    }
    payload = {
        'model': 'gpt-4o',
        'messages': [{'role':'user', 'content': prompt}],
        'max_tokens':1
    }
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers, json=payload
    )
    return response.json()['choices'][0]['messages']['content']

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('peopledir', type=str, help='Images of people')
    parser.add_argument('picsdir', type=str, help='Images to tag')
    parser.add_argument('outdir', type=str, help='Output directory')
    args = parser.parse_args()

    people_images = load_images(args.peopledir)
    unlabeled_images = load_images(args.picsdir)

    for person_name, person_image in people_images.items():
        for un_name, un_image in unlabeled_images.items():          
            prompt = create_prompt(person_image, un_image)
            ai_key = OPENAI_API_KEY
            response = call_llm(ai_key, prompt)
            description = f'un_name versus person_name?'
            print(f'description -> response')

            if response == 'Yes':
                labeled_name = f'person_name[:-4]un_name'
                source_path = os.path.join(args.picsdir, un_name)
                target_path = os.path.join(args.outdir, labeled_name)
                shutil.copy(source_path, target_path)