from autogen_agentchat.agents import AssistantAgent
from config import client

plan_agent = AssistantAgent(
    name="plan_agent",
    model_client=client,
    description="Arrange itinerary per day from POI list.",
    system_message="你是行程规划代理...\n"
)
