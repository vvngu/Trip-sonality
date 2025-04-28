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
        "Use Google Places Text Search API to search for points of interest or restaurants "
        "by theme and location, returning a simplified list"
    )

    async def run(self, theme: str, location: str, date: str) -> List[Dict]:
        """
        :param theme:    e.g. "Movie Food"
        :param location: e.g. "Los Angeles, CA"
        :param date:     e.g. "2025-05-01"
        :returns:        List of {"place","time","cost"}
        """
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"{theme} in {location}",
            "key": GOOGLE_PLACES_API_KEY,
            # Optional: radius, language, etc.
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        # Limit to the first 5 results for demonstration
        for item in data.get("results", [])[:5]:
            name = item.get("name")
            price_level = item.get("price_level", 1)
            # Estimate lunch time as 12:00
            event_time = f"{date} 12:00"
            # Initial cost estimate: price_level * 15 USD
            cost_estimate = price_level * 15
            results.append({
                "place": name,
                "time": event_time,
                "cost": f"${cost_estimate}"
            })
        return results

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
