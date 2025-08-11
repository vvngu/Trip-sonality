import httpx
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_NEARBY_ENDPOINT = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

def get_cuisine_keywords(location: str) -> List[str]:
    """Get cuisine keywords based on location"""
    location_cuisine = {
        'tokyo': ['ramen', 'sushi', 'japanese'],
        'paris': ['bistro', 'cafe', 'french'], 
        'los angeles': ['mexican', 'fusion', 'californian'],
        'new york': ['pizza', 'deli', 'american'],
        'london': ['pub', 'british'],
        'rome': ['pasta', 'pizza', 'italian'],
    }
    return location_cuisine.get(location.lower(), ['local', 'traditional'])

def apply_restaurant_mbti_scoring(restaurants: List[dict], mbti: str) -> List[dict]:
    """Apply MBTI-based scoring to restaurants"""
    for restaurant in restaurants:
        base_score = (restaurant.get('rating', 4.0) - 1) * 20
        restaurant_types = [t.lower() for t in restaurant.get('types', [])]
        
        mbti_bonus = 0
        if mbti and len(mbti) >= 4:
            if 'E' in mbti:  # Extroverts prefer bustling restaurants
                if any(t in restaurant_types for t in ['bar', 'night_club']):
                    mbti_bonus += 5
            else:  # Introverts prefer quieter dining
                if any(t in restaurant_types for t in ['cafe', 'bakery']):
                    mbti_bonus += 5
            if 'S' in mbti:  # Sensors prefer traditional food
                mbti_bonus += 3
            
        restaurant['score'] = min(100, max(60, base_score + mbti_bonus + 10))
    return restaurants

async def search_nearby_restaurants(
    lat: float,
    lng: float,
    location: str = "",  #  location for cuisine keywords
    mbti: str = "", # MBTI for scoring
    cuisine_keywords: Optional[List[str]] = None,
    radius: int = 1000,
    min_rating: float = 4.0,
    max_results: int = 5
) -> List[dict]:
    print(f"🍽️ search_nearby_restaurants called with: lat={lat}, lng={lng}, location={location}")

    """
    Enhanced restaurant search with automatic cuisine keywords and MBTI scoring
    """
    all_results = []
    seen = set()
    #Use location based cuisine keywords if not provided
    if not cuisine_keywords and location:
        cuisine_keywords = get_cuisine_keywords(location)

    # Default to empty string if no keyword provided
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
                            "matched_keyword": keyword,
                            "category": "restaurant" # for consistent tagging
                        })
                        if len(all_results) >= max_results:
                            break
        except Exception as e:
            print(f"Failed nearby search for keyword '{keyword}' near ({lat}, {lng}): {e}")
    #Apply MBTI scoring to all restaurants    
    if mbti:
        all_results = apply_restaurant_mbti_scoring(all_results, mbti)
    print(f"✅ search_nearby_restaurants returning {len(all_results)} restaurants")
    return all_results
