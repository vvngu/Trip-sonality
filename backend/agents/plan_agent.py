from autogen_agentchat.agents import AssistantAgent
from config import client
from utils import load_prompt

plan_agent = AssistantAgent(
    name="plan_agent",
    model_client=client,
    description="Arrange itinerary per day from POI list.",
    system_message=load_prompt("plan_agent")
)
