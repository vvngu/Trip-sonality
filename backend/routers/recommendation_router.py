from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from services.recommendation_service import RecommendationService
from models.schemas import RecommendationRequest, RecommendationResponse
from utils.error_handlers import ValidationError, NotFoundError, ExternalApiError, LlmProcessingError
from utils.helpers import validate_mbti_type
from constants.enums import MbtiType

# 创建APIRouter
router = APIRouter(tags=["推荐"])

# 依赖函数：获取推荐服务实例
def get_recommendation_service():
    return RecommendationService()

@router.post('/recommendations', response_model=RecommendationResponse, summary="获取旅行推荐")
async def get_recommendations(
    request: RecommendationRequest,
    service: Annotated[RecommendationService, Depends(get_recommendation_service)]
):
    """
    获取基于MBTI类型和电影的旅行推荐
    
    **请求体**:
    - **mbti_type**: MBTI人格类型，例如"INTJ"
    - **movie_input**: 电影名称或主题关键词
    
    **返回**:
    - **recommendation**: 详细的旅行推荐
    - **movie_info**: 电影基本信息
    - **mbti_type**: MBTI人格类型
    """
    try:
        # 验证MBTI类型
        mbti_type = validate_mbti_type(request.mbti_type)
        
        # 生成推荐
        response_data = service.generate_solo_movie_recommendations(
            mbti_type=mbti_type,
            movie_input=request.movie_input
        )
        
        return response_data
        
    except ValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except ExternalApiError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except LlmProcessingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except Exception as e:
        # 处理未预期的异常
        error_response = {
            "error": "internal_server_error",
            "message": "服务器内部错误",
            "details": str(e)
        }
        raise HTTPException(status_code=500, detail=error_response) 