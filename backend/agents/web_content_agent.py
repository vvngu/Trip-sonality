from autogen_agentchat.agents import AssistantAgent
from backend.config import client
from backend.utils import load_prompt

web_content_agent = AssistantAgent(
    name="web_content_agent",
    model_client=client,
    description="Analyze search result snippets and extract potential POIs.",
    system_message=load_prompt("web_content_agent")
)
