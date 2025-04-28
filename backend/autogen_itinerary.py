# backend/autogen_itinerary.py
"""
Multi-agent itinerary generation using GitHub Models or Azure OpenAI via the Autogen AgentChat framework.

Requires in .env:
  - API_HOST: 'github' or 'azure' (default 'github')
  - GITHUB_TOKEN: GitHub PAT with models:read (for GitHub Models)
  - GITHUB_MODEL: GitHub model name (e.g. 'gpt-4o')
  - AZURE_OPENAI_CHAT_MODEL, AZURE_OPENAI_CHAT_DEPLOYMENT, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_VERSION, AZURE_OPENAI_KEY (for Azure OpenAI)
  - GOOGLE_PLACES_API_KEY: Google Places API key

Usage:
  python autogen_itinerary.py '<json-string>'
"""
import asyncio
import os

import azure.identity
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient
from dotenv import load_dotenv
from my_tools.poi_and_cost import POISearchTool, CostEstimatorTool

# Setup the client to use either Azure OpenAI or GitHub Models
load_dotenv(override=True)
API_HOST = os.getenv("API_HOST", "github")


if API_HOST == "github":
    client = OpenAIChatCompletionClient(model=os.getenv("GITHUB_MODEL", "gpt-4o"), api_key=os.environ["GITHUB_TOKEN"], base_url="https://models.inference.ai.azure.com")
elif API_HOST == "azure":
    token_provider = azure.identity.get_bearer_token_provider(azure.identity.DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
    client = AzureOpenAIChatCompletionClient(
        model=os.environ["AZURE_OPENAI_CHAT_MODEL"],
        api_version=os.environ["AZURE_OPENAI_VERSION"],
        azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_ad_token_provider=token_provider,
    )

planner_agent = AssistantAgent(
    "planner_agent",
    model_client=client,
    description="A planner agent that use his/her knowledge to generate or revise a day-by-day itinerary outline.",
    system_message="You are a trip planning assistant. You will receive JSON input containing keys: budget, dates, location, mbti, theme, field, optionally _previous_itinerary. Your task is to generate a JSON array of objects [{day, food, activities, summary}], your final response must be NEXT.",
)

detail_agent = AssistantAgent(
    "detail_agent",
    model_client=client,
    description="A helpful assistant that can provide detailed information and cost for visiting about the destination.",
    system_message="You will receive an itinerary outline and user input. Your primary function is to enrich this outline by getting more detailed information for places suggested and estimate the cost of visiting for time, place, and cost for each day, ensure the original JSON structure is preserved, your final response must be NEXT.",
)

format_agent = AssistantAgent(
    "format_agent",
    model_client=client,
    description="A helpful assistant that can format the travel plan.",
    system_message="""You are a helpful assistant that format the detailed itinerary. You will receive a detailed itinerary and you will format it into:[

  {

    "day": "day info",

    "food": [

      { "time": "time", "place": "place info", "cost": "$price" },

      {}

      // ... more food entries for the day

    ],

    "activities": [

      // ... activity objects as before

    ],

    "summary": "summary info"

  },

]You must ensure that the final plan is integrated and complete. YOUR FINAL RESPONSE MUST BE THE COMPLETE PLAN. When the plan is complete and all perspectives are integrated, you can respond with TERMINATE.""",
)


async def run_agents():
    termination = TextMentionTermination("TERMINATE")
    group_chat = MagenticOneGroupChat(
        [planner_agent, detail_agent, format_agent],
        termination_condition=termination,
        model_client=client,
    )
    await Console(group_chat.run_stream(task="""User request:{
        "budget": "2500+ USD",
        "dates": "6 days",
        "field": "Food",
        "location": "Los Angeles, CA",
        "mbti": "ISTJ",
        "theme": "Movie"
    }"""))


if __name__ == "__main__":
    asyncio.run(run_agents())





# # Initialize tools
# poi_tool = POISearchTool()
# cost_tool = CostEstimatorTool()

# # Wrap tool methods into uniquely named callables for the agent
# async def poi_search(theme: str, location: str, date: str):
#     """Function wrapper for POI search tool"""
#     return await poi_tool.run(theme, location, date)

# def cost_estimate(items: list):
#     """Function wrapper for cost estimator tool"""
#     return cost_tool.run(items)


# detail_agent = AssistantAgent(
#     name="detail_agent",
#     model_client=client,
#     tools=[poi_search, cost_estimate],  # use uniquely named wrappers
#     description="Fill in itinerary details using POI and cost estimation tools",
#     system_message="""
# You receive the outline and user input. Use the poi_search tool to fetch places 
# and cost_estimate to assign time, place, and cost for each day.
# Maintain the JSON structure and reply with "NEXT".
# """.strip()
# )


# Run the multi-agent pipeline
# async def run_agents(request_json: str) -> None:
#     termination = TextMentionTermination("TERMINATE")
#     group = MagenticOneGroupChat(
#         [planner_agent, detail_agent, format_agent],
#         termination_condition=termination,
#         model_client=client
#     )
#     await Console(group.run_stream(task=f"User request: {request_json}"))

# # CLI entrypoint
# if __name__ == "__main__":
#     import sys
#     payload = sys.argv[1] if len(sys.argv) > 1 else json.dumps({
#         "budget": "2500+ USD",
#         "dates": "6 days",
#         "field": "Food",
#         "location": "Los Angeles, CA",
#         "mbti": "ISTJ",
#         "theme": "Movie"
#     })
#     asyncio.run(run_agents(payload))
