# backend/autogen_itinerary.py
"""
使用 AutoGen AgentChat 框架，通过多 Agent 协作生成个性化旅行行程。
整合了用户输入处理、网络搜索、地点查找、行程规划、审阅优化和格式化输出的全链路流程。

Requires in .env:
  - API_HOST: 'github' or 'azure' (default 'github')
  - GITHUB_TOKEN: GitHub PAT with models:read (for GitHub Models)
  - GITHUB_MODEL: GitHub model name (e.g. 'gpt-4o')
  - AZURE_OPENAI_CHAT_MODEL, AZURE_OPENAI_CHAT_DEPLOYMENT, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_VERSION, AZURE_OPENAI_KEY (for Azure OpenAI)
  - GOOGLE_PLACES_API_KEY: Google Places API key
  依赖 .env 文件中的环境变量:
  - OPENAI_API_KEY: OpenAI API 密钥
  - TAVILY_API_KEY: Tavily API 密钥 (用于 web_search)
  - GOOGLE_PLACES_API_KEY: Google Places API 密钥 (用于 poi_search)

Usage:
  python autogen_itinerary.py '<json-string>'
"""
import asyncio
from http.client import HTTPException
import json
import os
from typing import List, Dict, Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient
from dotenv import load_dotenv
from my_tools.poi_and_cost import POISearchTool, CostEstimatorTool, web_search as tavily_web_search # 显式导入 web_search

from openai import OpenAI

# Setup the client to use either Azure OpenAI or GitHub Models
load_dotenv(override=True)
API_HOST = os.getenv("API_HOST", "github")


# if API_HOST == "github":
#     client = OpenAIChatCompletionClient(model=os.getenv("GITHUB_MODEL", "gpt-4o"), api_key=os.environ["GITHUB_TOKEN"], base_url="https://models.inference.ai.azure.com")
# elif API_HOST == "azure":
#     token_provider = azure.identity.get_bearer_token_provider(azure.identity.DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
#     client = AzureOpenAIChatCompletionClient(
#         model=os.environ["AZURE_OPENAI_CHAT_MODEL"],
#         api_version=os.environ["AZURE_OPENAI_VERSION"],
#         azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
#         azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
#         azure_ad_token_provider=token_provider,
#     )

client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"  # 不需要改
)
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("请在 .env 文件中设置 OPENAI_API_KEY")

# --- 工具初始化 ---
# POI 搜索工具实例 (Google Places API)
poi_tool = POISearchTool()
# 成本估算工具实例 (用于优化成本)
cost_tool = CostEstimatorTool()

# --- 工具函数包装 ---
# 将工具方法包装成 Agent 可调用的函数
# Tavily Web Search 工具函数
async def web_search(query: str, max_results: int = 7) -> List[Dict]:
    """
    包装 Tavily web_search 工具函数，供 Agent 调用。
    执行网络搜索并返回相关结果列表。
    """
    print(f"--- Calling Tavily Web Search: query='{query}', max_results={max_results} ---")
    results = await tavily_web_search(query=query, max_results=max_results)
    print(f"--- Tavily Web Search Results Count: {len(results)} ---")
    return results

# POI 搜索工具函数 (Google Places)
async def poi_search(theme: str, location: str, n_days: int, mbti: str, field: str = "both", potential_names: List[str] = None, inclusion: List[str] = None, exclusion: List[str] = None) -> List[Dict]:
    """
    包装 POISearchTool 的 run 方法，供 Agent 调用。
    根据主题、地点、天数、MBTI 等搜索 POI（餐馆和活动）。
    新增: 接收 potential_names, inclusion, exclusion 用于结果筛选或优先级排序 (具体逻辑在 POISearchTool.run 中实现或由 poi_agent 处理)。
    """
    print(f"--- Calling POI Search: theme='{theme}', location='{location}', n_days={n_days}, mbti='{mbti}', potential_names={potential_names}, inclusion={inclusion}, exclusion={exclusion} ---")
    # 注意: POISearchTool.run 的签名可能需要更新以接收新参数
    # 这里暂时假设它能处理这些参数，或者 poi_agent 会在调用后进行过滤
    items = await poi_tool.run(theme=theme, location=location, n_days=n_days, mbti=mbti, field=field)
    # TODO: 在 POISearchTool.run 内部或这里添加基于 potential_names, inclusion, exclusion 的过滤逻辑
    print(f"--- POI Search Initial Results Count: {len(items)} ---")
    # 示例过滤逻辑 (可以在 poi_agent 的 prompt 中指导，或直接在工具中实现)
    # filtered_items = [item for item in items if item['name'] in potential_names] # 基于名字过滤
    # filtered_items = [item for item in items if not any(ex in item['name'].lower() for ex in exclusion)] # 基于排除词过滤
    return items # 返回原始或过滤后的列表

