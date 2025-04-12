from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ 添加这行
from models import TripRequest
from gpt_generator import generate_itinerary

app = FastAPI()

# ✅ 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有前端来源；上线时请限定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/plan_trip")
async def plan_trip(request: TripRequest):
    prompt = request.to_prompt()
    plan = generate_itinerary(prompt)
    return {"itinerary": plan}
