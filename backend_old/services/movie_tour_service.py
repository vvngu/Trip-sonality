import json
from typing import List, Dict, Optional, Any
from constants.enums import MbtiType
from utils.helpers import map_mbti_to_preferences, mbti_type_to_enum
from clients.llm_client import LLMClient
from clients.geoapify_client import GeoapifyClient
from llm.prompt_manager import PromptManager
from utils.error_handlers import LlmProcessingError, ExternalApiError, NotFoundError
from models.schemas import PoiSuggestion # 引入 POI 模型
import logging

logger = logging.getLogger(__name__)

class MovieTourService:
    """电影主题旅行服务，负责生成POI建议和行程计划"""

    def __init__(self):
        self.llm_client = LLMClient()
        self.geoapify_client = GeoapifyClient()
        self.prompt_manager = PromptManager()

    async def get_movie_poi_suggestions(self, location: str) -> Dict[str, Any]:
        """
        获取地点的电影相关POI建议
        
        Args:
            location: 用户指定的地点/城市
            
        Returns:
            包含POI建议列表和地点的字典
            
        Raises:
            LlmProcessingError: LLM调用或解析失败
            ExternalApiError: Geoapify API调用失败
            NotFoundError: 未找到验证的POI
        """
        verified_suggestions = []
        try:
            # 1. 使用LLM获取初步POI建议
            prompt = self.prompt_manager.get_movie_poi_suggestion_prompt(location)
            llm_response_str = await self.llm_client.call_llm(prompt)
            
            # 2. 解析LLM响应
            try:
                llm_suggestions_data = json.loads(llm_response_str)
                initial_suggestions = llm_suggestions_data.get('poi_suggestions', [])
                if not initial_suggestions:
                    logger.warning(f"LLM未能为地点 '{location}' 提供任何POI建议。LLM原始响应: {llm_response_str}")
                    # 即使LLM没有建议，也返回空列表，而不是抛出错误
                    # raise LlmProcessingError(message="LLM未能生成POI建议") 
                    return {"location": location, "suggestions": []}
            except json.JSONDecodeError as e:
                logger.error(f"解析LLM POI建议响应失败: {e}. LLM原始响应: {llm_response_str}")
                raise LlmProcessingError(message="解析LLM POI建议响应失败", details=str(e))
            except Exception as e:
                logger.error(f"处理LLM POI建议时发生意外错误: {e}. LLM原始响应: {llm_response_str}")
                raise LlmProcessingError(message="处理LLM POI建议时出错", details=str(e))

            # 3. 验证每个建议的POI
            for suggestion in initial_suggestions:
                poi_name = suggestion.get('poi_name')
                associated_movies = suggestion.get('associated_movies', [])
                description = suggestion.get('description')
                
                if not poi_name or not associated_movies:
                    logger.warning(f"LLM建议格式不完整，跳过: {suggestion}")
                    continue
                
                try:
                    # 使用Geoapify搜索POI
                    # 注意：这里假设location是城市名，如果需要更精确，需要先进行地理编码
                    location_context = {'city': location} # 简化处理，可能需要更复杂的上下文
                    search_results = self.geoapify_client.search_places_by_name_and_location(
                        name=poi_name,
                        location_context=location_context
                    )
                    
                    if search_results:
                        # 取第一个结果进行验证 (可以考虑更复杂的匹配逻辑)
                        feature = search_results[0]
                        poi_info = self.geoapify_client.extract_poi_info(feature)
                        
                        # 获取Geoapify ID
                        geoapify_id = feature.get('properties', {}).get('place_id')
                        if not geoapify_id:
                             logger.warning(f"Geoapify未能为POI '{poi_name}' 提供place_id，跳过。")
                             continue # 没有ID无法唯一标识
                             
                        # 创建经过验证的PoiSuggestion对象
                        verified_poi = PoiSuggestion(
                            poi_id=geoapify_id,
                            name=poi_info.get('name', poi_name), # 优先使用Geoapify的名称
                            latitude=poi_info.get('coordinates', {}).get('lat'),
                            longitude=poi_info.get('coordinates', {}).get('lon'),
                            address=poi_info.get('address'),
                            category=poi_info.get('category'),
                            associated_movies=associated_movies,
                            description=description # 使用LLM提供的描述
                        )
                        # 检查坐标是否存在
                        if verified_poi.latitude is None or verified_poi.longitude is None:
                            logger.warning(f"Geoapify未能为POI '{poi_name}' 提供有效坐标，跳过。")
                            continue
                            
                        verified_suggestions.append(verified_poi)
                        logger.info(f"成功验证并添加POI: {verified_poi.name}")
                    else:
                        logger.warning(f"Geoapify未能找到POI: '{poi_name}' 在 '{location}'")
                        
                except ExternalApiError as e:
                    logger.error(f"验证POI '{poi_name}' 时Geoapify API出错: {e}")
                    # 可以选择跳过这个POI或向上抛出错误
                    # 这里选择记录错误并继续处理下一个POI
                    continue 
                except Exception as e:
                    logger.error(f"验证POI '{poi_name}' 时发生意外错误: {e}")
                    continue # 跳过这个POI

            if not verified_suggestions:
                logger.warning(f"未能为地点 '{location}' 验证任何电影相关的POI。")
                # 根据需求，这里可以返回空列表或抛出NotFoundError
                # raise NotFoundError(message=f"在 '{location}' 未找到经验证的电影相关POI")
            
            return {"location": location, "suggestions": verified_suggestions}

        except LlmProcessingError as e:
            # LlmProcessingError 已被内部处理并记录
            raise e
        except Exception as e:
            logger.exception(f"获取POI建议时发生未知错误: {e}") # 使用exception记录堆栈跟踪
            raise LlmProcessingError(message="获取POI建议时发生内部错误", details=str(e))

    async def plan_movie_tour(self, location: str, selected_pois: List[Dict], mbti_type_str: Optional[str]) -> Dict[str, Any]:
        """
        根据用户选择的POI和可选的MBTI类型规划电影主题旅行
        
        Args:
            location: 地点/城市
            selected_pois: 用户选择的POI列表 (应符合PoiSuggestion结构)
            mbti_type_str: 可选的MBTI类型字符串
            
        Returns:
            包含行程计划的字典 (符合MovieTourPlanResponse结构)
            
        Raises:
            LlmProcessingError: LLM调用或解析失败
            ValueError: 输入数据无效 (虽然模型层已验证，服务层可再次检查)
        """
        try:
            mbti_type: Optional[MbtiType] = None
            mbti_prefs: Optional[str] = None
            
            # 1. 处理MBTI信息
            if mbti_type_str:
                try:
                    mbti_type = mbti_type_to_enum(mbti_type_str)
                    mbti_prefs = map_mbti_to_preferences(mbti_type)
                except ValueError as e:
                    # 理论上不应发生，因为请求模型已验证
                    logger.warning(f"收到无效的MBTI类型字符串 '{mbti_type_str}' (已通过Pydantic验证？): {e}")
                    # 可以选择忽略MBTI或抛出错误，这里选择忽略
                    mbti_type = None
                    mbti_prefs = None
            
            # 2. 验证selected_pois (可选，假定路由层传入的数据是有效的)
            if not selected_pois:
                raise ValueError("未选择任何POI用于行程规划")
            
            # 将Pydantic模型转换为字典列表以传递给PromptManager
            selected_pois_dicts = [poi.model_dump() for poi in selected_pois]

            # 3. 生成行程规划提示
            prompt = self.prompt_manager.get_movie_tour_plan_prompt(
                location=location,
                selected_pois=selected_pois_dicts,
                mbti_type=mbti_type, 
                mbti_prefs=mbti_prefs
            )
            
            # 4. 调用LLM生成行程
            llm_response_str = await self.llm_client.call_llm(prompt)
            
            # 5. 解析LLM响应
            try:
                itinerary_data = json.loads(llm_response_str)
                # 验证返回的数据结构是否符合预期 (MovieTourPlanResponse)
                # 这里可以添加更严格的验证逻辑，或依赖路由层的response_model
                if not itinerary_data or 'days' not in itinerary_data or not itinerary_data['days']:
                     logger.error(f"LLM返回的行程数据格式不完整或无效。LLM原始响应: {llm_response_str}")
                     raise LlmProcessingError(message="LLM未能生成有效的行程计划")
                
                return itinerary_data
            except json.JSONDecodeError as e:
                logger.error(f"解析LLM行程规划响应失败: {e}. LLM原始响应: {llm_response_str}")
                raise LlmProcessingError(message="解析LLM行程规划响应失败", details=str(e))
            except Exception as e:
                logger.error(f"处理LLM行程规划响应时发生意外错误: {e}. LLM原始响应: {llm_response_str}")
                raise LlmProcessingError(message="处理LLM行程规划响应时出错", details=str(e))

        except LlmProcessingError as e:
            raise e
        except ValueError as e:
            logger.error(f"规划电影行程时输入无效: {e}")
            raise e # 将ValueError传递给上层，转化为HTTP 400
        except Exception as e:
            logger.exception(f"规划电影行程时发生未知错误: {e}")
            raise LlmProcessingError(message="规划电影行程时发生内部错误", details=str(e)) 