# backend/app.py
"""
Main backend entry point: Receives user requests, calls the refactored AutoGen Agent workflow 
to generate itineraries, and stores results in MongoDB.

Database:
  - Name: Specified by MONGODB_DB environment variable (default: "trip_agent")
  - Collection: "conversations", stores session_id, user input, final itinerary JSON and timestamps.

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
# Import the refactored Agent workflow execution function
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
# Configure CORS middleware to allow frontend access
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

# --- API 请求和响应模型 ---

# 定义用户输入的 Pydantic 模型 (对应流程图中的 query 表单)
# Define user input Pydantic model (corresponds to query form in flowchart)
# "User's MBTI type (one of 16 types)"
# "User's budget (optional, USD)"
# "User's natural language query, including destination, days, preferences etc."
# "User's possible existing itinerary (optional, JSON object)"
class UserInput(BaseModel):
    mbti: str = Field(..., description="用户的 MBTI 类型 (16 种之一)")
    budget: Optional[int] = Field(None, description="用户的预算 (可选, 美元)")
    query: str = Field(..., description="用户的自然语言查询，包含目的地、天数、偏好等信息")
    current_itinerary: Optional[Dict[str, Any]] = Field(None, description="用户可能提供的现有行程 (可选, JSON 对象)")

# 定义 API 响应模型 - 简化为只包含session_id和原始JSON数据
# Define API response model - simplified to only include session_id and raw JSON data
class ItineraryResponse(BaseModel):
    session_id: str
    data: Any = Field(..., description="原始行程JSON数据")

# --- API 事件处理 --- 
# Application startup - connect to MongoDB
@app.on_event("startup")
async def startup_db_client():
    """应用启动时连接 MongoDB。"""
    try:
        await mongo_client.admin.command('ping')
        print("Successfully connected to MongoDB.")
        await conversations.create_index("session_id", unique=True)
        await conversations.create_index("updated_at")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """应用关闭时关闭 MongoDB 客户端。"""
    # Application shutdown - close MongoDB client
    print("Closing MongoDB connection...")
    mongo_client.close()

# --- API 端点 ---

@app.post("/plan", response_model=ItineraryResponse, tags=["Itinerary Planning"])
async def generate_plan(user_input: UserInput):
    """
    接收用户的行程规划请求，调用Agent工作流生成行程，
    将原始JSON结果存入MongoDB并直接返回给前端。
    # Receive user's itinerary planning request, call Agent workflow to generate itinerary,
    # Store raw JSON result in MongoDB and return directly to frontend
    """
    session_id = str(uuid.uuid4())
    print(f"Received new plan request. Session ID: {session_id}")
    print(f"User Input: {user_input.dict()}")
   
    # Prepare input dictionary to pass to Agent workflow   
    # 准备传递给 Agent 工作流的输入字典
    workflow_input = {
        "mbti": user_input.mbti,
        "Budget": user_input.budget,
        "Query": user_input.query,
        "CurrentItinerary": user_input.current_itinerary
    }
    # Remove keys with None values to avoid passing null  
    # 移除值为 None 的键，避免传递 null
    workflow_input = {k: v for k, v in workflow_input.items() if v is not None}

    try:
        # Execute Agent workflow
        # 执行 Agent 工作流
        print("--- Calling AutoGen Workflow --- ")
        result_data = await run_autogen_workflow(workflow_input)
        print("--- AutoGen Workflow Finished Successfully --- ")
        # Don't separate data anymore, use raw result directly
        # 不再分离数据，直接使用原始结果
        raw_data = result_data

    except FastAPIHTTPException as http_exc:
        print(f"HTTP Exception during workflow: {http_exc.status_code} - {http_exc.detail}")
        raise http_exc
    except Exception as e:
        print(f"Error during AutoGen workflow execution: {e}")
        raise FastAPIHTTPException(
            status_code=500,
            detail=f"An internal error occurred during itinerary generation: {e}"
        )

    # -- 将结果存储到 MongoDB --
    # Store result in MongoDB
    record = {
        "session_id": session_id,
        "user_input": user_input.dict(),
        "data": raw_data,  # 存储原始JSON数据
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    try:
        insert_result = await conversations.insert_one(record)
        print(f"Successfully inserted record into MongoDB with ID: {insert_result.inserted_id}")
    except Exception as e:
        print(f"Error saving record to MongoDB: {e}")

    # -- 返回响应给前端 --
    # Return response to frontend
    response_data = {
        "session_id": session_id,
        "data": raw_data  # 直接返回原始JSON数据
    }
    return response_data

@app.get("/health", tags=["Health Check"])
async def health_check():
    """简单的健康检查端点。"""
    # Simple health check endpoint
    return {"status": "ok"}

# --- 本地运行 (可选) ---
# Local run (optional)
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server locally on http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)