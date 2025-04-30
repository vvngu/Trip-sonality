from autogen_agentchat.agents import AssistantAgent
from config import client

format_agent = AssistantAgent(
    name="format_agent",
    model_client=client,
    description="Format final output into `locations` and `itinerary`.",
    system_message="你是最终格式化代理...\n"
)
