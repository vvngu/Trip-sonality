import json
from backend.agents.critic_agent import critic_agent
from pathlib import Path
import asyncio

async def test_critic_agent():
    
    # Example input
    user_query = """[
  {
    "day": "Day 1",
    "activities": [
      {
        "time": "10:00 AM (2h)",
        "poi": {
          "name": "Ghibli Museum",
          "address": "1 Chome-1-83 Shimorenjaku, Mitaka, Tokyo 181-0013, Japan",
          "lat": 35.696238,
          "lng": 139.5704317,
          "rating": 4.5,
          "price_level": null,
          "types": ["tourist_attraction", "museum", "point_of_interest", "establishment"],
          "place_id": "ChIJLYwD5TTuGGARBZKEP5BV4U0",
          "source": "web",
          "score": 95
        }
      },
      {
        "time": "2:00 PM (2h)",
        "poi": {
          "name": "National Film Archive of Japan",
          "address": "3 Chome-7-6 Kyobashi, Chuo City, Tokyo 104-0031, Japan",
          "lat": 35.6755095,
          "lng": 139.7706169,
          "rating": 4.2,
          "price_level": null,
          "types": ["museum", "movie_theater", "tourist_attraction", "point_of_interest", "establishment"],
          "place_id": "ChIJDTEgTOKLGGARRjeD6dnAoVY",
          "source": "api",
          "score": 84
        }
      },
      {
        "time": "5:00 PM (1.5h)",
        "poi": {
          "name": "Donguri Republic (Ghibli Store) DiverCity Tokyo Plaza",
          "address": "Japan, 〒135-0064 Tokyo, Koto City, Aomi, 1 Chome−1−10 ダイバーシティ東京プラザ 5F",
          "lat": 35.6248877,
          "lng": 139.7759954,
          "rating": 4.6,
          "price_level": null,
          "types": ["point_of_interest", "store", "establishment"],
          "place_id": "ChIJb8zxaVOJGGARTUht7fHfkpY",
          "source": "api",
          "score": 91
        }
      }
    ]
  },
  {
    "day": "Day 2",
    "activities": [
      {
        "time": "10:00 AM (2.5h)",
        "poi": {
          "name": "Warner Bros. Studio Tour Tokyo - The Making of Harry Potter",
          "address": "1 Chome-1-7 Kasugacho, Nerima City, Tokyo 179-0074, Japan",
          "lat": 35.745183,
          "lng": 139.6460909,
          "rating": 4.7,
          "price_level": null,
          "types": ["amusement_park", "tourist_attraction", "point_of_interest", "establishment"],
          "place_id": "ChIJZzjXkvLtGGARm2YFfi26zoU",
          "source": "api",
          "score": 97
        }
      },
      {
        "time": "2:00 PM (1.5h)",
        "poi": {
          "name": "Harry Potter Stairs & Time Turner",
          "address": "Japan, 〒107-0052 Tokyo, Minato City, Akasaka, 5 Chome−4−5 赤坂駅",
          "lat": 35.6726774,
          "lng": 139.735835,
          "rating": 4.5,
          "price_level": null,
          "types": ["tourist_attraction", "point_of_interest", "establishment"],
          "place_id": "ChIJhyc0046LGGARTtseD5A7W_M",
          "source": "api",
          "score": 88
        }
      },
      {
        "time": "4:00 PM (1.5h)",
        "poi": {
          "name": "Starbucks Reserve Roastery Tokyo",
          "address": "2 Chome-19-23 Aobadai, Meguro City, Tokyo 153-0042, Japan",
          "lat": 35.6492642,
          "lng": 139.6925907,
          "rating": 4.5,
          "price_level": 2,
          "types": ["cafe", "food", "store", "bar", "point_of_interest", "establishment"],
          "place_id": "ChIJq_fYt4iLGGARrOojmQ4IMyE",
          "source": "api",
          "score": 85
        }
      }
    ]
  },
  {
    "day": "Day 3",
    "activities": [
      {
        "time": "11:00 AM (1.5h)",
        "poi": {
          "name": "Film Coffee&Things",
          "address": "1 Chome-32-21 Sangenjaya, Setagaya City, Tokyo 154-0024, Japan",
          "lat": 35.6416409,
          "lng": 139.6705987,
          "rating": 4.4,
          "price_level": null,
          "types": ["cafe", "bakery", "food", "store", "point_of_interest", "establishment"],
          "place_id": "ChIJ0wM8bN71GGAR0AbK68qU_lc",
          "source": "api",
          "score": 82
        }
      },
      {
        "time": "2:00 PM (2h)",
        "poi": {
          "name": "Godzilla Head",
          "address": "1 Chome-19 Kabukicho, Shinjuku City, Tokyo 160-0021, Japan",
          "lat": 35.6950521,
          "lng": 139.7019117,
          "rating": 4.4,
          "price_level": null,
          "types": ["tourist_attraction", "point_of_interest", "establishment"],
          "place_id": "ChIJzRzI3HSNGGARRwZW6AtJfi0",
          "source": "api",
          "score": 80
        }
      },
      {
        "time": "5:00 PM (2h)",
        "poi": {
          "name": "TOHO Cinemas Shinjuku",
          "address": "Japan, 〒160-0021 Tokyo, Shinjuku City, Kabukicho, 1 Chome−19−1 Shinjuku Toho Building, ３階",
          "lat": 35.6951484,
          "lng": 139.7019653,
          "rating": 4.1,
          "price_level": null,
          "types": ["movie_theater", "shopping_mall", "cafe", "meal_takeaway", "restaurant", "food", "point_of_interest", "store", "establishment"],
          "place_id": "ChIJ__JMK9iMGGAR6P_7QHoOGE4",
          "source": "api",
          "score": 78
        }
      }
    ]
  }
]"""

    task = {
    "itinerary": user_query,
    "mbti": "INFP",
    "days": 3,
    "budget": 200,
    "location": "Tokyo"
    }
    result = await critic_agent.run(task=f"""{task}

Please score candidate activity POIs and plan the itinerary based on the criteria described in your system instructions.
""")

    print(result.messages[-1].content)

if __name__ == "__main__":
    asyncio.run(test_critic_agent())

