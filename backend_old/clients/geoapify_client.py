import requests
from typing import Dict, List, Any, Optional
from config import Config
from utils.error_handlers import ExternalApiError

class GeoapifyClient:
    """Geoapify Places API 客户端类"""
    
    def __init__(self):
        self.base_url = Config.GEOAPIFY_BASE_URL
        self.api_key = Config.GEOAPIFY_API_KEY
        
        if not self.api_key:
            raise ValueError("缺少Geoapify API密钥。请在.env文件中设置GEOAPIFY_API_KEY。")
    
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        向Geoapify API发送请求
        
        Args:
            params: 请求参数
            
        Returns:
            API响应JSON
            
        Raises:
            ExternalApiError: API调用失败时
        """
        # 添加API密钥到参数
        params['apiKey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ExternalApiError(
                    message="Geoapify API认证失败",
                    details="API密钥无效或已过期",
                    status_code=401
                )
            raise ExternalApiError(
                message="Geoapify API请求失败",
                details=str(e),
                status_code=e.response.status_code if hasattr(e, 'response') else 500
            )
        except requests.exceptions.Timeout:
            raise ExternalApiError(message="Geoapify API请求超时", status_code=504)
        except requests.exceptions.RequestException as e:
            raise ExternalApiError(message="Geoapify API连接错误", details=str(e))
        except ValueError as e:
            raise ExternalApiError(message="解析Geoapify API响应失败", details=str(e))
    
    def search_places_by_name_and_location(
        self, 
        name: str, 
        location_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        根据名称和地理位置上下文搜索地点
        
        Args:
            name: 地点名称
            location_context: 地理位置上下文
                可包含: country, city, state, county 等
            
        Returns:
            匹配的POI列表
            
        Raises:
            ExternalApiError: API调用失败时
        """
        params = {
            'name': name,
            'limit': 10,
            'format': 'json'
        }
        
        # 添加位置上下文过滤
        for key, value in location_context.items():
            if value:
                params[key] = value
        
        response = self._make_request(params)
        
        # 检查是否有结果
        if not response.get('features'):
            return []
        
        return response['features']
    
    def search_places_by_category_and_location(
        self, 
        categories: List[str], 
        location_context: Dict[str, Any], 
        radius: int = 5000,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        根据类别和地理位置搜索地点
        
        Args:
            categories: 地点类别列表
            location_context: 地理位置上下文
                必须包含: lon, lat (经纬度坐标)
                可选: country, city, state 等
            radius: 搜索半径(米)
            limit: 返回结果数量上限
            
        Returns:
            匹配的POI列表
            
        Raises:
            ExternalApiError: API调用失败时
            ValueError: 缺少必需参数时
        """
        # 检查必需参数
        if not categories:
            raise ValueError("缺少地点类别")
        
        if 'lat' not in location_context or 'lon' not in location_context:
            if 'city' not in location_context and 'country' not in location_context:
                raise ValueError("缺少位置信息(经纬度坐标或城市/国家)")
        
        params = {
            'categories': ','.join(categories),
            'limit': limit,
            'format': 'json'
        }
        
        # 添加位置上下文
        if 'lat' in location_context and 'lon' in location_context:
            params['filter'] = f"circle:{location_context['lon']},{location_context['lat']},{radius}"
            
        # 添加城市/国家过滤
        for key in ['city', 'country', 'state']:
            if key in location_context and location_context[key]:
                params[key] = location_context[key]
        
        response = self._make_request(params)
        
        # 检查是否有结果
        if not response.get('features'):
            return []
        
        return response['features']
    
    def extract_poi_info(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        从API响应中提取POI信息
        
        Args:
            feature: Geoapify API返回的feature对象
            
        Returns:
            格式化的POI信息
        """
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        
        result = {
            'name': properties.get('name', '未知地点'),
            'category': properties.get('category', '未分类'),
            'address': properties.get('formatted', ''),
            'city': properties.get('city', ''),
            'country': properties.get('country', ''),
            'coordinates': {}
        }
        
        # 提取坐标
        if geometry.get('type') == 'Point' and geometry.get('coordinates'):
            coordinates = geometry['coordinates']
            result['coordinates'] = {
                'lon': coordinates[0],
                'lat': coordinates[1]
            }
        
        return result 