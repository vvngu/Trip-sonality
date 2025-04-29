# backend/app.py
"""
主后端入口：接收一次请求，调用 autogen_itinerary.run_agents 生成完整行程，并存储最终结果。

数据库：
  - 名称：由 MONGODB_DB 环境变量指定（默认为 "trip_agent"）
  - 集合："conversations"，存储 session_id、请求载荷、最终行程 JSON 和更新时间戳。
"""
import os
import json
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import motor.motor_asyncio
from typing import Optional, Dict

# 导入多代理执行函数
from autogen_itinerary import run_agents

# 加载环境变量
load_dotenv()

# MongoDB 配置
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "trip_agent")
if not MONGODB_URI:
    raise RuntimeError("请在 .env 文件中设置 MONGODB_URI 环境变量。")

# 初始化 FastAPI 和 MongoDB 客户端
app = FastAPI()
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = mongo_client[MONGODB_DB]
conversations = db.get_collection("conversations")
itineraries = db.get_collection("itineraries")

# 创建索引
async def create_indexes():
    await itineraries.create_index("location")
    await itineraries.create_index("mbti")
    await itineraries.create_index("created_at")

@app.on_event("startup")
async def startup_event():
    await create_indexes()

@app.on_event("shutdown")
async def shutdown_db():
    """应用关闭时关闭 MongoDB 客户端。"""
    mongo_client.close()

@app.post("/plan")
async def plan_itinerary(request: ItineraryRequest):
    try:
        # Generate itinerary using the existing agents
        result = await run_agents(request.dict())
        
        # Store the itinerary in MongoDB
        itinerary_doc = {
            "mbti": request.mbti,
            "budget": request.budget,
            "query": request.query,
            "location": request.location,
            "dates": request.dates,
            "current_itinerary": request.current_itinerary,
            "generated_itinerary": result,
            "created_at": datetime.now(timezone.utc)
        }
        await itineraries.insert_one(itinerary_doc)
        
        return {"itinerary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 运行：
# uvicorn app:app --reload
