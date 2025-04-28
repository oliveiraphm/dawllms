
import argparse
import cv2
import base64
import openai
import time
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


client = openai.OpenAI()


def extract_frames(video_path):

    video = cv2.VideoCapture(video_path)
    frames = []
    while video.isOpened() and len(frames) <= 10:
        success, frame = video.read()
        if not success:
            break
        
        _, buffer = cv2.imencode('.jpg', frame)
        encoded = base64.b64encode(buffer)
        frame = encoded.decode('utf-8')
        frames += [frame]
    
    video.release()
    return frames


def create_prompt(frames):

    prompt = ['Generate a concise title for the video.']
    for frame in frames[:10]:
        element = {'image':frame, 'resize':768}
        prompt += [element]
    return prompt


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


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('videopath', type=str, help='Path of video file')
    args = parser.parse_args()
    
    frames = extract_frames(args.videopath)
    prompt = create_prompt(frames)
    title = call_llm(prompt)
    print(title)