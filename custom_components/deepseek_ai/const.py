"""DeepSeek AI 集成常量"""
DOMAIN = "deepseek_ai"
DEFAULT_NAME = "DeepSeek AI"

# 配置项
CONF_API_KEY = "api_key"
CONF_MODEL = "model"
CONF_MAX_TOKENS = "max_tokens"
CONF_TIMEOUT = "timeout"

# 默认值
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_MAX_TOKENS = 150
DEFAULT_TIMEOUT = 15

# API 端点
TEXT_COMPLETION_URL = "https://api.deepseek.com/v1/chat/completions"
SPEECH_TO_TEXT_URL = "https://api.deepseek.com/v1/audio/transcriptions"  # 假设DeepSeek支持类似API

# 硬件特定参数（s905l3_bigfs）
HARDWARE_OPTIMIZATION = {
    "concurrent_requests": 1,
    "max_retries": 2,
    "backoff_factor": 0.5
}
