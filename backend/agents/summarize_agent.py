#backend/agents/summarize_agent.py

from autogen_agentchat.agents import AssistantAgent
from backend.utils import load_prompt
from backend.config import client  # 提前统一管理 client 初始化

summarize_agent = AssistantAgent(
    "summarize_agent",
    model_client=client,
    description="This agent analyzes raw user input and produces a structured JSON...",
    system_message=load_prompt("summarize_agent")
)
