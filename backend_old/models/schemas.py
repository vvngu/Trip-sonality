from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator
from constants.enums import MbtiType

# 请求模型
class RecommendationRequest(BaseModel):
    """旅行推荐请求模型"""
    mbti_type: str = Field(..., description="MBTI人格类型，例如'INTJ'")
    movie_input: str = Field(..., description="电影名称或主题关键词")
    
    @field_validator('mbti_type')
    @classmethod
    def validate_mbti_type(cls, v):
        """验证MBTI类型"""
        try:
            return MbtiType(v.upper()).value
        except ValueError:
            raise ValueError(f"无效的MBTI类型: '{v}'。有效类型包括: {', '.join(MbtiType.list())}")

    class Config:
        json_schema_extra = {
            "example": {
                "mbti_type": "INTJ",
                "movie_input": "盗梦空间"
            }
        }


# 点of interest模型
class PlaceOfInterest(BaseModel):
    """兴趣点(POI)模型"""
    name: str = Field(..., description="地点名称")
    description: Optional[str] = Field(None, description="地点描述")
    category: Optional[str] = Field(None, description="地点类别")
    address: Optional[str] = Field(None, description="地点地址")
    city: Optional[str] = Field(None, description="所在城市")
    country: Optional[str] = Field(None, description="所在国家")
    coordinates: Optional[Dict[str, float]] = Field(None, description="经纬度坐标")
    relation_to_movie: Optional[str] = Field(None, description="与电影的关联")
    image_url: Optional[str] = Field(None, description="地点图片URL")


# 活动建议模型
class ActivitySuggestion(BaseModel):
    """活动建议模型"""
    title: str = Field(..., description="活动标题")
    description: str = Field(..., description="活动描述")
    relation_to_movie: Optional[str] = Field(None, description="与电影的关联")
    relation_to_mbti: Optional[str] = Field(None, description="与MBTI类型的关联")
    time_of_day: Optional[str] = Field(None, description="建议的时间段")


# 旅行推荐结果模型
class TravelRecommendation(BaseModel):
    """旅行推荐结果模型"""
    title: str = Field(..., description="推荐标题")
    movie_title: str = Field(..., description="相关电影标题")
    movie_overview: Optional[str] = Field(None, description="电影简介")
    theme: str = Field(..., description="旅行主题")
    destination: str = Field(..., description="目的地")
    description: str = Field(..., description="推荐描述")
    places_of_interest: List[PlaceOfInterest] = Field([], description="推荐景点列表")
    activities: List[ActivitySuggestion] = Field([], description="推荐活动列表")
    mbti_relevance: str = Field(..., description="与MBTI类型的相关性说明")


# 响应模型
class RecommendationResponse(BaseModel):
    """旅行推荐响应模型"""
    recommendation: TravelRecommendation = Field(..., description="旅行推荐结果")
    movie_info: Dict[str, Any] = Field(..., description="电影信息")
    mbti_type: str = Field(..., description="MBTI人格类型")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendation": {
                    "title": "梦境迷宫：INTJ的巴黎建筑探索",
                    "movie_title": "盗梦空间",
                    "movie_overview": "一个高端盗贼能够通过使用特殊技术，进入他人的梦境中盗取秘密。",
                    "theme": "梦境与现实交织的建筑探索",
                    "destination": "巴黎, 法国",
                    "description": "一场为INTJ设计的深度探索之旅，融合《盗梦空间》中的建筑美学与现实世界的巴黎地标。",
                    "places_of_interest": [
                        {
                            "name": "埃菲尔铁塔",
                            "description": "电影中梦境折叠场景的灵感来源",
                            "relation_to_movie": "在电影中，城市景观的折叠与变形展示了梦境的不稳定性",
                            "category": "地标建筑"
                        }
                    ],
                    "activities": [
                        {
                            "title": "建筑摄影探索",
                            "description": "带着专业相机探索巴黎独特的建筑风格",
                            "relation_to_movie": "电影中建筑师创造的不可能空间",
                            "relation_to_mbti": "满足INTJ对细节的关注和审美追求",
                            "time_of_day": "清晨"
                        }
                    ],
                    "mbti_relevance": "此行程专为INTJ设计，强调独立探索、逻辑思考和深度体验。"
                },
                "movie_info": {
                    "id": 27205,
                    "title": "盗梦空间",
                    "overview": "一个高端盗贼能够通过使用特殊技术，进入他人的梦境中盗取秘密。",
                    "release_date": "2010-07-16",
                    "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
                    "backdrop_path": "/s3TBrRGB1iav7gFOCNx3H31MoES.jpg"
                },
                "mbti_type": "INTJ"
            }
        }

