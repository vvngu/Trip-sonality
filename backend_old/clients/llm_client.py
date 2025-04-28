import openai
from typing import Dict, List, Any, Optional
from config import Config
from utils.error_handlers import LlmProcessingError

class LLMClient:
    """LLM API客户端类"""
    
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.model = Config.LLM_MODEL
        
        if not self.api_key:
            raise ValueError("缺少OpenAI API密钥。请在.env文件中设置OPENAI_API_KEY。")
        
        # 设置OpenAI客户端
        openai.api_key = self.api_key
    
    def call_llm(
        self, 
        prompt: str, 
        temperature: float = None, 
        max_tokens: int = None,
        stream: bool = False
    ) -> str:
        """
        调用LLM API生成文本
        
        Args:
            prompt: 输入提示
            temperature: 温度参数(控制随机性)
            max_tokens: 最大生成token数
            stream: 是否流式输出
            
        Returns:
            生成的文本
            
        Raises:
            LlmProcessingError: LLM处理失败时
        """
        if temperature is None:
            temperature = Config.LLM_TEMPERATURE
            
        if max_tokens is None:
            max_tokens = Config.LLM_MAX_TOKENS
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                # 处理流式响应
                collected_content = []
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.get("content"):
                        collected_content.append(chunk.choices[0].delta.content)
                return "".join(collected_content)
            else:
                # 处理非流式响应
                return response.choices[0].message.content
                
        except openai.OpenAIError as e:
            error_message = str(e)
            
            if "rate limit" in error_message.lower():
                raise LlmProcessingError(
                    message="LLM API速率限制",
                    details="已超过API调用速率限制，请稍后再试",
                    status_code=429
                )
            elif "authentication" in error_message.lower():
                raise LlmProcessingError(
                    message="LLM API认证失败",
                    details="API密钥无效或已过期",
                    status_code=401
                )
            elif "content filter" in error_message.lower():
                raise LlmProcessingError(
                    message="内容被LLM内容过滤器拦截",
                    details="请求或响应内容可能违反内容政策",
                    status_code=400
                )
            else:
                raise LlmProcessingError(
                    message="LLM API调用失败",
                    details=error_message
                )
    
    def extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        从LLM响应中提取JSON对象
        
        Args:
            response: LLM生成的文本
            
        Returns:
            提取的JSON对象
            
        Raises:
            LlmProcessingError: 解析失败时
        """
        import json
        import re
        
        # 尝试找到被```json和```包围的JSON内容
        json_pattern = r"```(?:json)?\s*([\s\S]*?)```"
        matches = re.findall(json_pattern, response)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # 尝试直接解析整个响应
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果上述方法都失败，尝试找到{和}包围的最大文本块并解析
            try:
                text = response.strip()
                start_idx = text.find('{')
                end_idx = text.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = text[start_idx:end_idx+1]
                    return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                pass
            
            raise LlmProcessingError(
                message="无法解析LLM响应为JSON",
                details="LLM生成的响应不是有效的JSON格式"
            ) 