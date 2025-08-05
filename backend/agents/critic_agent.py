from autogen_agentchat.agents import AssistantAgent
from tools.critic_meal_tool import search_nearby_restaurants
from config import client
from utils import load_prompt

critic_agent = AssistantAgent(
    name="critic_agent",
    model_client=client,
    tools=[search_nearby_restaurants],
    description="Review and optimize plan based on budget.",
    system_message=load_prompt("critic_agent")
)

