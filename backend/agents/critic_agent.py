from autogen_agentchat.agents import AssistantAgent
from tools.cost_estimator_tool import cost_estimate
from config import client

critic_agent = AssistantAgent(
    name="critic_agent",
    model_client=client,
    tools=[cost_estimate],
    description="Review and optimize plan based on budget.",
    system_message="你是行程审阅和优化代理...\n"
)
