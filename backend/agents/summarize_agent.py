from autogen_agentchat.agents import AssistantAgent
from utils import load_prompt
from config import client

summarize_agent = AssistantAgent(
    "summarize_agent",
    model_client=client,
    description="This agent analyzes raw user input and produces a structured JSON...",
    system_message=load_prompt("summarize_agent")
)
