"""DeepSeek 配置流"""
from __future__ import annotations
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_DEEPSEEK_API_KEY,
    CONF_AUTO_DISCOVER_INTERVAL,
    DEFAULT_AUTO_DISCOVER_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_DEEPSEEK_API_KEY): str,
    vol.Optional(
        CONF_AUTO_DISCOVER_INTERVAL,
        default=DEFAULT_AUTO_DISCOVER_INTERVAL
    ): cv.positive_int
})

class DeepseekIntegrationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理 DeepSeek 配置流"""
    
    VERSION = 1
    
    def __init__(self) -> None:
        """初始化配置流"""
        self._errors = {}
    
    async def async_step_user(self, user_input=None) -> FlowResult:
        """处理用户初始步骤"""
        self._errors = {}
        
        if user_input is not None:
            # 验证 API 密钥格式
            api_key = user_input[CONF_DEEPSEEK_API_KEY]
            if len(api_key) != 32 or not api_key.isalnum():
                self._errors[CONF_DEEPSEEK_API_KEY] = "invalid_api_key_format"
            else:
                # 创建配置项
                return self.async_create_entry(
                    title="DeepSeek AI 集成",
                    data=user_input
                )
        
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=self._errors
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry
    ) -> config_entries.OptionsFlow:
        """获取选项流"""
        return DeepseekIntegrationOptionsFlowHandler(config_entry)

class DeepseekIntegrationOptionsFlowHandler(config_entries.OptionsFlow):
    """处理 DeepSeek 选项更新"""
    
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """初始化选项流"""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
    
    async def async_step_init(self, user_input=None) -> FlowResult:
        """管理选项"""
        if user_input is not None:
            # 保存选项
            self.options.update(user_input)
            return self.async_create_entry(title="", data=self.options)
        
        # 显示当前配置值
        current_interval = self.config_entry.options.get(
            CONF_AUTO_DISCOVER_INTERVAL,
            self.config_entry.data.get(
                CONF_AUTO_DISCOVER_INTERVAL,
                DEFAULT_AUTO_DISCOVER_INTERVAL
            )
        )
        
        options_schema = vol.Schema({
            vol.Optional(
                CONF_AUTO_DISCOVER_INTERVAL,
                default=current_interval
            ): cv.positive_int
        })
        
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )
