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
from fastapi import FastAPI
from pydantic import BaseModel
import motor.motor_asyncio

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

# 请求模型：前端一次性传入所有字段
class ItineraryRequest(BaseModel):
    budget: str
    dates: str
    field: str
    location: str
    mbti: str
    theme: str

@app.on_event("shutdown")
async def shutdown_db():
    """应用关闭时关闭 MongoDB 客户端。"""
    mongo_client.close()

@app.post("/plan")
async def plan(req: ItineraryRequest):
    """
    接收行程请求，调用 run_agents 生成完整行程，存入 MongoDB 并返回。
    """
    session_id = str(uuid.uuid4())
    payload = json.dumps(req.dict())

    # 执行多代理管道，获取最终行程 JSON 字符串
    result_str = await run_agents(payload)

    # 尝试解析 JSON
    try:
        itinerary = json.loads(result_str)
    except json.JSONDecodeError:
        itinerary = None

    # 存储会话记录
    record = {
        "session_id": session_id,
        "payload": req.dict(),
        "itinerary": itinerary,
        "updated_at": datetime.now(timezone.utc)
    }
    await conversations.insert_one(record)

    # 返回会话 ID 和行程 JSON
    return {"session_id": session_id, "itinerary": itinerary}

# 运行：
# uvicorn app:app --reload
