from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, List

from services.movie_tour_service import MovieTourService
from models.schemas import (
    MovieTourSuggestionRequest,
    MovieTourSuggestionResponse,
    MovieTourPlanRequest,
    MovieTourPlanResponse,
    PoiSuggestion # 确保导入了 PoiSuggestion 以供类型提示
)
from utils.error_handlers import (
    LlmProcessingError, 
    ExternalApiError, 
    NotFoundError, 
    BaseAppError
)
import logging

logger = logging.getLogger(__name__)

# 创建APIRouter
router = APIRouter(tags=["电影主题旅行规划"])

# 依赖函数：获取电影旅行服务实例
def get_movie_tour_service():
    return MovieTourService()

@router.post(
    "/suggestions", 
    response_model=MovieTourSuggestionResponse, 
    summary="获取电影主题POI建议",
    description="根据指定地点，获取与电影相关的兴趣点(POI)建议列表，包含坐标和关联电影信息。"
)
async def get_poi_suggestions(
    request: MovieTourSuggestionRequest,
    service: Annotated[MovieTourService, Depends(get_movie_tour_service)]
):
    """
    接收地点信息，返回经过验证的电影相关POI建议。
    """
    try:
        logger.info(f"收到POI建议请求，地点: {request.location}")
        # 调用服务层获取建议
        result = await service.get_movie_poi_suggestions(location=request.location)
        logger.info(f"成功为地点 '{request.location}' 获取 {len(result.get('suggestions', []))} 条POI建议。")
        return result
    except (LlmProcessingError, ExternalApiError, NotFoundError) as e:
        logger.error(f"获取POI建议时发生错误 (地点: {request.location}): {e}")
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except Exception as e:
        logger.exception(f"处理POI建议请求时发生意外错误 (地点: {request.location}): {e}")
        raise HTTPException(status_code=500, detail={
            "error": "internal_server_error",
            "message": "处理POI建议请求时发生内部错误",
            "details": str(e)
        })

@router.post(
    "/plan", 
    response_model=MovieTourPlanResponse, 
    summary="规划电影主题旅行行程",
    description="根据用户选择的POI列表和可选的MBTI类型，生成个性化的单日电影主题Solo旅行计划。"
)
async def plan_movie_tour(
    request: MovieTourPlanRequest,
    service: Annotated[MovieTourService, Depends(get_movie_tour_service)]
):
    """
    接收选择的POI列表和可选MBTI类型，返回详细的行程计划。
    """
    try:
        logger.info(f"收到行程规划请求，地点: {request.location}, POIs数量: {len(request.selected_pois)}, MBTI: {request.mbti_type}")
        # 注意：selected_pois 在请求模型中已经是 List[PoiSuggestion] 类型
        result = await service.plan_movie_tour(
            location=request.location,
            selected_pois=request.selected_pois, # 直接传递 Pydantic 模型列表
            mbti_type_str=request.mbti_type
        )
        logger.info(f"成功为地点 '{request.location}' 生成行程计划。")
        return result
    except (LlmProcessingError, ValueError) as e:
        status_code = 400 if isinstance(e, ValueError) else e.status_code
        error_dict = e.to_dict() if hasattr(e, 'to_dict') else {"error": "invalid_input", "message": str(e)}
        logger.error(f"规划行程时发生错误 (地点: {request.location}): {e}")
        raise HTTPException(status_code=status_code, detail=error_dict)
    except Exception as e:
        logger.exception(f"处理行程规划请求时发生意外错误 (地点: {request.location}): {e}")
        raise HTTPException(status_code=500, detail={
            "error": "internal_server_error",
            "message": "处理行程规划请求时发生内部错误",
            "details": str(e)
        }) 