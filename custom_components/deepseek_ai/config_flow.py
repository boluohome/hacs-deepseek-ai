"""DeepSeek AI 配置流 - 针对 HassOS 优化"""
import logging
import voluptuous as vol
import re

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_API_KEY, CONF_DISCOVER_INTERVAL, DEFAULT_DISCOVER_INTERVAL

_LOGGER = logging.getLogger(__name__)

# API 密钥验证正则
API_KEY_REGEX = re.compile(r"^[a-zA-Z0-9]{32}$")

# 配置步骤数据结构
CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): str,
    vol.Optional(
        CONF_DISCOVER_INTERVAL,
        default=DEFAULT_DISCOVER_INTERVAL
    ): cv.positive_int
})

class DeepSeekAIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理 DeepSeek AI 配置流"""
    
    VERSION = 1
    
    def __init__(self) -> None:
        """初始化配置流"""
        self._errors = {}
        self._user_input = {}
    
    async def async_step_user(self, user_input=None) -> FlowResult:
        """处理用户初始步骤"""
        self._errors = {}
        
        if user_input is not None:
            # 保存用户输入用于验证
            self._user_input = user_input
            
            # 验证 API 密钥格式
            api_key = user_input[CONF_API_KEY]
            if not API_KEY_REGEX.match(api_key):
                self._errors[CONF_API_KEY] = "invalid_api_key_format"
            else:
                # 验证 API 密钥有效性
                if await self._test_api_key(api_key):
                    # 创建配置项
                    return self.async_create_entry(
                        title="DeepSeek AI",
                        data=user_input
                    )
                else:
                    self._errors["base"] = "invalid_api_key"
        
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=self._errors,
            description_placeholders={
                "api_key_format": "32位字母数字组合"
            }
        )
    
    async def _test_api_key(self, api_key: str) -> bool:
        """测试 API 密钥有效性"""
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "测试连接"}],
            "max_tokens": 5
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        return False
                    else:
                        _LOGGER.warning(f"API 测试返回状态码: {response.status}")
                        return False
        except Exception as e:
            _LOGGER.error(f"测试 API 密钥时出错: {e}")
            return False
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """获取选项流"""
        return DeepSeekAIOptionsFlowHandler(config_entry)

class DeepSeekAIOptionsFlowHandler(config_entries.OptionsFlow):
    """处理 DeepSeek AI 选项更新"""
    
    def __init__(self, config_entry):
        self.config_entry = config_entry
    
    async def async_step_init(self, user_input=None):
        """管理选项"""
        errors = {}
        current_interval = self.config_entry.options.get(
            CONF_DISCOVER_INTERVAL,
            self.config_entry.data.get(
                CONF_DISCOVER_INTERVAL,
                DEFAULT_DISCOVER_INTERVAL
            )
        )
        
        if user_input is not None:
            # 验证并更新配置
            return self.async_create_entry(title="", data=user_input)
        
        # 显示当前配置值
        options_schema = vol.Schema({
            vol.Optional(
                CONF_DISCOVER_INTERVAL,
                default=current_interval
            ): cv.positive_int
        })
        
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors
        )