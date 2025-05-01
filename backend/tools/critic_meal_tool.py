import httpx
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_NEARBY_ENDPOINT = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

async def search_nearby_restaurants(
    lat: float,
    lng: float,
    cuisine_keywords: Optional[List[str]] = None,
    radius: int = 1000,
    min_rating: float = 4.0,
    max_results: int = 5
) -> List[dict]:
    """
    Search nearby restaurants around (lat, lng), optionally filtered by cuisine keywords.
    """
    all_results = []
    seen = set()

    # Default to "restaurant" if no keyword provided
    keywords = cuisine_keywords if cuisine_keywords else [""]
    
    for keyword in keywords:
        params = {
            "key": GOOGLE_PLACES_API_KEY,
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "restaurant",
            "keyword": keyword
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(PLACES_NEARBY_ENDPOINT, params=params)
                response.raise_for_status()
                data = response.json()
                candidates = data.get("results", [])
                
                for r in candidates:
                    rating = r.get("rating", 0)
                    place_id = r.get("place_id")
                    if (
                        place_id not in seen and
                        rating is not None and rating >= min_rating
                    ):
                        seen.add(place_id)
                        all_results.append({
                            "name": r.get("name"),
                            "address": r.get("vicinity"),
                            "lat": r.get("geometry", {}).get("location", {}).get("lat"),
                            "lng": r.get("geometry", {}).get("location", {}).get("lng"),
                            "rating": rating,
                            "price_level": r.get("price_level"),
                            "types": r.get("types", []),
                            "place_id": place_id,
                            "source": "nearby_api",
                            "matched_keyword": keyword
                        })
                        if len(all_results) >= max_results:
                            break
        except Exception as e:
            print(f"Failed nearby search for keyword '{keyword}' near ({lat}, {lng}): {e}")
    
    return all_results
