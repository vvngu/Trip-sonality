from autogen_agentchat.agents import AssistantAgent
from tools.poi_activity_tool import gather_activity_pois
from config import client
from utils import load_prompt

poi_activity_agent = AssistantAgent(
    name="poi_activity_agent",
    model_client=client,
    description="Searches and scores activity POIs matching user's theme and preferences based on web content",
    tools=[gather_activity_pois],
    system_message=load_prompt("poi_activity_agent"),
)
