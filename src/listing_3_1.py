from dotenv import load_dotenv
import os
import openai

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


client = openai.OpenAI()
models = client.models.list()

for model in models.data:
    print(model)