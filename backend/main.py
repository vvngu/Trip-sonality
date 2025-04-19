from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from utils.error_handlers import register_exception_handlers  # ✅ 引入注册函数

# 创建 FastAPI 应用
app = FastAPI(
    title="Trip-sonality API",
    description="提供基于MBTI类型和电影的个性化Solo旅行推荐",
    version="1.0.0"
)

# 注册异常处理器 ✅
register_exception_handlers(app)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
from routers.recommendation_router import router as recommendation_router
from routers.movie_tour_router import router as movie_tour_router
app.include_router(recommendation_router, prefix="/api/v1")
app.include_router(movie_tour_router, prefix="/api/v1")

# 根目录与健康检查
@app.get("/")
async def index():
    return {
        "name": "Trip-sonality Backend API",
        "version": "1.0.0",
        "description": "提供基于MBTI类型和电影的个性化Solo旅行推荐",
        "endpoints": {
            "original_recommendations": "/api/v1/recommendations",
            "movie_tour_suggestions": "/api/v1/suggestions",
            "movie_tour_plan": "/api/v1/plan",
            "health": "/api/v1/health"
        }
    }

@app.get("/api/v1/health", tags=["健康检查"])
async def health_check():
    return {"status": "healthy", "message": "服务正常运行"}

# 本地启动（开发用）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
