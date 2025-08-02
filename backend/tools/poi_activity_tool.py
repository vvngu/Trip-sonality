import json
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv
from tools.critic_meal_tool import search_nearby_restaurants

load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_ENDPOINT = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# 构造活动相关的搜索 query（始终围绕电影主题）
def build_activity_queries(
    location: str,
    mbti: str,
    theme: str = "culture",
    inclusion: Optional[List[str]] = None,
) -> List[str]:
    queries = [
        f"{theme} attractions in {location} city",
        f"{theme} themed experiences in {location} city",
        f"{theme} locations in {location} city",
        f"{theme} experience for {mbti} in {location} city",
    ]

    if inclusion:
        for inc in inclusion:
            queries.append(f"{inc} in {location} related to {theme}")
    return queries

# 基础搜索调用 Google Places Text Search API
async def fetch_google_places(query: str, max_results: int = 5) -> List[dict]:
    params = {
        "query": query,
        "key": GOOGLE_PLACES_API_KEY
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(PLACES_ENDPOINT, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])[:max_results]
            return [
                {
                    "name": r.get("name"),
                    "address": r.get("formatted_address"),
                    "lat": r.get("geometry", {}).get("location", {}).get("lat"),
                    "lng": r.get("geometry", {}).get("location", {}).get("lng"),
                    "rating": r.get("rating"),
                    "price_level": r.get("price_level"),
                    "types": r.get("types", []),
                    "place_id": r.get("place_id"),
                    "source_query": query
                }
                for r in results
            ]
    except Exception as e:
        print(f"Query failed: {query}\nError: {e}")
        return []

# enrichment 用于结构化给到的地点
async def enrich_web_places(web_places: List[str], location: str, max_results_per_place: int = 1) -> List[dict]:
    enriched = []
    seen = set()

    for place in web_places:
        query = f"{place} in {location}"
        results = await fetch_google_places(query, max_results=max_results_per_place)
        for r in results:
            if r["place_id"] and r["place_id"] not in seen:
                seen.add(r["place_id"])
                r["matched_from"] = place
                r["source_query"] = query
                enriched.append(r)

    return enriched

# 主函数：结合 Google 查询 + Web 抓取地名 enrichment
async def gather_activity_pois(
    location: str,
    mbti: str = "",
    theme: str = "culture",
    inclusion: Optional[List[str]] = None,
    web_places: Optional[List[str]] = None,
    max_queries: int = 8,
    max_results_per_query: int = 5
) -> List[dict]:
    print(f"🔍 gather_activity_pois called with: location={location}, theme={theme}, mbti={mbti}")
    queries = build_activity_queries(location, mbti, theme, inclusion)
    seen = set()
    all_results = []

    # Google 构造查询部分
    for query in queries[:max_queries]:
        pois = await fetch_google_places(query, max_results=max_results_per_query)
        for poi in pois:
            if poi["place_id"] and poi["place_id"] not in seen:
                seen.add(poi["place_id"])
                poi["source"] = "api"
                all_results.append(poi)

    # web_content enrichment 部分
    if web_places:
        web_results = await enrich_web_places(web_places, location)
        for poi in web_results:
            if poi["place_id"] and poi["place_id"] not in seen:
                seen.add(poi["place_id"])
                poi["source"] = "web"
                all_results.append(poi)
    # Apply MBTI scoring before returning
    all_results = apply_mbti_scoring(all_results, mbti)

    # call search_nearby_restaurants for each high rated activity
    top_activities = sorted(all_results, key=lambda x: x.get('score', 0), reverse=True)[:4]

    for activity in top_activities:  # Use each activity's location
        nearby_restaurants = await search_nearby_restaurants(
            activity['lat'],     # Use EACH activity's coordinates
            activity['lng'], 
            location, 
            mbti,
            max_results=3
        )
        # Add restaurants directly to all_results (avoiding duplicates)
        for restaurant in nearby_restaurants:
            if restaurant["place_id"] not in seen:
                seen.add(restaurant["place_id"])
                all_results.append(restaurant)
     
        # Count activities vs restaurants for debug
    activities_count = len([r for r in all_results if r.get('category') != 'restaurant'])
    restaurants_count = len([r for r in all_results if r.get('category') == 'restaurant'])
    
    print(f"✅ gather_activity_pois returning {len(all_results)} total POIs ({activities_count} activities + {restaurants_count} restaurants)")
    return all_results

def apply_mbti_scoring(pois: List[dict], mbti: str) -> List[dict]:
    """Apply MBTI-based scoring to POI list"""
    for poi in pois:
        rating = poi.get('rating') or 4.0  # Handle None ratings
        base_score = (rating - 1) * 20  # Convert 1-5 rating to 0-80
        poi_types = [t.lower() for t in poi.get('types', [])]
        
        # MBTI bonuses
        mbti_bonus = 0
        
        # Extrovert vs Introvert
        if 'E' in mbti:
            if any(t in poi_types for t in ['shopping_mall', 'amusement_park', 'night_club']):
                mbti_bonus += 10
        else:  # Introvert
            if any(t in poi_types for t in ['library', 'museum', 'park', 'garden']):
                mbti_bonus += 10
        
        # Sensor vs Intuitive  
        if 'S' in mbti:
            if any(t in poi_types for t in ['restaurant', 'store', 'market', 'food']):
                mbti_bonus += 5
        else:  # Intuitive
            if any(t in poi_types for t in ['museum', 'art_gallery', 'university']):
                mbti_bonus += 5
        
        # Feeler bonus
        if 'F' in mbti:
            if any(t in poi_types for t in ['zoo', 'aquarium', 'park', 'place_of_worship']):
                mbti_bonus += 5
        
        # Final score
        poi['score'] = min(100, max(60, base_score + mbti_bonus + 10))  # Score between 60-100
    
    return pois