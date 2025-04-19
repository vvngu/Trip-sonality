import requests
from typing import Dict, List, Any, Optional
from config import Config
from utils.error_handlers import ExternalApiError, NotFoundError

class TMDbClient:
    """TMDb API客户端类"""
    
    def __init__(self):
        self.base_url = Config.TMDB_BASE_URL
        self.api_key = Config.TMDB_API_KEY
        
        if not self.api_key:
            raise ValueError("缺少TMDB API密钥。请在.env文件中设置TMDB_API_KEY。")
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        向TMDb API发送请求
        
        Args:
            endpoint: API端点
            params: 请求参数
            
        Returns:
            API响应JSON
            
        Raises:
            ExternalApiError: API调用失败时
            NotFoundError: 资源未找到时
        """
        if params is None:
            params = {}
        
        # 添加API密钥到参数
        params['api_key'] = self.api_key
        
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            
            # 检查HTTP状态码
            if response.status_code == 404:
                raise NotFoundError(message="电影未找到", details=f"TMDb API无法找到请求的资源: {endpoint}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ExternalApiError(
                    message="TMDb API认证失败",
                    details="API密钥无效或已过期",
                    status_code=401
                )
            raise ExternalApiError(
                message="TMDb API请求失败",
                details=str(e),
                status_code=e.response.status_code if hasattr(e, 'response') else 500
            )
        except requests.exceptions.Timeout:
            raise ExternalApiError(message="TMDb API请求超时", status_code=504)
        except requests.exceptions.RequestException as e:
            raise ExternalApiError(message="TMDb API连接错误", details=str(e))
        except ValueError as e:
            raise ExternalApiError(message="解析TMDb API响应失败", details=str(e))
    
    def search_movie(self, title: str) -> Dict[str, Any]:
        """
        根据标题搜索电影
        
        Args:
            title: 电影标题
            
        Returns:
            最佳匹配的电影数据或空字典
            
        Raises:
            ExternalApiError: API调用失败时
        """
        params = {
            'query': title,
            'language': 'zh-CN',  # 首选中文结果
            'include_adult': 'false',
            'page': 1
        }
        
        data = self._make_request('/search/movie', params)
        
        # 检查是否有结果
        if not data.get('results') or len(data['results']) == 0:
            # 尝试英文搜索
            params['language'] = 'en-US'
            data = self._make_request('/search/movie', params)
            
            if not data.get('results') or len(data['results']) == 0:
                raise NotFoundError(
                    message=f"未找到与'{title}'相关的电影",
                    details="请尝试使用其他电影名称或检查拼写"
                )
        
        # 返回最佳匹配结果
        return data['results'][0]
    
    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """
        获取电影详细信息
        
        Args:
            movie_id: 电影ID
            
        Returns:
            电影详细信息
            
        Raises:
            ExternalApiError: API调用失败时
            NotFoundError: 电影未找到时
        """
        # 获取基本详情
        params = {
            'language': 'zh-CN',  # 首选中文
            'append_to_response': 'keywords,production_countries,production_companies'
        }
        
        movie_data = self._make_request(f'/movie/{movie_id}', params)
        
        # 如果中文结果不完整，尝试获取英文详情补充
        if not movie_data.get('overview'):
            params['language'] = 'en-US'
            en_data = self._make_request(f'/movie/{movie_id}', params)
            
            # 合并数据，优先使用中文
            for key, value in en_data.items():
                if not movie_data.get(key) and value:
                    movie_data[key] = value
        
        return movie_data
    
    def get_movie_keywords(self, movie_id: int) -> List[str]:
        """
        获取电影关键词
        
        Args:
            movie_id: 电影ID
            
        Returns:
            关键词列表
            
        Raises:
            ExternalApiError: API调用失败时
        """
        data = self._make_request(f'/movie/{movie_id}/keywords')
        return [keyword['name'] for keyword in data.get('keywords', [])] 