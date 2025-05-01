from autogen_agentchat.agents import AssistantAgent
# from backend.tools.tavily_search_tool import web_search, clean_html_from_url
# from backend.config import client
# from backend.utils import load_prompt
from tools.tavily_search_tool import web_search, clean_html_from_url
from config import client
from utils import load_prompt

search_agent = AssistantAgent(
    name="search_agent",
    model_client=client,
    tools=[web_search, clean_html_from_url],
    description="Second step: performs Tavily search and extracts Ghibli-related travel locations",
    system_message=load_prompt("search_agent")
)
