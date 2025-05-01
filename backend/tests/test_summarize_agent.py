import asyncio
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from backend.agents.summarize_agent import summarize_agent

async def test_summarize():
    input_json = {
        "mbti": "INFP",
        "Budget": 3000,
        "Query": "I'd like a 5-day movie-themed trip to Tokyo. I love quiet cafes and Ghibli. Avoid nightlife.",
        "CurrentItinerary": None
    }

    prompt = f"用户请求 JSON 如下：\n{input_json}"
    print(summarize_agent._system_messages)
    

    result = await summarize_agent.run(task=prompt)
    print(result.messages[-1].content)

if __name__ == "__main__":
    asyncio.run(test_summarize())
