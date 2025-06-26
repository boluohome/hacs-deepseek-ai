"""DeepSeek 集成常量"""
DOMAIN = "deepseek_integration"

# 配置键
CONF_DEEPSEEK_API_KEY = "api_key"
CONF_AUTO_DISCOVER_INTERVAL = "auto_discover_interval"
DEFAULT_AUTO_DISCOVER_INTERVAL = 300  # 5分钟

# 设备角色
ROLE_EYES = "eyes"       # 摄像头/视觉设备
ROLE_EARS = "ears"       # 麦克风/音频输入设备
ROLE_MOUTH = "mouth"     # 扬声器/音频输出设备
ROLE_HANDS = "hands"     # 执行器/开关设备
ROLE_SENSORS = "sensors" # 传感器设备