# 新增：电影主题旅行规划相关模型

# 电影POI建议请求模型
class MovieTourSuggestionRequest(BaseModel):
    """电影主题旅行POI建议请求模型"""
    location: str = Field(..., description="用户指定的地点/城市")
    mbti_type: Optional[str] = Field(None, description="可选的MBTI类型")
    
    @field_validator('mbti_type')
    @classmethod
    def validate_mbti_type(cls, v):
        """验证MBTI类型（如果提供）"""
        if v is None:
            return v
        try:
            return MbtiType(v.upper()).value
        except ValueError:
            raise ValueError(f"无效的MBTI类型: '{v}'。有效类型包括: {', '.join(MbtiType.list())}")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": "巴黎",
                "mbti_type": "INTJ"
            }
        }

# POI建议项模型
class PoiSuggestion(BaseModel):
    """POI建议项模型"""
    poi_id: str = Field(..., description="POI的唯一标识符 (例如 Geoapify ID)")
    name: str = Field(..., description="POI名称")
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")
    address: Optional[str] = Field(None, description="地址")
    category: Optional[str] = Field(None, description="类别")
    associated_movies: List[str] = Field(..., description="与此POI关联的电影列表")
    description: Optional[str] = Field(None, description="POI或其与电影关联的简要描述")
    
    class Config:
        json_schema_extra = {
            "example": {
                "poi_id": "51a8e5853e3e490000aac869",
                "name": "埃菲尔铁塔",
                "latitude": 48.8584,
                "longitude": 2.2945,
                "address": "巴黎香榭丽舍大街",
                "category": "地标建筑",
                "associated_movies": ["盗梦空间", "午夜巴黎", "法国贵族"],
                "description": "这座标志性建筑在《盗梦空间》中成为了梦境折叠的视觉灵感来源。"
            }
        }

# POI建议响应模型
class MovieTourSuggestionResponse(BaseModel):
    """电影主题旅行POI建议响应模型"""
    suggestions: List[PoiSuggestion] = Field(..., description="POI建议列表")
    location: str = Field(..., description="查询的地点")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": "巴黎",
                "suggestions": [
                    {
                        "poi_id": "51a8e5853e3e490000aac869",
                        "name": "埃菲尔铁塔",
                        "latitude": 48.8584,
                        "longitude": 2.2945,
                        "address": "巴黎香榭丽舍大街",
                        "category": "地标建筑",
                        "associated_movies": ["盗梦空间", "午夜巴黎", "法国贵族"],
                        "description": "这座标志性建筑在《盗梦空间》中成为了梦境折叠的视觉灵感来源。"
                    }
                ]
            }
        }

# 电影主题旅行计划请求模型
class MovieTourPlanRequest(BaseModel):
    """电影主题旅行计划请求模型"""
    location: str = Field(..., description="用户指定的地点/城市")
    selected_pois: List[PoiSuggestion] = Field(..., description="用户从建议中选择的POI列表")
    mbti_type: Optional[str] = Field(None, description="可选的MBTI类型")
    
    @field_validator('mbti_type')
    @classmethod
    def validate_mbti_type(cls, v):
        """验证MBTI类型（如果提供）"""
        if v is None:
            return v
        try:
            return MbtiType(v.upper()).value
        except ValueError:
            raise ValueError(f"无效的MBTI类型: '{v}'。有效类型包括: {', '.join(MbtiType.list())}")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": "巴黎",
                "mbti_type": "INTJ",
                "selected_pois": [
                    {
                        "poi_id": "51a8e5853e3e490000aac869",
                        "name": "埃菲尔铁塔",
                        "latitude": 48.8584,
                        "longitude": 2.2945,
                        "address": "巴黎香榭丽舍大街",
                        "category": "地标建筑",
                        "associated_movies": ["盗梦空间", "午夜巴黎"],
                        "description": "这座标志性建筑在《盗梦空间》中成为了梦境折叠的视觉灵感来源。"
                    }
                ]
            }
        }

