# backend/my_tools/poi_and_cost.py
"""
包含用于搜索兴趣点 (POI) 和估算成本的工具。
主要包括：
- Tavily 网络搜索工具 (web_search)
- Google Places POI 搜索工具 (POISearchTool)
- 成本估算工具 (CostEstimatorTool)
"""
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
from autogen_agentchat.tools import register_tool
import httpx

# 从 .env 文件加载环境变量
load_dotenv()


# --- Tavily Web Search Tool ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    # 注意：如果不需要 web_search 功能，可以将此检查注释掉或移除
    print("警告: TAVILY_API_KEY 未在 .env 文件中设置。web_search 工具将不可用。")
    # raise RuntimeError("请在 .env 文件中设置 TAVILY_API_KEY 环境变量。")

# @register_tool 装饰器用于向 AutoGen Agent 注册此函数作为一个可调用工具
# 如果 Agent 的 tools 参数包含了这个函数 (或其包装器)，Agent 就可以调用它
@register_tool(name="web_search", description="执行 Tavily 搜索并返回相关的网页结果列表。")
async def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    使用 Tavily API 执行网络搜索。

    Args:
        query (str): 用户的搜索查询。
        max_results (int): 希望返回的最大搜索结果数量。

    Returns:
        List[Dict]: 包含搜索结果的列表，每个结果是一个字典，包含 'title', 'url', 'snippet'。
                   'snippet' 是网页内容的摘要。

    Raises:
        RuntimeError: 如果 TAVILY_API_KEY 未设置。
        httpx.HTTPStatusError: 如果 API 请求失败。
    """
    if not TAVILY_API_KEY:
        return [{"error": "Tavily API key not configured."}]
        # raise RuntimeError("Tavily API key not configured.")

    tavily_url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    payload = {
        "query": query,
        "search_depth": "basic",  # 'basic' 或 'advanced' (更贵)
        "max_results": max_results,
        "include_domains": [],  # 可以指定只搜索特定域名
        "exclude_domains": [],  # 可以指定排除特定域名
        "include_raw_content": False, # False 表示只返回摘要 (snippet)
        "include_answer": False # 是否包含 AI 生成的答案
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client: # 增加超时时间
        try:
            response = await client.post(tavily_url, headers=headers, json=payload)
            response.raise_for_status() # 检查 HTTP 错误状态
            data = response.json()
        except httpx.RequestError as exc:
            print(f"调用 Tavily API 时发生网络错误: {exc}")
            # 返回错误信息或空列表，避免中断整个流程
            return [{"error": f"Failed to connect to Tavily API: {exc}"}]
        except httpx.HTTPStatusError as exc:
            print(f"Tavily API 返回错误状态: {exc.response.status_code} - {exc.response.text}")
            return [{"error": f"Tavily API error: {exc.response.status_code}"}]

    results = []
    for item in data.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", "") # 'content' 字段通常是摘要
        })

    return results



# --- Google Places POI Search Tool ---
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
if not GOOGLE_PLACES_API_KEY:
    raise RuntimeError("Please set the GOOGLE_PLACES_API_KEY environment variable in your .env file.")

# POI 搜索工具类
# 注意：此类并未直接使用 @register_tool，而是其实例的方法被包装后传递给 Agent
class POISearchTool:
    """
    使用 Google Places API (Text Search) 搜索 POI 的工具。
    可以根据主题、地点、MBTI 等搜索餐馆和活动。
    """
    name = "poi_search"
    description = (
        "根据主题 (theme) 和地点 (location) 搜索 POI (兴趣点)，" # 移除 n_days 相关描述，由 Agent 控制数量
        "为行程规划生成餐馆 (Meal) 和活动 (Activity) 建议。"
        "返回带有天数建议 (day)、预估持续时间 (time) 和基础成本 (cost) 标签的 POI 列表。"
    )

    # 注意：此 run 方法目前不直接处理 potential_names, inclusion, exclusion。
    # 这些参数的过滤逻辑建议由调用此工具的 poi_agent 通过其 LLM 能力在获取结果后执行。
    async def run(self, theme: str, location: str, n_days: int, mbti: str, field: str = "both") -> List[Dict]:
        """
        执行 Google Places API 的 Text Search 来查找 POI。

        Args:
            theme (str): 行程主题，例如 "Movie", "History"。
            location (str): 目的地，例如 "Los Angeles, CA"。
            n_days (int): 行程的总天数，用于决定需要查找多少 POI。
            mbti (str): 用户的 MBTI 类型，用于个性化查询，例如 "INFP"。
            field (str): 指定查找的 POI 类型，'Meal', 'Activity', 或 'both' (默认)。
                      (当前实现会同时查找两者，忽略此参数)

        Returns:
            List[Dict]: 包含 POI 信息的字典列表。每个字典包含:
                - day (int): 建议分配的行程天数 (基于索引计算)。
                - name (str): POI 名称。
                - type (str): POI 类型 ('Meal' 或 'Activity')。
                - address (str): POI 地址。
                - lat (float): 纬度。
                - lng (float): 经度。
                - rating (float): 用户评分 (可能为空)。
                - price_level (int): 价格等级 (1-4，可能为空，默认为 1)。
                - time (str): 预估的持续时间 ('1h' for Meal, '2h' for Activity)。
                - cost (str): 基础成本估算 (基于 price_level 计算，格式如 '$15')。
                - place_id (str): Google Places POI 的唯一 ID。

        Raises:
            httpx.HTTPStatusError: 如果 Google Places API 请求失败。
        """
        base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        # 准备查询语句，结合主题、MBTI 和地点
        meal_query = f"{theme} restaurant for {mbti} personality in {location}" # 更具体的查询
        activity_query = f"{theme} attraction or activity for {mbti} personality in {location}"

        # 需要获取的 POI 数量 (大约每天 2 餐 + 2 活动)
        num_each_type = n_days * 2

        items: List[Dict] = []

        async with httpx.AsyncClient(timeout=15) as client: # 增加超时时间
            # --- 搜索餐馆 (Meal) ---
            try:
                print(f"Searching Meals: {meal_query}")
                meal_resp = await client.get(base_url, params={"query": meal_query, "key": GOOGLE_PLACES_API_KEY})
                meal_resp.raise_for_status()
                meal_data = meal_resp.json()
                raw_meals = meal_data.get("results", [])[:num_each_type]
                print(f"Found {len(raw_meals)} raw meal results.")

                # 处理餐馆结果
                for idx, res in enumerate(raw_meals):
                    day = (idx // 2) + 1 # 简单地将结果分配到天数中
                    name = res.get("name")
                    address = res.get("formatted_address") or res.get("vicinity")
                    loc = res.get("geometry", {}).get("location", {})
                    lat = loc.get("lat")
                    lng = loc.get("lng")
                    rating = res.get("rating")
                    # Google Places price_level: 0 (Free) to 4 (Very Expensive)
                    # 如果缺失，我们假设一个较低的默认值，例如 1 或 2
                    price_level = res.get("price_level", 1) # 假设默认为 1 ($)
                    place_id = res.get("place_id")
                    duration = "1h"  # 餐馆的预估持续时间
                    # 基础成本估算：可以根据 price_level 调整基数和倍数
                    # price_level 1=$15, 2=$30, 3=$45, 4=$60 (示例)
                    base_cost = (price_level or 1) * 15
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
                        "cost": f"${base_cost}", # 格式化成本
                        "place_id": place_id,
                    })
            except httpx.RequestError as e:
                print(f"Error during Google Places Meal Search (Network): {e}")
                # 可以考虑返回部分结果或错误信息
            except httpx.HTTPStatusError as e:
                print(f"Error during Google Places Meal Search (API Status {e.response.status_code}): {e.response.text}")

            # --- 搜索活动 (Activity) ---
            try:
                print(f"Searching Activities: {activity_query}")
                act_resp = await client.get(base_url, params={"query": activity_query, "key": GOOGLE_PLACES_API_KEY})
                act_resp.raise_for_status()
                act_data = act_resp.json()
                raw_acts = act_data.get("results", [])[:num_each_type]
                print(f"Found {len(raw_acts)} raw activity results.")

                # 处理活动结果
                for idx, res in enumerate(raw_acts):
                    day = (idx // 2) + 1 # 同样简单分配天数
                    name = res.get("name")
                    address = res.get("formatted_address") or res.get("vicinity")
                    loc = res.get("geometry", {}).get("location", {})
                    lat = loc.get("lat")
                    lng = loc.get("lng")
                    rating = res.get("rating")
                    price_level = res.get("price_level", 2) # 活动的默认 price_level 可以设高一点，比如 2
                    place_id = res.get("place_id")
                    duration = "2h"  # 活动的预估持续时间
                    # 活动的基础成本估算可能需要不同的逻辑，这里仍然使用 price_level
                    # price_level 1=$15, 2=$30, 3=$60, 4=$100 (示例)
                    cost_multiplier = 15 if price_level <= 2 else (30 if price_level == 3 else 50)
                    base_cost = (price_level or 2) * cost_multiplier
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
                        "cost": f"${base_cost}", # 格式化成本
                        "place_id": place_id,
                    })
            except httpx.RequestError as e:
                print(f"Error during Google Places Activity Search (Network): {e}")
            except httpx.HTTPStatusError as e:
                print(f"Error during Google Places Activity Search (API Status {e.response.status_code}): {e.response.text}")

        print(f"Total POIs fetched: {len(items)}")
        # TODO (在 poi_agent 中): 根据 potential_names, inclusion, exclusion 进一步筛选或排序这里的 items
        return items

# --- Cost Estimator Tool ---
# 成本估算工具类
class CostEstimatorTool:
    """
    根据 POI 的评分等因素，优化其成本估算的工具。
    可以被 critic_agent 用来微调预算。
    """
    name = "cost_estimator"
    description = (
        "根据评分 (rating) 和价格等级 (price_level) 等因素，" # 添加 price_level
        "优化 POI 列表中的成本 (cost) 字段。"
    )

    # 注意：此方法直接修改传入的列表中的字典
    def run(self, items: List[Dict]) -> List[Dict]:
        """
        接收 POI 列表，并更新其中每个 POI 的 'cost' 字段。

        Args:
            items (List[Dict]): 包含 POI 信息的字典列表。
                                 每个字典需要包含 'cost' 字段 (如 '$15')，
                                 并且最好有 'rating' 和 'price_level' 字段。

        Returns:
            List[Dict]: 更新了 'cost' 字段的原始列表。
        """
        # 示例策略：高评分增加成本，低评分减少成本。
        # 可以根据需要实现更复杂的逻辑，例如结合 price_level。
        for entry in items:
            try:
                # 尝试解析现有成本，去除 '$' 符号
                base_cost_str = entry.get("cost", "$0").strip("$")
                base_cost = float(base_cost_str)
            except (ValueError, TypeError):
                base_cost = 0.0 # 如果解析失败，默认为 0

            rating = entry.get("rating")
            price_level = entry.get("price_level") # 获取 price_level
            final_cost = base_cost # 默认等于基础成本

            # 基于评分调整成本 (示例)
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
