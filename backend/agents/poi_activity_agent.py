from autogen_agentchat.agents import AssistantAgent
# from backend.tools.poi_activity_tool import gather_activity_pois
# from backend.config import client
# from backend.utils import load_prompt
from tools.poi_activity_tool import gather_activity_pois
from config import client
from utils import load_prompt

poi_activity_agent = AssistantAgent(
    name="poi_activity_agent",
    model_client=client,
    description="Searches and scores movie-themed activity POIs based on user profile and web content.",
    tools=[gather_activity_pois],
    system_message=load_prompt("poi_activity_agent"),
)
