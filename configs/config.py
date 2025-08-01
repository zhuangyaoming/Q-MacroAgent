import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
print("API_URL:", os.getenv("DEEPSEEK_API_URL"))