import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

class Config:
    """应用配置类"""
    # API密钥
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    GEOAPIFY_API_KEY = os.getenv('GEOAPIFY_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # LLM配置
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4-turbo')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '1000'))
    
    # API URL
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    GEOAPIFY_BASE_URL = "https://api.geoapify.com/v2/places"
    
    # Flask配置
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    ENV = os.getenv('FLASK_ENV', 'development') 