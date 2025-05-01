import asyncio
from backend.agents.poi_activity_agent import poi_activity_agent
from datetime import date

async def test_poi_agent():
    task_input = {
        "location": "Tokyo",
        "mbti": "INFP",
        "theme": "Movie",
        "days": 4,
        "budget": 2000,
        "inclusion": ["Totoro", "quiet cafe"],
        "web_places": [
            "Ghibli Museum",
            "Hotel Gajoen",
            "Gonpachi Restaurant",
            "Womb Nightclub",
            "Setagaya Daita",
            "Kichijoji",
            "Donguri Republic"
        ],
        "start_date": str(date.today())
    }

    prompt = f"""You are given the following user preferences and trip configuration:
{task_input}

Please search, combine, deduplicate, and score candidate activity POIs based on the criteria described in your system instructions.
"""

    result = await poi_activity_agent.run(task=prompt)
    # print(result)
    print(result.messages[-1].content)

if __name__ == "__main__":
    asyncio.run(test_poi_agent())
