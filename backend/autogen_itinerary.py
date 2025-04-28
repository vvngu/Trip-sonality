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

# Initialize tools
poi_tool = POISearchTool()
cost_tool = CostEstimatorTool()

# Wrap tool methods into uniquely named callables for the agent
# async def poi_search(theme: str, location: str, dates: str, mbti: str, field: str):
#     """Function wrapper for POI search tool"""
#     return await poi_tool.run(theme, location, dates, mbti, field)
async def poi_search(theme: str, location: str, n_days: int, mbti: str, field: str):
    """Function wrapper for POI search tool"""
    # Convert n_days if passed as string like '6 days'
    try:
        days = int(n_days)
    except (ValueError, TypeError):
        days = int(n_days.split()[0]) if isinstance(n_days, str) else 1
    return await poi_tool.run(theme, location, days, mbti, field)

def cost_estimate(items: list):
    """Function wrapper for cost estimator tool"""
    return cost_tool.run(items)

# Agent 1: Search for POIs with durations and base cost
search_agent = AssistantAgent(
    "search_agent",
    model_client=client,
    tools=[poi_search],
    description="Search agent that finds all relevant restaurants and attractions, retrieving name, type, location, time (duration), and base cost.",
    system_message="""
You are a POI search agent. You will receive JSON with keys: theme, location, dates (number of days), mbti, field.
Call poi_search once to get a list of items, each with fields: name, type (Meal/Activity), address, lat, lng, rating, price_level, time (duration), cost (base), place_id, and day number.
Output a JSON object: { "items": [ { ... } ] } preserving these fields.
"""
)
# Agent 2: Refine cost estimates
detail_agent = AssistantAgent(
    "detail_agent",
    model_client=client,
    tools=[cost_estimate],
    description="Detail agent that refines base cost while preserving durations.",
    system_message="""
You are a detail agent. You will receive JSON: { "items": [ { name, type, address, lat, lng, rating, price_level, time (duration), cost (base), place_id, day }, ... ] }.
Call cost_estimate once with the full items list to update each entry's cost based on rating and price_level.
Output a JSON object: { "items": [ { same fields including updated cost }, ... ] }.
"""
)
# Agent 3: Schedule times into actual ranges and assemble plan
plan_agent = AssistantAgent(
    "plan_agent",
    model_client=client,
    description="Planning agent that assembles a day-by-day itinerary with scheduled times and ensures budget.",
    system_message="""
You are a planning agent. You will receive JSON with keys: budget, dates (number of days), and detailed "items" list (with name, type, time (duration), cost, and day number).
Convert each item's duration (e.g., "2h") into a realistic time slot for that day (e.g., "1:00 PM - 3:00 PM").
Generate a JSON array "itinerary" with objects:
[
  {
    "day": <number>,
    "food": [
      { "name": <name>, "time": <start-end>, "cost": <cost> },
      { "name": <name>, "time": <start-end>, "cost": <cost> }
    ],
    "activities": [
      { "name": <name>, "time": <start-end>, "cost": <cost> },
      ...
    ],
    "summary": <text>
  },
  ...
]
Ensure each day includes exactly two meals and at least one activity. The total cost across all days must not exceed the budget.
"""
)
# Agent 4: Format the finalized plan
format_agent = AssistantAgent(
    "format_agent",
    model_client=client,
    description="Formatting agent that outputs the plan in polished JSON.",
    system_message="""
You are a formatting agent. You will receive the complete plan as JSON.
Format it cleanly as final output and then respond with TERMINATE.
"""
)

# planner_agent = AssistantAgent(
#     "planner_agent",
#     model_client=client,
#     description="A planner agent that use his/her knowledge to generate or revise a day-by-day itinerary outline.",
#     system_message="You are a trip planning assistant. You will receive JSON input containing keys: budget, dates, location, mbti, theme, field, optionally _previous_itinerary. Your task is to generate a JSON array of objects [{day, food, activities, summary}].",
# )

# detail_agent = AssistantAgent(
#     "detail_agent",
#     model_client=client,
#     tools=[poi_search, cost_estimate], 
#     description="A helpful assistant that can provide detailed information and cost with tools poi_search and cost_estimate for visiting about the destination.",
#     system_message="You will receive an itinerary outline and user input. Your primary function is to enrich this outline by getting more detailed information for places suggested using poi_search tool and estimate the cost of visiting for place using cost_estimate tool, ensure the original JSON structure is preserved.",
# )

# format_agent = AssistantAgent(
#     "format_agent",
#     model_client=client,
#     description="A helpful assistant that can format the travel plan.",
#     system_message="""You are a helpful assistant that format the detailed itinerary. You will receive a detailed itinerary and you will format it into:[

#   {

#     "day": "day info",

#     "food": [

#       { "time": "time", "place": "place info", "cost": "$price" },

#       {}

#       // ... more food entries for the day

#     ],

#     "activities": [

#       // ... activity objects as before

#     ],

#     "summary": "summary info"

#   },

# ]You must ensure that the final plan is integrated and complete. YOUR FINAL RESPONSE MUST BE THE COMPLETE PLAN. When the plan is complete and all perspectives are integrated, you can respond with TERMINATE.""",
# )


async def run_agents():
    termination = TextMentionTermination("TERMINATE")
    group_chat = MagenticOneGroupChat(
        [search_agent, detail_agent, plan_agent, format_agent],
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
