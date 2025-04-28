# backend/my_tools/poi_and_cost.py
"""
Tools for searching points of interest (POI) and estimating costs.
"""
import os
from dotenv import load_dotenv
from typing import List, Dict
import httpx

# Load environment variables from .env
load_dotenv()

# Read Google Places API key from environment variables
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
if not GOOGLE_PLACES_API_KEY:
    raise RuntimeError("Please set the GOOGLE_PLACES_API_KEY environment variable in your .env file.")

class POISearchTool:
    name = "poi_search"
    description = (
        "Search for POIs by theme and location, generating at least 2*n_days meals and 2*n_days activities. "
        "Returns items tagged with day, estimated duration (time), and cost."
    )

    async def run(self, theme: str, location: str, n_days: int, mbti: str, field: str) -> List[Dict]:
        """
        :param theme: e.g. "Movie"
        :param location: e.g. "Los Angeles, CA"
        :param n_days: number of days for itinerary
        :param mbti: e.g. "ISTJ"
        :param field: ignored (meals and activities both generated)
        :returns: List of {
            "day", "name", "type", "address", "lat", "lng", "rating", 
            "price_level", "time", "cost", "place_id"
        }
        """
        base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        # Prepare queries for meals and activities
        meal_query = f"{theme} restaurant for {mbti} in {location}"
        activity_query = f"{theme} attraction for {mbti} in {location}"

        async with httpx.AsyncClient(timeout=10) as client:
            meal_resp = await client.get(base_url, params={"query": meal_query, "key": GOOGLE_PLACES_API_KEY})
            act_resp = await client.get(base_url, params={"query": activity_query, "key": GOOGLE_PLACES_API_KEY})
            meal_resp.raise_for_status()
            act_resp.raise_for_status()
            meal_data = meal_resp.json()
            act_data = act_resp.json()

        # Extract results
        raw_meals = meal_data.get("results", [])[:2 * n_days]
        raw_acts = act_data.get("results", [])[:2 * n_days]

        items: List[Dict] = []
        # Process meals
        for idx, res in enumerate(raw_meals):
            day = (idx // 2) + 1
            name = res.get("name")
            address = res.get("formatted_address") or res.get("vicinity")
            loc = res.get("geometry", {}).get("location", {})
            lat = loc.get("lat")
            lng = loc.get("lng")
            rating = res.get("rating")
            price_level = res.get("price_level", 1)
            place_id = res.get("place_id")
            duration = "1h"  # estimated duration for a meal
            base_cost = price_level * 15
            items.append({
                "day": day,
                "name": name,
                "type": "Meal",
                "address": address,
                "lat": lat,
                "lng": lng,
                "rating": rating,
                "price_level": price_level,
                "time": duration,
                "cost": f"${base_cost}",
                "place_id": place_id,
            })
        # Process activities
        for idx, res in enumerate(raw_acts):
            day = (idx // 2) + 1
            name = res.get("name")
            address = res.get("formatted_address") or res.get("vicinity")
            loc = res.get("geometry", {}).get("location", {})
            lat = loc.get("lat")
            lng = loc.get("lng")
            rating = res.get("rating")
            price_level = res.get("price_level", 1)
            place_id = res.get("place_id")
            duration = "2h"  # estimated duration for an activity
            base_cost = price_level * 15
            items.append({
                "day": day,
                "name": name,
                "type": "Activity",
                "address": address,
                "lat": lat,
                "lng": lng,
                "rating": rating,
                "price_level": price_level,
                "time": duration,
                "cost": f"${base_cost}",
                "place_id": place_id,
            })
        return items

class CostEstimatorTool:
    name = "cost_estimator"
    description = (
        "Estimate and refine the cost field for a list of activities/restaurants, "
        "taking into account ratings and price levels"
    )

    def run(self, items: List[Dict]) -> List[Dict]:
        """
        :param items: List of {"place","time","cost"} with initial cost estimates
        :returns:      Updated list with final cost estimates
        """
        # Sample strategy: increase cost by 10% for high-rated items, apply 10% discount for low-rated items
        for entry in items:
            base_cost = float(entry["cost"].strip("$"))
            rating = entry.get("rating")
            if rating is not None:
                if rating >= 4.5:
                    final_cost = round(base_cost * 1.1)
                elif rating < 3.0:
                    final_cost = round(base_cost * 0.9)
                else:
                    final_cost = base_cost
            else:
                final_cost = base_cost
            entry["cost"] = f"${final_cost}"
        return items
