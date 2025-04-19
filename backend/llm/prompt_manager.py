from typing import Dict, List, Any, Optional
from constants.enums import MbtiType

class PromptManager:
    """LLM提示模板管理器"""
    
    @staticmethod
    def get_location_extraction_prompt(
        movie_title: str, 
        overview: str, 
        keywords: List[str] = None,
        production_countries: List[str] = None
    ) -> str:
        """
        生成用于从电影信息中提取潜在地点/主题的提示
        
        Args:
            movie_title: 电影标题
            overview: 电影概述
            keywords: 电影关键词
            production_countries: 制片国家/地区
            
        Returns:
            格式化的提示文本
        """
        keywords_str = "、".join(keywords) if keywords else "无相关关键词"
        countries_str = "、".join(production_countries) if production_countries else "未知"
        
        prompt = f"""作为一位电影旅行专家，请从以下电影信息中提取可能成为旅行目的地的地点、城市或国家，以及潜在的旅行主题。

电影信息:
- 标题: {movie_title}
- 概述: {overview}
- 关键词: {keywords_str}
- 制片国家/地区: {countries_str}

请分析这部电影的场景、故事、主题和氛围，提取以下信息:
1. 主要取景地或故事发生地 (具体地点、城市和国家)
2. 电影中出现或暗示的特色场所类型 (如特定建筑、自然景观、历史遗迹等)
3. 适合作为旅行主题的元素 (基于电影的情感基调、视觉风格或核心主题)

请以JSON格式返回结果:
```json
{{
  "locations": [
    {{
      "name": "地点名称",
      "type": "城市/国家/地标/自然景观等",
      "relevance": "与电影的关联度说明",
      "coordinates": {{  // 如果知道的话
        "lat": 纬度,
        "lon": 经度
      }}
    }}
  ],
  "themes": [
    {{
      "name": "主题名称",
      "description": "主题描述",
      "relevance": "与电影的关联度说明"
    }}
  ],
  "primary_destination": {{
    "city": "主要目的地城市",
    "country": "主要目的地国家",
    "explanation": "为什么选择这个目的地"
  }}
}}
```

注意:
- 如果电影是虚构世界或未指明地点，请尝试提取能启发现实世界旅行的相似地点或主题
- 优先选择具体、可实际访问的地点，而非过于宽泛的区域
- 为每个地点和主题提供与电影的明确关联性说明
- 如果确实无法从电影中提取地点信息，请提供基于电影风格和主题的合理替代建议"""
        
        return prompt
    
    @staticmethod
    def get_poi_validation_prompt(
        movie_context: str, 
        poi_list: List[Dict[str, Any]]
    ) -> str:
        """
        生成用于验证POI与电影关联性的提示
        
        Args:
            movie_context: 电影上下文信息
            poi_list: POI列表
            
        Returns:
            格式化的提示文本
        """
        poi_str = "\n".join([
            f"- 名称: {poi.get('name', '未知')}\n  类别: {poi.get('category', '未知')}\n  地址: {poi.get('address', '未知')}\n  所在地: {poi.get('city', '未知')}, {poi.get('country', '未知')}"
            for poi in poi_list
        ])
        
        prompt = f"""作为一位电影旅行体验设计专家，请评估以下兴趣点(POI)与电影的关联性和旅行体验潜力。

电影上下文:
{movie_context}

兴趣点列表:
{poi_str}

对于每个兴趣点，请评估:
1. 与电影的主题、氛围或视觉风格的关联度(高/中/低)
2. 能否提供与电影相关的独特体验
3. 为什么这个地点适合作为电影主题旅行的一部分
4. 建议的游览活动或体验方式，以最大化与电影的连接

请以JSON格式返回结果，包含每个POI的评估和丰富的描述:
```json
[
  {{
    "name": "POI名称",
    "movie_relevance": "高/中/低",
    "relevance_explanation": "关联性的详细解释",
    "experience_description": "建议的游览体验描述",
    "activities": ["建议活动1", "建议活动2"]
  }}
]
```"""
        
        return prompt
    
    @staticmethod
    def get_recommendation_generation_prompt(
        mbti_type: MbtiType, 
        mbti_prefs: str, 
        movie_info: Dict[str, Any], 
        locations_themes: Dict[str, Any],
        pois: List[Dict[str, Any]] = None
    ) -> str:
        """
        生成最终旅行推荐的核心提示
        
        Args:
            mbti_type: MBTI类型
            mbti_prefs: MBTI偏好描述
            movie_info: 电影信息
            locations_themes: 地点和主题信息
            pois: 地点列表
            
        Returns:
            格式化的提示文本
        """
        movie_title = movie_info.get('title', '未知电影')
        movie_overview = movie_info.get('overview', '无概述')
        
        # 提取主要目的地
        primary_destination = locations_themes.get('primary_destination', {})
        destination_city = primary_destination.get('city', '未知城市')
        destination_country = primary_destination.get('country', '未知国家')
        
        # 格式化POI列表
        poi_str = ""
        if pois:
            poi_str = "\n".join([
                f"- {poi.get('name', '未知地点')}: {poi.get('description', '无描述')}"
                for poi in pois[:5]  # 限制为最多5个POI
            ])
        else:
            poi_str = "没有具体兴趣点信息"
        
        prompt = f"""作为一位专注于个性化旅行体验的旅行顾问，请为一位MBTI类型为{mbti_type}的独自旅行者设计一个基于电影《{movie_title}》的主题旅行方案。

## 旅行者信息
- MBTI类型: {mbti_type}
- 个性特点和偏好: {mbti_prefs}

## 电影信息
- 电影名称: {movie_title}
- 电影简介: {movie_overview}

## 目的地信息
- 主要城市: {destination_city}
- 所在国家: {destination_country}

## 潜在兴趣点
{poi_str}

请创建一个深度融合MBTI个性特点和电影元素的旅行推荐，包括:
1. 吸引人的标题，融合电影主题和目的地
2. 根据MBTI类型定制的旅行整体叙事和氛围
3. 2-4个符合MBTI偏好的推荐景点/体验，每个都与电影元素相关
4. 2-3个个性化活动建议，解释它们如何既满足该MBTI类型的偏好，又与电影主题相呼应
5. 行程中的"特别时刻"，即一个完美契合MBTI类型和电影氛围的独特体验

请以JSON格式返回结果:
```json
{{
  "recommendation": {{
    "title": "引人入胜的旅行标题",
    "movie_title": "{movie_title}",
    "movie_overview": "电影简介",
    "theme": "旅行主题",
    "destination": "{destination_city}, {destination_country}",
    "description": "整体旅行描述，包含MBTI和电影元素融合的叙述",
    "places_of_interest": [
      {{
        "name": "地点名称",
        "description": "地点详细描述",
        "relation_to_movie": "与电影的关联说明",
        "category": "地点类型"
      }}
    ],
    "activities": [
      {{
        "title": "活动标题",
        "description": "活动详细描述",
        "relation_to_movie": "与电影的关联",
        "relation_to_mbti": "与MBTI类型的关联",
        "time_of_day": "建议的时间段"
      }}
    ],
    "mbti_relevance": "详细说明这个旅行方案如何特别适合{mbti_type}类型的人"
  }}
}}
```

请确保:
1. 内容真实、具体，避免过于宽泛的描述
2. 深入挖掘电影的视觉风格、情感基调和核心主题
3. 准确反映{mbti_type}的旅行偏好和决策风格
4. 建议切实可行且有特色，不仅是常规旅游项目
5. 所有内容保持严格的JSON格式，确保可被程序解析"""
        
        return prompt

    @staticmethod
    def get_movie_poi_suggestion_prompt(location: str) -> str:
        """
        生成用于获取地点相关的电影POI建议的提示
        
        Args:
            location: 用户指定的地点/城市
            
        Returns:
            格式化的提示文本
        """
        prompt = f"""作为一名熟悉全球电影取景地的专家，请在**{location}**这个地方，列出至少5个与著名或有特色的电影相关的兴趣点(POI)。

对于每个POI，请提供:
1.  **poi_name**: 地点的准确名称。
2.  **associated_movies**: 一个包含至少一部与此POI相关的电影标题的列表。
3.  **description**: 一段简短的描述，说明这个地点与所列电影的关系，或者为什么它是一个有趣的电影相关地点。

请以JSON格式返回结果，格式如下:
```json
{{
  "poi_suggestions": [
    {{
      "poi_name": "POI 1的名称",
      "associated_movies": ["电影A", "电影B"],
      "description": "关于POI 1及其与电影关联的描述"
    }},
    {{
      "poi_name": "POI 2的名称",
      "associated_movies": ["电影C"],
      "description": "关于POI 2及其与电影关联的描述"
    }}
    // ... 更多POI
  ]
}}
```

请确保:
- 地点位于或紧邻**{location}**。
- 电影是相对知名或有代表性的。
- 描述清晰地说明了POI与电影的联系。
- 输出严格遵守JSON格式。"""
        return prompt

    @staticmethod
    def get_movie_tour_plan_prompt(
        location: str, 
        selected_pois: List[Dict], 
        mbti_type: Optional[MbtiType] = None, 
        mbti_prefs: Optional[str] = None
    ) -> str:
        """
        生成用于创建电影主题旅行计划的提示
        
        Args:
            location: 地点/城市
            selected_pois: 用户选择的POI列表 (包含名称、坐标、关联电影等)
            mbti_type: 可选的MBTI类型
            mbti_prefs: 可选的MBTI偏好描述
            
        Returns:
            格式化的提示文本
        """
        # 格式化选定的POI信息
        poi_details_str = ""
        for i, poi in enumerate(selected_pois, 1):
            movies = ", ".join(poi.get('associated_movies', []))
            poi_details_str += f"{i}. {poi.get('name', '未知POI')}\n   - 关联电影: {movies}\n   - 描述: {poi.get('description', '无')}\n   - 位置: 纬度 {poi.get('latitude', 'N/A')}, 经度 {poi.get('longitude', 'N/A')}\n\n"
        
        # 构建MBTI信息段落
        mbti_section = ""
        if mbti_type and mbti_prefs:
            mbti_section = f"## 旅行者个性化需求\n- MBTI类型: {mbti_type.value}\n- 个性偏好: {mbti_prefs}\n请在行程规划中特别考虑这些偏好，例如活动类型、节奏、餐饮选择和整体氛围。"
        else:
            mbti_section = "## 旅行者个性化需求\n未提供MBTI类型，请设计一个适合普遍独自旅行者的行程。"
        
        prompt = f"""作为一名专业的个性化旅行规划师，请为一位前往**{location}**的**独自旅行者**设计一个为期一天的详细电影主题旅行计划。

旅行者已选择了以下与电影相关的兴趣点(POI):
{poi_details_str}

{mbti_section}

请创建一个引人入胜且实用的单日行程计划，包含:
1.  **行程标题 (title)**: 结合地点、电影元素和(如果提供)MBTI类型的吸引人标题。
2.  **行程概述 (overview)**: 对整个行程的简要介绍，强调其独特性、电影主题和(如果提供)MBTI契合度。
3.  **详细行程项 (itinerary_items)**: 一个包含多个步骤的列表，涵盖全天活动。每个步骤应包含:
    *   `type`: 项目类型 ('poi', 'meal', 'activity', 'travel' 等)。
    *   `name`: 项目名称 (例如，访问某个POI，午餐，电影主题活动)。
    *   `description`: 详细描述，自然地融入电影参考、Solo旅行考量和(如果提供)MBTI偏好。对于'meal'或'activity'，可以推荐具体的餐厅类型或活动。
    *   `start_time`: 建议的开始时间 (例如 "09:00", "13:00")。
    *   `duration_minutes`: 估计的持续时间（分钟）。
    *   `poi_details`: 如果`type`是'poi'，请包含传入的完整POI信息 (名称、坐标、电影等)。
    *   `location_details`: (可选) 对于餐厅、咖啡馆等，可以提供一些细节 (如类型、氛围描述)。

**重要指示:**
-   行程应围绕用户选择的POI展开，合理安排访问顺序。
-   在POI之间穿插相关的活动、餐饮建议。
-   活动和餐饮建议应考虑"独自旅行"的特点，并(如果提供MBTI)符合其偏好。
-   电影元素的融入要自然，不仅仅是提及电影名称。
-   建议的地点（如餐厅）应位于所选POI附近或行程路线上。
-   提供一个逻辑连贯、节奏合理的单日行程。

请以JSON格式返回完整的行程计划，结构如下:
```json
{{
  "title": "行程标题",
  "location": "{location}",
  "overview": "行程概述...",
  "days": [  // 设计为支持多日，但本次只需返回一天
    {{
      "day_number": 1,
      "theme": "可选的当天主题",
      "items": [
        {{
          "type": "poi | meal | activity | travel",
          "name": "项目名称",
          "description": "详细描述...",
          "start_time": "HH:MM",
          "duration_minutes": 整数,
          "poi_details": {{ /* 仅当 type 为 'poi' 时包含 */ }},
          "location_details": {{ /* 可选，用于餐厅等 */ }}
        }},
        // ... 更多行程项
      ]
    }}
  ]
}}
```

请确保最终输出严格遵守JSON格式。"""
        return prompt 