# 成本估算工具函数
def cost_estimate(items: List[Dict]) -> List[Dict]:
    """
    包装 CostEstimatorTool 的 run 方法，供 Agent 调用。
    根据评分等因素优化 POI 列表的成本估算。
    """
    print(f"--- Calling Cost Estimator for {len(items)} items ---")
    updated_items = cost_tool.run(items=items)
    print(f"--- Cost Estimator Finished ---")
    return updated_items

# --- Prompt 加载函数 ---
def _load_prompt(file: str) -> str:
    """从 prompts 文件夹加载指定文件的内容作为 Agent 的系统提示。"""
    path = os.path.join("backend", "prompts", f"{file}.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception as e:
        print(f"加载 Prompt 文件 {path} 时出错: {e}")
        return "You are a helpful AI assistant."

# --- Agent 定义 ---

# Agent 1: summarize_agent - 用户输入验证和标准化
summarize_agent = AssistantAgent(
    name="summarize_agent",
    model_client=client,
    description=(
        "This agent analyzes the raw user input (MBTI, budget, query, and optional itinerary) "
        "and produces a structured JSON summary with fields such as theme, location, travel dates, "
        "inclusion and exclusion preferences. If location is invalid or missing, it returns an error_type."
    ),
    system_message=_load_prompt("summarize_agent")  # 从 prompts/summarize_agent.txt 中读取
)

# Agent 2: search_agent - 使用 Tavily 进行网络搜索
search_agent = AssistantAgent(
    name="search_agent",
    model_client=client,
    tools=[web_search], # 注册 web_search 工具
    description=(
        "第二步：接收 summarize_agent 输出的标准化 JSON。根据主题和地点，构造搜索查询（例如 '洛杉矶的电影主题景点'），"
        "调用 web_search 工具执行 Tavily 搜索，获取相关网页结果（标题、URL、摘要）。"
    ),
    system_message="""你是网络搜索代理。
    你的任务是接收标准化的用户请求 JSON（包含 theme, location 等字段）。
    根据 theme 和 location 构造一个或多个精确的搜索查询。
    调用 `web_search` 工具来查找相关的景点、活动或餐厅。
    搜索查询示例: "{theme} attractions in {location}", "{theme} restaurants in {location} for {mbti}", "things to do in {location} related to {theme}".
    你需要选择最合适的查询。
    将 `web_search` 返回的原始结果列表（包含 title, url, snippet）整理成 JSON 格式输出: {"search_results": [ { "title": ..., "url": ..., "snippet": ... }, ... ]}
    """
)

# Agent 3: web_content_agent - 网页内容提取与总结
web_content_agent = AssistantAgent(
    name="web_content_agent",
    model_client=client,
    # 注意：如果需要实际抓取网页内容，这里可能需要添加一个网页抓取工具
    # tools=[web_scraper_tool], # 假设有一个 web_scraper_tool
    description=(
        "第三步：接收 search_agent 输出的网页搜索结果。分析结果中的 snippets（摘要），"
        "（可选：如果摘要信息不足，可以调用工具抓取关键 URL 的正文内容）。"
        "识别并提取潜在的 POI（景点、餐厅等）名称列表。"
        "结合用户偏好（inclusion/exclusion）进行初步筛选。"
        "输出潜在 POI 名称列表 JSON: {"potential_poi_names": ["POI Name 1", "POI Name 2", ...]}"
    ),
    system_message="""你是网页内容分析和提取代理。
    你的任务是接收 `search_agent` 返回的搜索结果 JSON `{"search_results": [...]}` 和来自 `summarize_agent` 的标准化用户请求 JSON (包含 `inclusion`, `exclusion` 字段)。
    1. 分析 `search_results` 列表中的 `snippet` 文本。
    2. 从这些文本中识别并提取出具体的、潜在的地点名称（景点、餐厅、活动场所等）。
    3. （可选高级功能：如果 `snippet` 信息不足以判断，可以考虑调用网页抓取工具获取更详细信息，但这通常不是必须的，优先依赖摘要）。
    4. 参考用户请求中的 `inclusion` 和 `exclusion` 列表，对提取出的地点名称进行初步过滤。确保结果符合用户偏好。
    5. 输出一个 JSON 对象，包含最终筛选后的潜在 POI 名称列表: `{"potential_poi_names": ["地点A", "地点B", ...]}`。列表不能为空，如果分析后没有合适的地点，返回 `{"potential_poi_names": []}`。
    """
)

# Agent 4: poi_agent - 标准化地点数据 (Google Places)
poi_agent = AssistantAgent(
    name="poi_agent",
    model_client=client,
    tools=[poi_search], # 注册 poi_search 工具 (Google Places)
    description=(
        "第四步：接收 web_content_agent 输出的潜在 POI 名称列表和 summarize_agent 的标准化请求。"
        "主要目标是获取标准化的 POI 数据。调用 `poi_search` 工具，"
        "传入 theme, location, n_days, mbti 等信息来查找合适的餐馆和活动。"
        "（可选增强：可以尝试将 `potential_poi_names` 作为线索传递给 `poi_search` 工具或在获取结果后进行匹配/筛选）。"
        "确保生成足够数量（例如每天 2 餐 + 2 活动）的 POI。"
        "输出包含详细信息的 POI 列表 JSON: {"items": [ {day, name, type, address, lat, lng, rating, price_level, time(duration), cost, place_id}, ... ]}"
    ),
    system_message="""你是地点信息查找和标准化代理。
    你的任务是接收 `web_content_agent` 输出的 `{"potential_poi_names": [...]}` 列表和 `summarize_agent` 输出的标准化请求 JSON (`theme`, `location`, `dates` (n_days), `mbti`, `inclusion`, `exclusion`)。
    1. 主要目标是利用 `poi_search` 工具获取结构化的 POI 数据（餐馆和活动）。
    2. 调用 `poi_search` 工具，必须提供 `theme`, `location`, `n_days`, `mbti` 参数。
    3. （可选策略）你可以将 `potential_poi_names`, `inclusion`, `exclusion` 作为参数传递给 `poi_search`（如果工具支持），或者在获取 `poi_search` 结果后，根据这些信息进行筛选或排序，优先选择匹配的地点。
    4. 确保工具调用返回的 `items` 列表包含足够数量的 POI (至少 `2 * n_days` 餐馆 和 `2 * n_days` 活动)。
    5. 输出 `poi_search` 工具返回的结构化 POI 列表，格式为 JSON: `{"items": [ { "day": ..., "name": ..., "type": ..., ... }, ... ]}`。确保包含所有必要的字段：day, name, type, address, lat, lng, rating, price_level, time(duration), cost, place_id。
    """
)

# Agent 5: plan_agent - 安排行程
plan_agent = AssistantAgent(
    name="plan_agent",
    model_client=client,
    description=(
        "第五步：接收 poi_agent 输出的详细 POI 列表和 summarize_agent 的标准化请求（尤其是天数）。"
        "根据天数，将 POI 合理地分配到每天的行程中。"
        "目标是每天大约 2 餐 + 1-2 个活动，避免行程过密或过疏。"
        "将持续时间（如 '2h'）转换为大致的时间段（需要LLM判断）。"
        "输出初步的行程计划 JSON: {"itinerary": [ {day, food:[], activities:[], summary}, ... ]}"
    ),
    system_message="""你是行程规划代理。
    你的任务是接收 `poi_agent` 输出的 POI 列表 JSON `{"items": [...]}` 和 `summarize_agent` 的请求 JSON (需要 `dates` (n_days))。
    1. 分析 `items` 列表，其中每个 POI 都有一个建议的 `day` 编号。
    2. 按照 `day` 将这些 POI 分组。
    3. 为每个 POI 分配一个合理的时间段。考虑 POI 的 `type`（Meal/Activity）和 `time`（持续时间，如 "1h", "2h"），并根据常识安排时间（例如，午餐在中午，晚餐在晚上，活动在白天）。输出的时间格式应为 "HH:MM-HH:MM"（例如 "12:00-13:00", "14:00-17:00"）。
    4. 确保每天的行程包含大约 2 个 Meal 和 1-2 个 Activity。如果 `poi_agent` 提供的 POI 数量不足或过多，你需要做出合理选择或调整。
    5. 为每天生成一个简短的总结 (summary)。
    6. 输出一个 JSON 对象，包含 `itinerary` 数组:
       ```json
       {
         "itinerary": [
           {
             "day": <day_number>,
             "food": [
               { "name": "<Meal Name>", "time": "<HH:MM-HH:MM>", "cost": "<$cost>" },
               ...
             ],
             "activities": [
               { "name": "<Activity Name>", "time": "<HH:MM-HH:MM>", "cost": "<$cost>" },
               ...
             ],
             "summary": "<Daily summary text>"
           },
           ... // 后面几天的行程
         ]
       }
       ```
    确保输出的 JSON 格式严格符合要求。
    """
)

# Agent 6: critic_agent - 审阅与优化
critic_agent = AssistantAgent(
    name="critic_agent",
    model_client=client,
    tools=[cost_estimate], # 注册 cost_estimate 工具
    description=(
        "第六步：接收 plan_agent 生成的初步行程计划和 summarize_agent 的标准化请求（尤其是 budget）。"
        "评估计划的合理性：预算是否超标？活动安排是否过于密集或不合逻辑？路线是否可行（可选，基于常识判断）？"
        "可以调用 `cost_estimate` 工具来优化成本估算。"
        "进行必要的微调（如调整活动顺序、替换超预算项目等）。"
        "输出优化后的行程计划 JSON，结构与 plan_agent 输出相同。"
    ),
    system_message="""你是行程审阅和优化代理。
    你的任务是接收 `plan_agent` 生成的行程计划 JSON `{"itinerary": [...]}` 和 `summarize_agent` 的请求 JSON (需要 `budget` 和 `items` 列表 - 可能需要从 `poi_agent` 的输出传递过来，或者让 `plan_agent` 在其输出中包含原始 `items`)。
    1. **成本检查**: 计算行程的总成本，并与用户 `budget` 对比。
    2. **成本优化 (可选)**: 如果需要更精确的成本或希望基于评分调整成本，可以准备 `items` 列表（需要包含 rating 和 cost 字段），然后调用 `cost_estimate` 工具。你需要将更新后的成本应用回 `itinerary` 中。
    3. **合理性检查**: 评估每天的活动安排是否过于密集或空闲？时间分配是否合理？是否存在明显的逻辑冲突（例如，两个活动时间重叠）？
    4. **预算调整**: 如果总成本超出预算，尝试进行调整。可以替换掉一些高成本的活动/餐厅，或者移除优先级较低的项目。优先保留符合用户 `inclusion` 偏好的项目。
    5. **微调**: 对活动顺序、时间安排等进行细微调整，使行程更流畅。
    6. 输出最终优化后的行程计划 JSON，其结构必须与 `plan_agent` 的输出完全一致: `{"itinerary": [ {day, food:[], activities:[], summary}, ... ]}`。
    """
    # 注意: critic_agent 可能需要访问 poi_agent 输出的原始 items 列表来进行成本估算和替换决策。
    # 这需要在 Agent 间传递数据时考虑，或者调整 plan_agent 的输出包含必要信息。
)

# Agent 7: format_agent - 整理最终输出
format_agent = AssistantAgent(
    name="format_agent",
    model_client=client,
    description=(
        "第七步（最后一步）：接收 critic_agent 优化后的最终行程计划。"
        "还需要访问 poi_agent 输出的 POI 列表以提取位置信息。"
        "生成前端所需的两种 JSON 结构：`locations` (包含 ID, name, position) 和 `itinerary`。"
        "确保所有字段都正确填充，格式符合要求。"
        "输出包含这两个结构的最终 JSON 对象，并以 TERMINATE 结束。"
    ),
    system_message="""你是最终格式化代理。
    你的任务是接收 `critic_agent` 输出的最终行程计划 JSON `{"itinerary": [...]}`。你还需要访问 `poi_agent` 输出的原始 POI 列表 `{"items": [...]}` (包含经纬度 lat, lng)。
    1. **创建 `locations` 列表**:
       - 遍历 `poi_agent` 输出的 `items` 列表。
       - 对于每个 item，提取 `name`, `lat`, `lng`。
       - 创建一个 `locations` 数组，每个元素格式如下：
         `{ "id": <index>, "name": "<POI Name>", "position": { "lat": <latitude>, "lng": <longitude> } }`
       - 确保每个在最终 `itinerary` 中出现的地点都在 `locations` 列表中，并且 ID 唯一。

    2. **整理 `itinerary` 列表**:
       - 使用 `critic_agent` 输出的 `itinerary` 数组。确保其结构和内容符合最终要求。

    3. **组合最终输出**:
       - 创建一个包含 `locations` 和 `itinerary` 两个键的 JSON 对象。
       - 格式如下：
         ```json
         {
           "locations": [
             { "id": 0, "name": "...", "position": { "lat": ..., "lng": ... } },
             ...
           ],
           "itinerary": [
             { "day": 1, "food": [...], "activities": [...], "summary": "..." },
             ...
           ]
         }
         ```
    4. 确保整个输出是有效的 JSON。
    5. 在输出最终的 JSON 对象后，必须紧接着响应 `TERMINATE`。
    """
    # 注意: format_agent 需要同时访问 critic_agent 的输出和 poi_agent 的输出。
    # 这需要在 MagenticOneGroupChat 的消息传递或状态管理中处理。
)

# planner_agent = AssistantAgent(
#     "planner_agent",
#     model_client=client,
#     description="A planner agent that use his/her knowledge to generate or revise a day-by-day itinerary outline.",
#     system_message="You are a trip planning assistant. You will receive JSON input containing keys: budget, dates, location, mbti, theme, field, optionally _previous_itinerary. Your task is to generate a JSON array of objects [{day, food, activities, summary}].",
# )

# detail_agent = AssistantAgent(
#     "detail_agent",
#     model_client=client,
#     tools=[poi_search, cost_estimate], 
#     description="A helpful assistant that can provide detailed information and cost with tools poi_search and cost_estimate for visiting about the destination.",
#     system_message="You will receive an itinerary outline and user input. Your primary function is to enrich this outline by getting more detailed information for places suggested using poi_search tool and estimate the cost of visiting for place using cost_estimate tool, ensure the original JSON structure is preserved.",
# )

async def run_autogen_workflow(initial_user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    运行完整的 AutoGen Agent 工作流来生成行程。

    Args:
        initial_user_input: 包含用户输入的字典，例如:
            {
                "mbti": "INFP",
                "Budget": 5000,
                "Query": "I want a 5-day movie-themed trip to Los Angeles. Focus on studio tours and classic restaurants, but avoid nightlife.",
                "CurrentItinerary": null # 或者包含之前的行程 JSON
            }

    Returns:
        包含最终行程计划的字典 (格式符合 format_agent 的输出)。

    Raises:
        HTTPException: 如果用户输入验证失败 (例如，无效地点)。
        Exception: 如果 Agent 工作流中发生其他错误。
    """
    print("--- Starting AutoGen Workflow ---")
    print(f"Initial User Input: {initial_user_input}")

    # 定义 Agent 序列
    agents = [
        summarize_agent,
        search_agent,
        web_content_agent,
        poi_agent,
        plan_agent,
        critic_agent,
        format_agent
    ]

    # 设置终止条件：当 format_agent 输出包含 "TERMINATE" 时结束
    termination = TextMentionTermination(mention="TERMINATE", agent=format_agent)

    # 创建 MagenticOneGroupChat 实例
    # 它会按顺序执行 Agent，并将前一个 Agent 的输出作为下一个 Agent 的输入
    group_chat = MagenticOneGroupChat(
        agents=agents,
        termination_condition=termination,
        model_client=client, # 可以为 group chat 本身指定一个 client，用于管理流程
    )

    # --- 数据传递说明 ---
    # MagenticOneGroupChat 默认将上一个 Agent 的最后一条消息内容作为下一个 Agent 的输入。
    # 这对于简单线性流程是足够的。
    # 但在这个流程中，后面的 Agent (如 critic_agent, format_agent) 可能需要访问前面多个 Agent 的输出
    # (例如，format_agent 需要 critic_agent 的 itinerary 和 poi_agent 的 items)。
    #
    # 处理方式:
    # 1. **修改 Agent 输出**: 让 Agent 在其输出中包含所有下游可能需要的信息。
    #    例如，plan_agent 的输出可以是一个包含 "itinerary" 和原始 "items" 的字典。
    #    这是最直接的方式，但可能导致消息体变大。
    # 2. **自定义 GroupChatManager**: 继承 MagenticOneGroupChat 并重写消息选择逻辑，
    #    维护一个共享的状态或显式地将需要的历史消息传递给当前 Agent。这更灵活但更复杂。
    # 3. **调整 Agent Prompt**: 指导 Agent 在需要时明确向上一个或更早的 Agent 请求所需信息（但这会增加交互轮次）。
    #
    # **当前实现选择方式 1 的简化版**:
    # - 我们将在 Agent 的 Prompt 中指导它们输出下游需要的信息。
    # - 例如，指导 poi_agent 在输出 `{"items": ...}` 时包含所有需要的信息。
    # - 指导 plan_agent 输出 `{"itinerary": ..., "original_items_for_critic": ...}` (如果 critic 需要)。
    # - 指导 critic_agent 输出 `{"itinerary": ..., "original_items_for_formatter": ...}` (如果 formatter 需要)。
    # 这需要在 Agent 的 system_message 中明确指示。

    # 准备初始任务消息
    # 将用户的字典输入转换为 JSON 字符串，作为 summarize_agent 的初始输入
    initial_task = json.dumps(initial_user_input)

    print(f"--- Initiating Group Chat with Task: {initial_task[:200]}... ---") # 打印部分任务内容

    try:
        # 运行 Agent 流程
        # 使用 run() 而不是 run_stream() 来获取最终结果
        final_result = await group_chat.run(task=initial_task)

        print("--- AutoGen Workflow Completed ---")

        # final_result 理论上是 format_agent 的最后一条消息
        if final_result and hasattr(final_result, 'content'):
            # 尝试解析 format_agent 的输出
            # 它应该包含 "locations" 和 "itinerary"
            # 它可能包含 "TERMINATE" 文本，需要去除
            content_str = final_result.content.replace("TERMINATE", "").strip()
            try:
                final_json = json.loads(content_str)
                if "locations" in final_json and "itinerary" in final_json:
                    print("--- Final Output Parsed Successfully ---")
                    return final_json
                else:
                    print("--- Error: Final output JSON missing required keys ('locations', 'itinerary') ---")
                    print(f"Raw content: {content_str}")
                    raise Exception("Agent workflow finished, but final output format is incorrect.")
            except json.JSONDecodeError as e:
                print(f"--- Error: Failed to decode final JSON output: {e} ---")
                print(f"Raw content: {content_str}")
                raise Exception("Agent workflow finished, but failed to parse final output.")
        else:
            print("--- Error: Agent workflow finished, but no final result message found. ---")
            raise Exception("Agent workflow did not produce a final result.")

    except HTTPException as he:
        # 透传 summarize_agent 抛出的 HTTP 异常 (例如无效地点)
        raise he
    except Exception as e:
        print(f"--- AutoGen Workflow Error: {e} ---")
        # 可以根据需要进行更细致的错误处理
        raise Exception(f"An error occurred during the itinerary generation: {e}")


# --- 主程序入口 (示例) ---
# 通常这个函数会由 app.py 调用
async def main_test():
    """本地测试运行函数"""
    test_input = {
        "mbti": "INFP",
        "Budget": 3000, # 预算设置为 3000 USD
        "Query": "Plan a 3-day movie-themed trip to Los Angeles for an INFP. I love classic Hollywood and studio tours. Please include some iconic restaurants. Avoid crowded nightlife spots and street food.",
        "CurrentItinerary": None
    }
    # 从 Query 中提取或由 summarize_agent 标准化出的字段:
    # "theme": "Movie",
    # "location": "Los Angeles",
    # "dates": 3,
    # "inclusion": ["classic Hollywood", "studio tours", "iconic restaurants"],
    # "exclusion": ["crowded nightlife spots", "street food"]

    try:
        result = await run_autogen_workflow(test_input)
        print("\n--- Generated Itinerary ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("--------------------------")
    except Exception as e:
        print(f"\n--- Workflow Failed ---")
        print(f"Error: {e}")
        print("-----------------------")

if __name__ == "__main__":
    # 如果直接运行此文件，执行测试
    # 注意：直接运行时，确保 .env 文件在正确的位置并已配置
    print("Running local test...")
    asyncio.run(main_test())