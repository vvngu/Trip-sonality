# backend/config.py
import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

# # Setup the client to use either Azure OpenAI or GitHub Models
# load_dotenv(override=True)
# API_HOST = os.getenv("API_HOST", "github")


# if API_HOST == "github":
#     client = OpenAIChatCompletionClient(model=os.getenv("GITHUB_MODEL", "gpt-4o"), api_key=os.environ["GITHUB_TOKEN"], base_url="https://models.inference.ai.azure.com")
# elif API_HOST == "azure":
#     token_provider = azure.identity.get_bearer_token_provider(azure.identity.DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
#     client = AzureOpenAIChatCompletionClient(
#         model=os.environ["AZURE_OPENAI_CHAT_MODEL"],
#         api_version=os.environ["AZURE_OPENAI_VERSION"],
#         azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
#         azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
#         azure_ad_token_provider=token_provider,
#     )

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("请在 .env 文件中设置 OPENAI_API_KEY")

client = OpenAIChatCompletionClient(
    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
    api_key=OPENAI_API_KEY,
    base_url="https://api.openai.com/v1"
)
