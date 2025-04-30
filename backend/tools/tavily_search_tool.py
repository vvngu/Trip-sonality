import os
import httpx
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

async def web_search(query: str, max_results: int = 5) -> List[Dict]:
    if not TAVILY_API_KEY:
        return [{"error": "Tavily API key not configured."}]

    url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    payload = {
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_raw_content": False,
        "include_answer": False
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Tavily API error: {e}")
            return []

    return [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", "")
        }
        for item in data.get("results", [])
    ]


import requests
from bs4 import BeautifulSoup

def clean_html_from_url(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # 只提取有结构含义的部分（不含正文长文段）
        items = soup.find_all(["li", "h2", "strong", "b"])
        lines = [item.get_text(strip=True) for item in items if item.get_text()]
        text = "\n".join(lines)
        return text[:1500]  # 控制总长度
    except Exception as e:
        print(f"[clean_html_from_url] Parse error: {e}")
        return ""