# 行程项模型
class ItineraryItem(BaseModel):
    """行程项模型"""
    type: str = Field(..., description="项目类型：'poi'(景点)、'meal'(餐饮)、'activity'(活动)或'travel'(交通)")
    name: str = Field(..., description="项目名称")
    description: str = Field(..., description="详细描述，包含MBTI/Solo/电影元素")
    start_time: Optional[str] = Field(None, description="开始时间")
    duration_minutes: Optional[int] = Field(None, description="持续时间（分钟）")
    poi_details: Optional[PoiSuggestion] = Field(None, description="如果type是'poi'，包含完整POI详情")
    location_details: Optional[Dict[str, Any]] = Field(None, description="位置详情，适用于餐厅/咖啡馆等")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "poi",
                "name": "埃菲尔铁塔探索",
                "description": "独自探索这座《盗梦空间》中梦境折叠的灵感来源，适合INTJ的独立思考者。",
                "start_time": "10:00",
                "duration_minutes": 120,
                "poi_details": {
                    "poi_id": "51a8e5853e3e490000aac869",
                    "name": "埃菲尔铁塔",
                    "latitude": 48.8584,
                    "longitude": 2.2945,
                    "address": "巴黎香榭丽舍大街",
                    "category": "地标建筑",
                    "associated_movies": ["盗梦空间", "午夜巴黎"],
                    "description": "这座标志性建筑在《盗梦空间》中成为了梦境折叠的视觉灵感来源。"
                }
            }
        }

# 行程日模型（可选，用于多日行程规划）
class ItineraryDay(BaseModel):
    """行程日模型"""
    day_number: int = Field(..., description="第几天")
    theme: Optional[str] = Field(None, description="当天主题")
    items: List[ItineraryItem] = Field(..., description="当天行程项目")
    
    class Config:
        json_schema_extra = {
            "example": {
                "day_number": 1,
                "theme": "梦境与建筑的交融",
                "items": [
                    {
                        "type": "poi",
                        "name": "埃菲尔铁塔探索",
                        "description": "独自探索这座《盗梦空间》中梦境折叠的灵感来源，适合INTJ的独立思考者。",
                        "start_time": "10:00",
                        "duration_minutes": 120
                    }
                ]
            }
        }

# 电影主题旅行计划响应模型
class MovieTourPlanResponse(BaseModel):
    """电影主题旅行计划响应模型"""
    title: str = Field(..., description="行程标题")
    location: str = Field(..., description="地点")
    overview: str = Field(..., description="行程总体介绍，结合MBTI/Solo/电影主题")
    days: List[ItineraryDay] = Field(..., description="行程天数列表")  # 使用多日行程结构
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "INTJ的巴黎电影奇遇：《盗梦空间》独行者体验",
                "location": "巴黎",
                "overview": "这是一个为独立思考的INTJ设计的巴黎电影主题之旅，将带您探索《盗梦空间》的取景地与灵感来源。行程强调独立探索、深度思考和个人体验，避开过度社交场所。",
                "days": [
                    {
                        "day_number": 1,
                        "theme": "梦境与建筑的交融",
                        "items": [
                            {
                                "type": "poi",
                                "name": "埃菲尔铁塔探索",
                                "description": "独自探索这座《盗梦空间》中梦境折叠的灵感来源，适合INTJ的独立思考者。",
                                "start_time": "10:00",
                                "duration_minutes": 120
                            }
                        ]
                    }
                ]
            }
        } 