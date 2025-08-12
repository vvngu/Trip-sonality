import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set OPENAI_API_KE in .env file")

client = OpenAIChatCompletionClient(
    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    api_key=OPENAI_API_KEY,
    base_url="https://api.openai.com/v1"
)
