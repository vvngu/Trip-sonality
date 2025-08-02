from autogen_agentchat.agents import AssistantAgent
from tools.tavily_search_tool import web_search, clean_html_from_url
from config import client
from utils import load_prompt

search_agent = AssistantAgent(
    name="search_agent",
    model_client=client,
    tools=[web_search, clean_html_from_url],
    description="Second step: Performs web search to find relevant travel locations based on user's theme and preferences",
    system_message=load_prompt("search_agent")
)
