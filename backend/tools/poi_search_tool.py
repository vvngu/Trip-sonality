import os
import httpx
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

class POISearchTool:
    name = "poi_search"
    description = "使用 Google Places 搜索地点并返回餐馆/活动信息"

    async def run(self, theme: str, location: str, n_days: int, mbti: str, field: str = "both") -> List[Dict]:
        base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        meal_query = f"{theme} restaurant for {mbti} in {location}"
        act_query = f"{theme} attraction for {mbti} in {location}"

        async with httpx.AsyncClient(timeout=10) as client:
            meal_resp = await client.get(base_url, params={"query": meal_query, "key": GOOGLE_PLACES_API_KEY})
            act_resp = await client.get(base_url, params={"query": act_query, "key": GOOGLE_PLACES_API_KEY})
            meal_resp.raise_for_status()
            act_resp.raise_for_status()

            meal_data = meal_resp.json().get("results", [])[:2 * n_days]
            act_data = act_resp.json().get("results", [])[:2 * n_days]

        items = []
        for idx, res in enumerate(meal_data):
            items.append({
                "day": (idx // 2) + 1,
                "name": res.get("name"),
                "type": "Meal",
                "address": res.get("formatted_address") or res.get("vicinity"),
                "lat": res.get("geometry", {}).get("location", {}).get("lat"),
                "lng": res.get("geometry", {}).get("location", {}).get("lng"),
                "rating": res.get("rating"),
                "price_level": res.get("price_level", 1),
                "time": "1h",
                "cost": f"${res.get('price_level', 1) * 15}",
                "place_id": res.get("place_id"),
            })
        for idx, res in enumerate(act_data):
            items.append({
                "day": (idx // 2) + 1,
                "name": res.get("name"),
                "type": "Activity",
                "address": res.get("formatted_address") or res.get("vicinity"),
                "lat": res.get("geometry", {}).get("location", {}).get("lat"),
                "lng": res.get("geometry", {}).get("location", {}).get("lng"),
                "rating": res.get("rating"),
                "price_level": res.get("price_level", 2),
                "time": "2h",
                "cost": f"${res.get('price_level', 2) * 20}",
                "place_id": res.get("place_id"),
            })
        return items
