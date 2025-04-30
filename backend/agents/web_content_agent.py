from autogen_agentchat.agents import AssistantAgent
from config import client

web_content_agent = AssistantAgent(
    name="web_content_agent",
    model_client=client,
    description="Analyze search result snippets and extract potential POIs.",
    system_message="你是网页内容分析代理...\n"
)
