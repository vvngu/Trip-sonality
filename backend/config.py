# backend/config.py
import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("请在 .env 文件中设置 OPENAI_API_KEY")

client = OpenAIChatCompletionClient(
    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
    api_key=OPENAI_API_KEY,
    base_url="https://api.openai.com/v1"
)
