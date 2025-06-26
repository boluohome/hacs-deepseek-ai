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
    ): int
})

class DeepSeekConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理 DeepSeek 配置流"""
    
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_PUSH
    
    async def async_step_user(self, user_input=None):
        """处理用户初始步骤"""
        errors = {}
        
        if user_input is not None:
            # 验证 API 密钥格式
            if len(user_input[CONF_DEEPSEEK_API_KEY]) != 32:
                errors[CONF_DEEPSEEK_API_KEY] = "invalid_api_key_format"
            else:
                # 创建配置项
                return self.async_create_entry(
                    title="DeepSeek Integration",
                    data=user_input
                )
        
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """获取选项流"""
        return DeepSeekOptionsFlowHandler(config_entry)

class DeepSeekOptionsFlowHandler(config_entries.OptionsFlow):
    """处理 DeepSeek 选项更新"""
    
    def __init__(self, config_entry):
        """初始化选项流"""
        self.config_entry = config_entry
    
    async def async_step_init(self, user_input=None):
        """管理选项"""
        errors = {}
        
        if user_input is not None:
            # 验证并更新配置
            return self.async_create_entry(title="", data=user_input)
        
        # 显示当前配置值
        options_schema = vol.Schema({
            vol.Optional(
                CONF_AUTO_DISCOVER_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_AUTO_DISCOVER_INTERVAL,
                    self.config_entry.data.get(
                        CONF_AUTO_DISCOVER_INTERVAL,
                        DEFAULT_AUTO_DISCOVER_INTERVAL
                    )
                )
            ): int
        })
        
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors
        )
