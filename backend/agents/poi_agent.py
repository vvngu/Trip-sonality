from autogen_agentchat.agents import AssistantAgent
from tools.poi_search_tool import poi_search
from config import client

poi_agent = AssistantAgent(
    name="poi_agent",
    model_client=client,
    tools=[poi_search],
    description="Use Google Places API to convert POI names to structured info.",
    system_message="你是地点查找代理...\n"
)
