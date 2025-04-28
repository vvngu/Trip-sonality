from constants.enums import MbtiType

def map_mbti_to_preferences(mbti_type: MbtiType) -> str:
    """
    将MBTI类型映射为描述性偏好特征的字符串，用于输入LLM
    
    Args:
        mbti_type: MBTI类型枚举值
    
    Returns:
        描述偏好特征的字符串
    """
    # MBTI类型特征映射
    mbti_preferences = {
        # 分析家(Analysts)
        MbtiType.INTJ: "独立、理性、注重效率的思考者，偏好独自探索有深度的景点，喜欢提前规划行程，注重行程的逻辑性和效率，享受有知识性的体验，避免过度社交场所。",
        MbtiType.INTP: "好奇、创新、理论导向的思考者，喜欢探索独特的景点和概念，享受有思考空间的地方，注重发现新知识，偏好灵活的行程安排，通常避免拥挤的旅游景点。",
        MbtiType.ENTJ: "目标导向、果断、组织能力强，喜欢高效率的行程，偏好文化和历史景点，注重体验的质量和价值，享受挑战性活动，善于规划和领导。",
        MbtiType.ENTP: "灵活、创新、喜欢辩论的探索者，喜欢尝试新事物和非传统景点，享受即兴和自发的冒险，喜欢与当地人交流，寻求多样化的体验。",
        
        # 外交家(Diplomats)
        MbtiType.INFJ: "有洞察力、理想主义、注重意义的人道主义者，喜欢安静有意义的景点，注重体验的精神层面，偏好与文化和历史深度连接，避免过度商业化的场所。",
        MbtiType.INFP: "理想主义、有同理心、注重个人价值观的梦想家，喜欢艺术与自然融合的地方，享受有故事和灵感的场所，偏好自由探索而非严格计划。",
        MbtiType.ENFJ: "富有同情心、社交能力强、注重和谐的鼓舞者，喜欢能与当地文化和人民互动的体验，注重团体活动和共享经历，享受有社会意义的旅行。",
        MbtiType.ENFP: "热情、创意丰富、注重可能性的自由精神，喜欢探索多样化和新奇的体验，享受自发的冒险，喜欢结交新朋友，对文化和创意场所有浓厚兴趣。",
        
        # 哨兵(Sentinels)
        MbtiType.ISTJ: "实际、负责、注重细节的传统主义者，偏好周密规划的行程，欣赏历史和文化景点，注重旅行的实用性和价值，享受有序和可预测的体验。",
        MbtiType.ISFJ: "细心、传统、乐于助人的保护者，喜欢熟悉和舒适的环境，注重历史和文化，偏好温和的活动，重视旅行的意义和与家人朋友的联系。",
        MbtiType.ESTJ: "有组织能力、实际、注重传统的管理者，喜欢结构化的旅行体验，偏好经典景点，注重时间管理和行程效率，喜欢有明确目标的活动。",
        MbtiType.ESFJ: "友善、注重和谐、负责任的照顾者，喜欢社交和团体活动，注重传统文化体验，偏好温馨舒适的环境，享受与他人分享的旅行时光。",
        
        # 探险家(Explorers)
        MbtiType.ISTP: "灵活、冷静、观察力强的实干家，喜欢动手实践的体验，注重刺激和冒险，对机械和工艺有兴趣，享受自由探索而非固定计划。",
        MbtiType.ISFP: "艺术感强、敏感、注重和谐的艺术家，喜欢美丽的自然和艺术景点，注重感官体验，偏好自由自在的行程，享受当下的美好瞬间。",
        MbtiType.ESTP: "活力充沛、实用主义、喜欢冒险的行动者，追求刺激和新奇体验，喜欢体育和户外活动，享受即兴决定和多样化体验，注重现实享受。",
        MbtiType.ESFP: "随和、热情、享乐主义的表演者，喜欢社交和娱乐活动，注重感官享受，偏好有趣和新奇的体验，享受与他人分享快乐时光。"
    }
    
    return mbti_preferences.get(mbti_type, "独特的旅行者，有自己的偏好和风格。")


def mbti_type_to_enum(mbti_type: str) -> MbtiType:
    """验证MBTI类型是否有效，并返回对应的枚举值"""
    try:
        return MbtiType(mbti_type.upper())
    except ValueError:
        print(f"严重错误：函数 get_mbti_enum 接收到未经验证的 MBTI 字符串: {mbti_type}") # 添加日志记录
        raise ValueError("Invalid MBTI type or incorrect processing") 


def format_poi_suggestion_for_prompt(poi_suggestions):
    """
    将POI建议格式化为适合LLM提示的字符串
    
    Args:
        poi_suggestions: POI建议列表
    
    Returns:
        格式化后的字符串，用于LLM提示
    """
    formatted_text = ""
    for i, poi in enumerate(poi_suggestions, 1):
        formatted_text += f"{i}. {poi.name}: {poi.description}\n   地址: {poi.address}\n   类型: {poi.category}\n   电影关联: {poi.movie_connection}\n\n"
    return formatted_text


def parse_llm_itinerary_response(llm_response):
    """
    解析LLM返回的行程响应，提取日程信息
    
    Args:
        llm_response: 来自LLM的响应字符串
    
    Returns:
        解析后的行程日程列表
    """
    try:
        # 这里实现解析逻辑，将LLM返回的文本解析为结构化的行程
        # 这是一个简化的实现，实际情况可能需要更复杂的解析逻辑
        days = []
        current_day = None
        current_items = []
        
        lines = llm_response.strip().split('\n')
        for line in lines:
            line = line.strip()
            # 检测新的一天
            if line.startswith("第") and ("天" in line):
                # 如果已经有当前日程，保存它
                if current_day is not None:
                    days.append({"day": current_day, "items": current_items})
                # 开始新的一天
                current_day = line
                current_items = []
            # 检测行程项目（通常格式为"时间段: 活动"）
            elif ":" in line or "：" in line:
                # 统一冒号格式
                line = line.replace("：", ":")
                parts = line.split(":", 1)
                if len(parts) == 2:
                    time_slot = parts[0].strip()
                    activity = parts[1].strip()
                    current_items.append({"time_slot": time_slot, "activity": activity})
        
        # 添加最后一天
        if current_day is not None:
            days.append({"day": current_day, "items": current_items})
        
        return days
    
    except Exception as e:
        print(f"解析LLM行程响应时出错: {str(e)}")
        return []


def validate_coordinates(latitude, longitude):
    """
    验证坐标是否有效
    
    Args:
        latitude: 纬度
        longitude: 经度
    
    Returns:
        如果坐标有效，返回True；否则返回False
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True
        return False
    except:
        return False 