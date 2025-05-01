import asyncio
from backend.agents.search_agent import search_agent

async def test_search():
    summary = {
        "theme": "Movie",
        "location": "Tokyo",
        "dates": 5,
        "start": "2024-05-01",
        "end": "2024-05-05",
        "mbti": "INFP",
        "inclusion": ["quiet cafes", "Studio Ghibli"],
        "exclusion": ["nightlife"]
    }

    query_input = f"Please search and extract movie-related locations based on the following:\n{summary}"

    result = await search_agent.run(task=query_input)

    print(result.messages[-1].content)

if __name__ == "__main__":
    asyncio.run(test_search())
