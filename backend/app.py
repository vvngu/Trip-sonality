# backend/app.py
"""
主后端入口：接收用户请求，调用重构后的 AutoGen Agent 工作流生成行程，并将结果存储到 MongoDB。

数据库：
  - 名称：由 MONGODB_DB 环境变量指定（默认为 "trip_agent"）
  - 集合："conversations"，存储 session_id、用户输入、最终行程 JSON 和时间戳。
"""
import os
import json
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException as FastAPIHTTPException # 别名以区分
from pydantic import BaseModel, Field # Field 用于添加默认值等
from typing import Optional, Any, List, Dict # Optional 用于可选字段
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware

# 导入重构后的 Agent 工作流执行函数
from autogen_itinerary import run_autogen_workflow

# 加载环境变量
load_dotenv()

# MongoDB 配置
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "trip_agent")
if not MONGODB_URI:
    raise RuntimeError("请在 .env 文件中设置 MONGODB_URI 环境变量。")

# 初始化 FastAPI 和 MongoDB 客户端
app = FastAPI(
    title="Trip-sonality API",
    description="API for generating personalized travel itineraries using an AutoGen multi-agent system.",
    version="1.0.0"
)

# 配置 CORS 中间件，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端应用的URL
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有headers
)

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = mongo_client[MONGODB_DB]
conversations = db.get_collection("conversations")
itineraries = db.get_collection("itineraries")

# --- API 请求和响应模型 ---

# 定义用户输入的 Pydantic 模型 (对应流程图中的 query 表单)
class UserInput(BaseModel):
    mbti: str = Field(..., description="用户的 MBTI 类型 (16 种之一)")
    budget: Optional[int] = Field(None, description="用户的预算 (可选, 美元)")
    query: str = Field(..., description="用户的自然语言查询，包含目的地、天数、偏好等信息")
    current_itinerary: Optional[Dict[str, Any]] = Field(None, description="用户可能提供的现有行程 (可选, JSON 对象)")

    # 可以在这里添加验证逻辑，例如检查 mbti 是否有效
    # @validator('mbti')
    # def check_mbti(cls, v):
    #     if v.upper() not in ['ISTJ', 'ISFJ', ...]: # 列出所有 16 种
    #         raise ValueError('Invalid MBTI type')
    #     return v.upper()

# 定义 API 响应模型
class ItineraryResponse(BaseModel):
    session_id: str
    locations: List[Dict[str, Any]] = Field(..., description="包含地点信息的列表，用于地图标记")
    itinerary: List[Dict[str, Any]] = Field(..., description="按天组织的详细行程安排")

# --- API 事件处理 --- 

@app.on_event("startup")
async def startup_db_client():
    """应用启动时连接 MongoDB。"""
    # 客户端已在全局初始化，这里可以添加连接测试或索引创建逻辑
    try:
        await mongo_client.admin.command('ping')
        print("Successfully connected to MongoDB.")
        # 可以在这里确保索引存在
        await conversations.create_index("session_id", unique=True)
        await conversations.create_index("updated_at")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """应用关闭时关闭 MongoDB 客户端。"""
    print("Closing MongoDB connection...")
    mongo_client.close()

# --- API 端点 ---

@app.post("/plan", response_model=ItineraryResponse, tags=["Itinerary Planning"])
async def generate_plan(user_input: UserInput):
    """
    接收用户的行程规划请求 (包含 MBTI, 预算, 查询文本等)，
    调用 `run_autogen_workflow` 来执行 Agent 工作流，生成行程，
    将结果存入 MongoDB 并返回给前端。
    """
    session_id = str(uuid.uuid4())
    print(f"Received new plan request. Session ID: {session_id}")
    print(f"User Input: {user_input.dict()}")

    # 准备传递给 Agent 工作流的输入字典
    # 注意键名需要与 autogen_itinerary.py 中 Agent 的期望匹配
    workflow_input = {
        "mbti": user_input.mbti,
        "Budget": user_input.budget, # 使用 'Budget' 而不是 'budget' ? 确认 Agent 期望
        "Query": user_input.query,
        "CurrentItinerary": user_input.current_itinerary
    }
    # 移除值为 None 的键，避免传递 null
    workflow_input = {k: v for k, v in workflow_input.items() if v is not None}

    try:
        # 执行 Agent 工作流
        print("--- Calling AutoGen Workflow --- ")
        result_data = await run_autogen_workflow(workflow_input)
        print("--- AutoGen Workflow Finished Successfully --- ")

        # run_autogen_workflow 成功时直接返回包含 locations 和 itinerary 的字典
        locations = result_data.get("locations", [])
        itinerary = result_data.get("itinerary", [])

        # 基本验证，确保返回的是列表
        if not isinstance(locations, list):
            print(f"Warning: 'locations' field is not a list. Received: {type(locations)}")
            locations = []
        if not isinstance(itinerary, list):
            print(f"Warning: 'itinerary' field is not a list. Received: {type(itinerary)}")
            itinerary = []

    except FastAPIHTTPException as http_exc:
        # 捕获并重新抛出由 Agent (如 summarize_agent) 或工作流本身抛出的 HTTP 异常
        print(f"HTTP Exception during workflow: {http_exc.status_code} - {http_exc.detail}")
        raise http_exc # FastAPI 会处理这个异常并返回给客户端
    except Exception as e:
        # 捕获其他所有在 Agent 工作流中发生的异常
        print(f"Error during AutoGen workflow execution: {e}")
        # 向客户端返回一个通用的服务器错误
        raise FastAPIHTTPException(
            status_code=500,
            detail=f"An internal error occurred during itinerary generation: {e}"
        )

    # -- 将结果存储到 MongoDB --
    record = {
        "session_id": session_id,
        "user_input": user_input.dict(), # 存储原始用户输入
        "locations": locations,
        "itinerary": itinerary,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    try:
        insert_result = await conversations.insert_one(record)
        print(f"Successfully inserted record into MongoDB with ID: {insert_result.inserted_id}")
    except Exception as e:
        # 即使存储失败，也应该返回结果给用户，但记录错误
        print(f"Error saving record to MongoDB: {e}")

    # -- 返回响应给前端 --
    response_data = {
        "session_id": session_id,
        "locations": locations,
        "itinerary": itinerary
    }
    # Pydantic 会自动验证 response_data 是否符合 ItineraryResponse 模型
    return response_data

@app.get("/health", tags=["Health Check"])
async def health_check():
    """简单的健康检查端点。"""
    return {"status": "ok"}

# --- 本地运行 (可选) ---
# 如果你想直接运行这个 FastAPI 应用 (例如用于测试):
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server locally on http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
    # 访问 http://localhost:8000/docs 可以看到 Swagger UI