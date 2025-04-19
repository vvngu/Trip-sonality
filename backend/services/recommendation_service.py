from typing import Dict, List, Any, Optional
from constants.enums import MbtiType
from utils.helpers import map_mbti_to_preferences
from clients.tmdb_client import TMDbClient
from clients.geoapify_client import GeoapifyClient
from llm.llm_client import LLMClient
from llm.prompt_manager import PromptManager
from utils.error_handlers import ExternalApiError, LlmProcessingError, NotFoundError, ValidationError

class RecommendationService:
    """电影主题旅行推荐服务"""
    
    def __init__(self):
        """初始化服务依赖"""
        self.tmdb_client = TMDbClient()
        self.geoapify_client = GeoapifyClient()
        self.llm_client = LLMClient()
        
    def generate_solo_movie_recommendations(
        self, 
        mbti_type: MbtiType, 
        movie_input: str
    ) -> Dict[str, Any]:
        """
        生成基于MBTI类型和电影的Solo旅行推荐
        
        Args:
            mbti_type: MBTI人格类型
            movie_input: 电影名称或关键词
            
        Returns:
            包含旅行推荐的响应对象
            
        Raises:
            ExternalApiError: 外部API调用失败时
            LlmProcessingError: LLM处理失败时
            NotFoundError: 电影未找到时
            ValidationError: 输入验证失败时
        """
        try:
            # 1. 获取MBTI偏好描述
            mbti_preferences = self._get_mbti_preferences(mbti_type)
            
            # 2. 搜索电影并获取详情
            movie_info = self._get_movie_info(movie_input)
            
            # 3. 使用LLM提取电影中的地点和主题
            locations_themes = self._extract_locations_from_llm(movie_info)
            
            # 4. 搜索相关POI
            poi_list = self._search_relevant_pois(locations_themes, movie_info)
            
            # 5. 生成最终推荐
            recommendation_data = self._generate_llm_recommendation(
                mbti_type=mbti_type,
                prefs=mbti_preferences,
                movie_info=movie_info,
                locations_themes=locations_themes,
                pois=poi_list
            )
            
            # 6. 构建最终响应
            response = {
                'recommendation': recommendation_data.get('recommendation', {}),
                'movie_info': movie_info,
                'mbti_type': mbti_type.value if isinstance(mbti_type, MbtiType) else mbti_type
            }
            
            return response
            
        except NotFoundError as e:
            # 重新抛出，不需修改
            raise e
        except ExternalApiError as e:
            # 重新抛出，不需修改
            raise e
        except LlmProcessingError as e:
            # 重新抛出，不需修改
            raise e
        except ValueError as e:
            # 转换为验证错误
            raise ValidationError(
                message="处理请求时出错",
                details=str(e)
            )
        except Exception as e:
            # 捕获意外错误并转换为合适的错误类型
            raise ExternalApiError(
                message="生成推荐时发生错误",
                details=str(e)
            )
    
    def _get_mbti_preferences(self, mbti_type: MbtiType) -> str:
        """
        获取MBTI类型对应的偏好描述
        
        Args:
            mbti_type: MBTI人格类型
            
        Returns:
            MBTI偏好描述文本
        """
        return map_mbti_to_preferences(mbti_type)
    
    def _get_movie_info(self, movie_input: str) -> Dict[str, Any]:
        """
        搜索电影并获取详细信息
        
        Args:
            movie_input: 电影名称或关键词
            
        Returns:
            包含电影信息的字典
            
        Raises:
            NotFoundError: 电影未找到时
            ExternalApiError: TMDb API调用失败时
        """
        # 搜索电影
        movie_basic = self.tmdb_client.search_movie(movie_input)
        movie_id = movie_basic.get('id')
        
        if not movie_id:
            raise NotFoundError(
                message=f"未找到与'{movie_input}'相关的电影",
                details="请尝试使用其他电影名称或检查拼写"
            )
        
        # 获取电影详情
        movie_details = self.tmdb_client.get_movie_details(movie_id)
        
        # 提取电影信息
        movie_info = {
            'id': movie_id,
            'title': movie_details.get('title', movie_input),
            'overview': movie_details.get('overview', ''),
            'release_date': movie_details.get('release_date', ''),
            'poster_path': movie_details.get('poster_path', ''),
            'backdrop_path': movie_details.get('backdrop_path', '')
        }
        
        # 提取关键词
        keywords = []
        if 'keywords' in movie_details:
            keywords = [k.get('name', '') for k in movie_details['keywords'].get('keywords', [])]
        
        # 提取制片国家
        production_countries = []
        if 'production_countries' in movie_details:
            production_countries = [c.get('name', '') for c in movie_details.get('production_countries', [])]
        
        # 将关键词和制片国家添加到movie_info中，方便后续处理
        movie_info['keywords'] = keywords
        movie_info['production_countries'] = production_countries
        
        return movie_info
    
    def _extract_locations_from_llm(self, movie_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用LLM从电影信息中提取潜在的旅行地点和主题
        
        Args:
            movie_info: 电影信息字典
            
        Returns:
            包含地点和主题的字典
            
        Raises:
            LlmProcessingError: LLM处理失败时
        """
        # 准备提取提示
        extraction_prompt = PromptManager.get_location_extraction_prompt(
            movie_title=movie_info['title'],
            overview=movie_info['overview'],
            keywords=movie_info.get('keywords', []),
            production_countries=movie_info.get('production_countries', [])
        )
        
        # 调用LLM
        extraction_response = self.llm_client.call_llm(extraction_prompt)
        
        # 解析响应
        locations_themes = self.llm_client.extract_json_from_response(extraction_response)
        
        return locations_themes
    
    def _search_relevant_pois(
        self, 
        locations_themes: Dict[str, Any], 
        movie_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        搜索与电影相关的兴趣点(POI)
        
        Args:
            locations_themes: 从LLM提取的地点和主题信息
            movie_info: 电影信息字典
            
        Returns:
            POI列表
            
        Raises:
            ExternalApiError: Geoapify API调用失败时
        """
        poi_list = []
        
        # 获取主要目的地信息
        primary_destination = locations_themes.get('primary_destination', {})
        destination_city = primary_destination.get('city', '')
        destination_country = primary_destination.get('country', '')
        
        if not destination_city or not destination_country:
            # 如果LLM未能提取出明确的目的地，尝试使用制片国家的首都或主要城市
            production_countries = movie_info.get('production_countries', [])
            if production_countries and len(production_countries) > 0:
                destination_country = production_countries[0]
                # 这里可以添加一个映射首都的功能，但简化起见，我们暂时跳过
        
        # 如果有明确的目的地城市
        if destination_city and destination_country:
            location_context = {
                'city': destination_city,
                'country': destination_country
            }
            
            # 从提取的地点中获取关键词列表
            location_names = []
            location_types = []
            
            for location in locations_themes.get('locations', []):
                name = location.get('name', '')
                location_type = location.get('type', '')
                
                if name:
                    location_names.append(name)
                if location_type and location_type not in ['城市', '国家', 'city', 'country']:
                    location_types.append(location_type)
            
            # 搜索特定地点
            poi_list.extend(self._search_pois_by_names(location_names, location_context))
            
            # 如果POI数量不足，尝试按类别搜索
            if len(poi_list) < 3 and location_types:
                poi_list.extend(self._search_pois_by_categories(location_types, location_context, poi_list))
        
        return poi_list
    
    def _search_pois_by_names(
        self, 
        location_names: List[str], 
        location_context: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        根据地点名称搜索POI
        
        Args:
            location_names: 地点名称列表
            location_context: 地理位置上下文 (城市, 国家)
            
        Returns:
            POI列表
        """
        poi_list = []
        # 限制为前3个，避免过多API调用
        for name in location_names[:3]:
            try:
                results = self.geoapify_client.search_places_by_name_and_location(
                    name=name,
                    location_context=location_context
                )
                
                # 每个地点最多取2个结果
                for result in results[:2]:
                    poi_info = self.geoapify_client.extract_poi_info(result)
                    poi_list.append(poi_info)
            except ExternalApiError:
                # 忽略单个POI搜索失败，继续搜索其他POI
                continue
        
        return poi_list
    
    def _search_pois_by_categories(
        self, 
        categories: List[str], 
        location_context: Dict[str, str],
        existing_pois: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        根据类别搜索POI
        
        Args:
            categories: 类别列表
            location_context: 地理位置上下文 (城市, 国家)
            existing_pois: 已有的POI列表，用于去重
            
        Returns:
            POI列表
        """
        poi_list = []
        try:
            # 最多使用3个类别
            category_list = categories[:3]
            results = self.geoapify_client.search_places_by_category_and_location(
                categories=category_list,
                location_context=location_context,
                radius=5000,
                limit=5
            )
            
            for result in results:
                poi_info = self.geoapify_client.extract_poi_info(result)
                
                # 检查是否已经存在相同名称的POI
                if not any(p.get('name') == poi_info.get('name') for p in existing_pois):
                    poi_list.append(poi_info)
        except (ExternalApiError, ValueError):
            # 忽略类别搜索失败
            pass
        
        return poi_list
    
    def _generate_llm_recommendation(
        self, 
        mbti_type: MbtiType, 
        prefs: str, 
        movie_info: Dict[str, Any], 
        locations_themes: Dict[str, Any],
        pois: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        生成最终的旅行推荐
        
        Args:
            mbti_type: MBTI人格类型
            prefs: MBTI偏好描述
            movie_info: 电影信息字典
            locations_themes: 地点和主题信息
            pois: POI列表
            
        Returns:
            推荐数据字典
            
        Raises:
            LlmProcessingError: LLM处理失败时
        """
        # 准备推荐提示
        recommendation_prompt = PromptManager.get_recommendation_generation_prompt(
            mbti_type=mbti_type,
            mbti_prefs=prefs,
            movie_info=movie_info,
            locations_themes=locations_themes,
            pois=pois
        )
        
        # 调用LLM
        recommendation_response = self.llm_client.call_llm(recommendation_prompt)
        
        # 解析响应
        recommendation_data = self.llm_client.extract_json_from_response(recommendation_response)
        
        return recommendation_data 