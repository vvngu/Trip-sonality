from autogen_agentchat.agents import AssistantAgent
from tools.poi_activity_tool import gather_activity_pois
from tools.critic_meal_tool import search_nearby_restaurants
from config import client
from utils import load_prompt
from typing import List, Dict, Any, Optional

poi_activity_agent = AssistantAgent(
    name="poi_activity_agent",
    model_client=client,
    description="Enhanced agent that finds activity POIs and restaurants with MBTI-based scoring",
    tools=[gather_activity_pois, search_nearby_restaurants],
    system_message=load_prompt("poi_activity_agent"),
)
