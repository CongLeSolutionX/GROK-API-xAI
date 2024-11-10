import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
# load_dotenv()
load_dotenv(dotenv_path='../.env') # since my .env file is up one directory level

# Confirm of accessing the environment variable
print(os.getenv('XAI_API_KEY'))


XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

completion = client.chat.completions.create(
    model="grok-beta",
    messages=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
)

print(completion.choices[0].message)