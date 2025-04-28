from enum import Enum, auto

class MbtiType(str, Enum):
    """MBTI人格类型枚举"""
    # 分析家(Analysts)
    INTJ = "INTJ"  # 建筑师
    INTP = "INTP"  # 逻辑学家
    ENTJ = "ENTJ"  # 指挥官
    ENTP = "ENTP"  # 辩论家
    
    # 外交家(Diplomats)
    INFJ = "INFJ"  # 提倡者
    INFP = "INFP"  # 调停者
    ENFJ = "ENFJ"  # 主人公
    ENFP = "ENFP"  # 竞选者
    
    # 哨兵(Sentinels)
    ISTJ = "ISTJ"  # 物流师
    ISFJ = "ISFJ"  # 守卫者
    ESTJ = "ESTJ"  # 总经理
    ESFJ = "ESFJ"  # 执政官
    
    # 探险家(Explorers)
    ISTP = "ISTP"  # 鉴赏家
    ISFP = "ISFP"  # 冒险家
    ESTP = "ESTP"  # 企业家
    ESFP = "ESFP"  # 表演者
    
    @classmethod
    def list(cls):
        """返回所有MBTI类型的列表"""
        return [e.value for e in cls] 