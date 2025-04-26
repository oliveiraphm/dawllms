from dotenv import load_dotenv
import os
import openai

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


client = openai.OpenAI()
result = client.chat.completions.create(
    model='gpt-3.5-turbo-0125',
    messages=[ {
        'role':'user',
        'content':'Tell me a story!'
    }

    ],
    max_tokens=512,
    stop='happily ever after',
    temperature=1.5,
    presence_penalty=0.5,
    logit_bias={14844:-100}

)
print(result.choices[0].message.content)