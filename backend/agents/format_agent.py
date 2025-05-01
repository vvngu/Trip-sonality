from autogen_agentchat.agents import AssistantAgent
# from backend.config import client
# from backend.utils import load_prompt
from config import client
from utils import load_prompt

format_agent = AssistantAgent(
    name="format_agent",
    model_client=client,
    description="Format final output into `locations` and `itinerary`.",
    system_message=load_prompt("format_agent"),
)
