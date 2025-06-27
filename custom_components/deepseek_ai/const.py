"""DeepSeek AI 集成常量"""
DOMAIN = "deepseek_ai"

# 配置项
CONF_API_KEY = "api_key"
CONF_API_BASE = "api_base"
CONF_TEMPERATURE = "temperature"
CONF_MAX_TOKENS = "max_tokens"
CONF_VISION_ENABLED = "vision_enabled"
CONF_SPEECH_ENABLED = "speech_enabled"

# 默认值
DEFAULT_API_BASE = "https://api.deepseek.com/v1"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 512

# 设备角色
ROLE_EYES = "eyes"
ROLE_EARS = "ears"
ROLE_MOUTH = "mouth"
ROLE_HANDS = "hands"
ROLE_SENSORS = "sensors"

# 设备类型映射
DEVICE_ROLE_MAPPING = {
    "camera": ROLE_EYES,
    "binary_sensor.motion": ROLE_EYES,
    "binary_sensor.sound": ROLE_EARS,
    "media_player": ROLE_MOUTH,
    "switch": ROLE_HANDS,
    "light": ROLE_HANDS,
    "cover": ROLE_HANDS,
    "climate": ROLE_HANDS,
    "sensor": ROLE_SENSORS
}

# 情感状态
EMOTION_CALM = "calm"
EMOTION_CONCERNED = "concerned"
EMOTION_WORRIED = "worried"
EMOTION_HAPPY = "happy"