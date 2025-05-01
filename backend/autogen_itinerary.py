# backend/autogen_itinerary.py

import asyncio
from http.client import HTTPException
import json
import os
from typing import List, Dict, Any

# from backend.config import client
# from backend.utils import clean_json_content

# from backend.agents.summarize_agent import summarize_agent
# from backend.agents.search_agent import search_agent
# from backend.agents.web_content_agent import web_content_agent
# from backend.agents.poi_activity_agent import poi_activity_agent
# from backend.agents.plan_agent import plan_agent
# from backend.agents.critic_agent import critic_agent
# from backend.agents.format_agent import format_agent
from config import client
from utils import clean_json_content
from agents.summarize_agent import summarize_agent
from agents.search_agent import search_agent
from agents.web_content_agent import web_content_agent
from agents.poi_activity_agent import poi_activity_agent
from agents.plan_agent import plan_agent
from agents.critic_agent import critic_agent
from agents.format_agent import format_agent

from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination



# # Setup the client to use either Azure OpenAI or GitHub Models
# load_dotenv(override=True)
# API_HOST = os.getenv("API_HOST", "github")


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


# Agent 7: format_agent - 整理最终输出
# format_agent = AssistantAgent(
#     name="format_agent",
#     model_client=client,
#     description=(
#         "第七步（最后一步）：接收 critic_agent 优化后的最终行程计划。"
#         "还需要访问 poi_agent 输出的 POI 列表以提取位置信息。"
#         "生成前端所需的两种 JSON 结构：`locations` (包含 ID, name, position) 和 `itinerary`。"
#         "确保所有字段都正确填充，格式符合要求。"
#         "输出包含这两个结构的最终 JSON 对象，并以 TERMINATE 结束。"
#     ),
#     system_message="""你是最终格式化代理。
#     你的任务是接收 `critic_agent` 输出的最终行程计划 JSON `{"itinerary": [...]}`。你还需要访问 `poi_agent` 输出的原始 POI 列表 `{"items": [...]}` (包含经纬度 lat, lng)。
#     1. **创建 `locations` 列表**:
#        - 遍历 `poi_agent` 输出的 `items` 列表。
#        - 对于每个 item，提取 `name`, `lat`, `lng`。
#        - 创建一个 `locations` 数组，每个元素格式如下：
#          `{ "id": <index>, "name": "<POI Name>", "position": { "lat": <latitude>, "lng": <longitude> } }`
#        - 确保每个在最终 `itinerary` 中出现的地点都在 `locations` 列表中，并且 ID 唯一。

#     2. **整理 `itinerary` 列表**:
#        - 使用 `critic_agent` 输出的 `itinerary` 数组。确保其结构和内容符合最终要求。

#     3. **组合最终输出**:
#        - 创建一个包含 `locations` 和 `itinerary` 两个键的 JSON 对象。
#        - 格式如下：
#          ```json
#          {
#            "locations": [
#              { "id": 0, "name": "...", "position": { "lat": ..., "lng": ... } },
#              ...
#            ],
#            "itinerary": [
#              { "day": 1, "food": [...], "activities": [...], "summary": "..." },
#              ...
#            ]
#          }
#          ```
#     4. 确保整个输出是有效的 JSON。
#     5. 在输出最终的 JSON 对象后，必须紧接着响应 `TERMINATE`。
#     """
#     # 注意: format_agent 需要同时访问 critic_agent 的输出和 poi_agent 的输出。
#     # 这需要在 MagenticOneGroupChat 的消息传递或状态管理中处理。
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

    
    agents=[
        summarize_agent,
        # search_agent,
        # web_content_agent,
        # poi_activity_agent,
        # plan_agent,
        # critic_agent,
        format_agent
    ]

    # 设置终止条件：当 format_agent 输出包含 "TERMINATE" 时结束
    termination = TextMentionTermination(text="TERMINATE")


    # 创建 MagenticOneGroupChat 实例
    # 它会按顺序执行 Agent，并将前一个 Agent 的输出作为下一个 Agent 的输入
    group_chat = MagenticOneGroupChat(
        agents,
        termination_condition=termination,
        model_client=client, # 可以为 group chat 本身指定一个 client，用于管理流程
    )

    initial_task = json.dumps(initial_user_input)

    print(f"--- Initiating Group Chat with Task: {initial_task[:200]}... ---") # 打印部分任务内容

    try:
        # 运行 Agent 流程
        # 使用 run() 而不是 run_stream() 来获取最终结果
        final_result = await group_chat.run(task=initial_task)

        messages = final_result.messages
        final_output = None

        for msg in reversed(messages):
            if msg.source == "format_agent":
                print(msg.content)
                try:
                    # 尝试解析消息内容为 JSON
                    cleaned_str = clean_json_content(msg.content)
                    print(cleaned_str)
                    final_output = json.loads(cleaned_str)
                    print("提取的格式化输出：")
                    print(json.dumps(final_output, indent=2, ensure_ascii=False))
                    break
                except json.JSONDecodeError:
                    print("无法解析 format_agent 的内容为 JSON。")
                    break
        else:
            print("未找到来自 format_agent 的消息。")

        print("--- AutoGen Workflow Completed ---")
        # print(f"Final Result: {final_result}")
        print(type(final_output))
        return final_output
        
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
        "Budget": 1000, # 预算设置为 3000 USD
        "Query": "Plan a 1-day movie-themed trip to Los Angeles for an INFP. I love classic Hollywood and studio tours. Please include some iconic restaurants. Avoid crowded nightlife spots and street food.",
        "CurrentItinerary": None
    }
    try:
        result = await run_autogen_workflow(test_input)
    except Exception as e:
        print(f"\n--- Workflow Failed ---")
if __name__ == "__main__":
    # 如果直接运行此文件，执行测试
    # 注意：直接运行时，确保 .env 文件在正确的位置并已配置
    print("Running local test...")
    asyncio.run(main_test())