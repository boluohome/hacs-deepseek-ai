"""DeepSeek AI 配置流"""
from __future__ import annotations
import logging
import voluptuous as vol
import re

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_MODEL,
    CONF_MAX_TOKENS,
    CONF_TIMEOUT,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT
)

_LOGGER = logging.getLogger(__name__)

API_KEY_REGEX = re.compile(r"^[a-zA-Z0-9]{32}$")

CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): str,
    vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): str,
    vol.Optional(CONF_MAX_TOKENS, default=DEFAULT_MAX_TOKENS): cv.positive_int,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
})

class DeepSeekAIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理 DeepSeek AI 配置流"""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None) -> FlowResult:
        """处理用户初始步骤"""
        errors = {}
        
        if user_input is not None:
            # 验证 API 密钥格式
            if not API_KEY_REGEX.match(user_input[CONF_API_KEY]):
                errors[CONF_API_KEY] = "invalid_api_key_format"
            else:
                # 创建唯一ID（基于API密钥前6位）
                await self.async_set_unique_id(user_input[CONF_API_KEY][:6])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title="DeepSeek AI",
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
        return DeepSeekAIOptionsFlow(config_entry)

class DeepSeekAIOptionsFlow(config_entries.OptionsFlow):
    """处理 DeepSeek AI 选项更新"""
    
    def __init__(self, config_entry):
        self.config_entry = config_entry
    
    async def async_step_init(self, user_input=None):
        """管理选项"""
        errors = {}
        current_config = self.config_entry.data
        
        if user_input is not None:
            # 更新配置
            new_data = {**self.config_entry.data, **user_input}
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=new_data
            )
            return self.async_create_entry(title="", data={})
        
        options_schema = vol.Schema({
            vol.Optional(
                CONF_MODEL,
                default=current_config.get(CONF_MODEL, DEFAULT_MODEL)
            ): str,
            vol.Optional(
                CONF_MAX_TOKENS,
                default=current_config.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)
            ): cv.positive_int,
            vol.Optional(
                CONF_TIMEOUT,
                default=current_config.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
            ): cv.positive_int,
        })
        
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors
        )
