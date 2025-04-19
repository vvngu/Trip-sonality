from flask import jsonify

# 自定义异常类
class BaseAppError(Exception):
    """应用基础异常类"""
    status_code = 500
    error_code = "internal_error"
    message = "服务器内部错误"
    
    def __init__(self, message=None, status_code=None, error_code=None, details=None):
        super().__init__(message or self.message)
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code
        self.details = details
        
    def to_dict(self):
        error_dict = {
            "error": self.error_code,
            "message": self.message,
        }
        if self.details:
            error_dict["details"] = self.details
        return error_dict


class ExternalApiError(BaseAppError):
    """外部API调用异常"""
    status_code = 502
    error_code = "external_api_error"
    message = "外部API调用失败"


class LlmProcessingError(BaseAppError):
    """LLM处理异常"""
    status_code = 500
    error_code = "llm_processing_error"
    message = "语言模型处理失败"


class ValidationError(BaseAppError):
    """输入验证异常"""
    status_code = 400
    error_code = "validation_error"
    message = "输入参数无效"


class NotFoundError(BaseAppError):
    """资源未找到异常"""
    status_code = 404
    error_code = "not_found"
    message = "请求的资源未找到"


# Flask错误处理器
def register_error_handlers(app):
    """注册Flask应用的错误处理器"""
    
    # 自定义异常处理
    @app.errorhandler(BaseAppError)
    def handle_base_app_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    # 400处理
    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({
            "error": "bad_request",
            "message": "请求格式无效"
        }), 400
    
    # 404处理
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            "error": "not_found",
            "message": "请求的资源不存在"
        }), 404
    
    # 405处理
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            "error": "method_not_allowed",
            "message": "请求方法不允许"
        }), 405
    
    # 500处理
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        return jsonify({
            "error": "internal_server_error",
            "message": "服务器内部错误"
        }), 500 