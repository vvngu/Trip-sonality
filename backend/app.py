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
from fastapi.middleware.cors import CORSMiddleware

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
    接收行程请求，调用run_agents生成行程和位置数据，存入MongoDB并返回。
    """
    import re
    
    session_id = str(uuid.uuid4())
    payload = json.dumps(req.dict())

    try:
        # 执行多代理管道
        task_result = await run_agents(payload)
        
        # 从TaskResult对象提取文本内容
        if hasattr(task_result, 'result'):
            result_text = task_result.result
        elif hasattr(task_result, 'content'):
            result_text = task_result.content 
        elif hasattr(task_result, 'message'):
            result_text = task_result.message
        else:
            result_text = str(task_result)
            
        print(f"获取到原始结果: {result_text[:200]}...")
        
        # 尝试直接解析整个JSON对象
        try:
            # 使用正则表达式找到完整的JSON对象
            json_pattern = r'\{\s*"locations"\s*:.*"itinerary"\s*:.*\}'
            json_match = re.search(json_pattern, result_text, re.DOTALL)
            
            if json_match:
                complete_json = json_match.group(0)
                print(f"找到完整的JSON对象: {complete_json[:100]}...")
                parsed_data = json.loads(complete_json)
                
                # 提取locations和itinerary
                locations = parsed_data.get("locations", [])
                itinerary = parsed_data.get("itinerary", [])
                
                # 确保两者都是列表
                if not isinstance(locations, list):
                    locations = []
                if not isinstance(itinerary, list):
                    itinerary = []
            else:
                # 找不到完整JSON，尝试分别提取locations和itinerary
                # 先查找locations的JSON数组
                locations_pattern = r'"locations"\s*:\s*(\[.*?\])'
                locations_match = re.search(locations_pattern, result_text, re.DOTALL)
                
                # 再查找itinerary的JSON数组
                itinerary_pattern = r'"itinerary"\s*:\s*(\[.*?\])'
                itinerary_match = re.search(itinerary_pattern, result_text, re.DOTALL)
                
                # 提取并解析locations
                if locations_match:
                    locations_json = locations_match.group(1)
                    try:
                        locations = json.loads(locations_json)
                    except json.JSONDecodeError:
                        print("无法解析locations JSON")
                        locations = []
                else:
                    locations = []
                
                # 提取并解析itinerary  
                if itinerary_match:
                    itinerary_json = itinerary_match.group(1)
                    try:
                        itinerary = json.loads(itinerary_json)
                    except json.JSONDecodeError:
                        print("无法解析itinerary JSON")
                        itinerary = []
                else:
                    itinerary = []
                
                print(f"分开提取: 找到{len(locations)}个位置和{len(itinerary)}天行程")
        
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            # 如果解析失败，设置空值
            locations = []
            itinerary = []
            
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        locations = []
        itinerary = []

    # 存储会话记录
    record = {
        "session_id": session_id,
        "payload": req.dict(),
        "locations": locations,
        "itinerary": itinerary,
        "updated_at": datetime.now(timezone.utc)
    }
    await conversations.insert_one(record)

    # 返回会话ID、位置和行程JSON
    return {
        "session_id": session_id, 
        "locations": locations,
        "itinerary": itinerary
    }

# 运行：
# uvicorn app:app --reload