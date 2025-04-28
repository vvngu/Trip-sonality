# Trip-sonality Backend API

## 项目简介

Trip-sonality Backend是一个基于FastAPI的后端服务，提供个性化的Solo Trip电影主题旅行灵感推荐。该服务接收用户的MBTI人格类型和电影名称/主题，结合外部API (TMDb, Geoapify)和大型语言模型(OpenAI)，生成符合用户个性的旅行建议。

## 核心功能

- 基于MBTI类型分析用户旅行偏好
- 电影信息检索与解析
- 提取电影中的潜在旅行目的地和主题
- 搜索与目的地相关的兴趣点(POI)
- 生成个性化的电影主题旅行方案

## 技术栈

- **后端框架**: FastAPI (Python)
- **ASGI服务器**: Uvicorn
- **HTTP请求**: requests
- **配置管理**: python-dotenv
- **数据验证**: pydantic
- **API集成**:
  - TMDb API - 电影数据
  - Geoapify Places API - 地点搜索
  - OpenAI API - LLM生成与推理

## 安装与设置

### 前提条件

- Python 3.8+
- TMDb API密钥
- Geoapify API密钥
- OpenAI API密钥

### 安装步骤

1. 克隆仓库
   ```bash
   git clone <repository-url>
   cd Trip-sonality/backend
   ```

2. 创建并激活虚拟环境
   ```bash
   python -m venv venv
   source venv/bin/activate  # 在Windows上使用 venv\Scripts\activate
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量
   ```bash
   cp .env.example .env
   ```
   编辑`.env`文件，填入所需API密钥

## 运行服务

启动开发服务器:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

服务将在 http://localhost:5000 运行

## API文档

FastAPI自动生成交互式API文档：

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## API端点

### 获取旅行推荐

**请求**:
```http
POST /api/v1/recommendations
Content-Type: application/json

{
  "mbti_type": "INTJ",
  "movie_input": "盗梦空间"
}
```

**响应**:
```json
{
  "recommendation": {
    "title": "推荐标题",
    "movie_title": "电影标题",
    "movie_overview": "电影简介",
    "theme": "旅行主题",
    "destination": "目的地",
    "description": "旅行描述",
    "places_of_interest": [
      {
        "name": "景点名称",
        "description": "景点描述",
        "relation_to_movie": "与电影的关联",
        "category": "景点类型"
      }
    ],
    "activities": [
      {
        "title": "活动标题",
        "description": "活动描述",
        "relation_to_movie": "与电影的关联",
        "relation_to_mbti": "与MBTI类型的关联",
        "time_of_day": "建议时间"
      }
    ],
    "mbti_relevance": "MBTI相关性说明"
  },
  "movie_info": {
    "id": 电影ID,
    "title": "电影标题",
    "overview": "电影简介",
    "release_date": "发行日期",
    "poster_path": "海报路径",
    "backdrop_path": "背景图路径"
  },
  "mbti_type": "INTJ"
}
```

### 健康检查

**请求**:
```http
GET /api/v1/health
```

**响应**:
```json
{
  "status": "healthy",
  "message": "服务正常运行"
}
```

## 项目结构

```
backend/
├── main.py                   # FastAPI应用入口
├── config.py                 # 配置管理
├── requirements.txt          # Python依赖
├── .env.example              # 环境变量示例
├── constants/                # 常量定义
├── routers/                  # API路由
├── services/                 # 业务逻辑
├── clients/                  # 外部API客户端
├── llm/                      # LLM集成
├── utils/                    # 辅助工具
└── models/                   # 数据模型
```

## 开发与贡献

项目遵循以下开发实践:
- 模块化设计
- 异常处理
- API文档
- 类型提示

## 问题与支持

如有问题或需要支持，请提交Issue。 