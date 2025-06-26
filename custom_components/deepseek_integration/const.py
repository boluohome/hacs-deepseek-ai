"""常量定义"""
DOMAIN = "deepseek_integration"
DEFAULT_NAME = "DeepSeek"

# 配置项
CONF_DEEPSEEK_API_KEY = "deepseek_api_key"
CONF_AUTO_DISCOVER_INTERVAL = "auto_discover_interval"
CONF_LEARNING_MODE = "learning_mode"

# 默认值
DEFAULT_AUTO_DISCOVER_INTERVAL = 3600  # 1小时
DEFAULT_LEARNING_MODE = "adaptive"

# 设备角色
ROLE_EYES = "eyes"
ROLE_EARS = "ears"
ROLE_MOUTH = "mouth"
ROLE_HANDS = "hands"
ROLE_SENSORS = "sensors"

# 服务
SERVICE_EXECUTE_COMMAND = "execute_command"