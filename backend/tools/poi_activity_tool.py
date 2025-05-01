import json
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_ENDPOINT = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# 构造活动相关的搜索 query（始终围绕电影主题）
def build_activity_queries(
    location: str,
    mbti: str,
    inclusion: Optional[List[str]] = None,
) -> List[str]:
    queries = [
        f"movie attractions in {location}",
        f"movie themed experiences in {location}",
        f"movie filming locations in {location}",
        f"movie experience for {mbti} in {location}",
    ]

    if inclusion:
        for inc in inclusion:
            queries.append(f"{inc} in {location} related to movies")
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

# enrichment 用于结构化 web_content_agent 给到的地点
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
    mbti: str,
    inclusion: Optional[List[str]] = None,
    web_places: Optional[List[str]] = None,
    max_queries: int = 8,
    max_results_per_query: int = 5
) -> List[dict]:
    queries = build_activity_queries(location, mbti, inclusion)
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

    return all_results
