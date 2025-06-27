"""DeepSeek AI 配置流"""
from __future__ import annotations
import logging
import re
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_API_BASE,
    CONF_TEMPERATURE,
    CONF_MAX_TOKENS,
    DEFAULT_API_BASE,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS
)

_LOGGER = logging.getLogger(__name__)

# API 密钥验证正则
API_KEY_REGEX = re.compile(r"^[a-zA-Z0-9]{32}$")

# 配置步骤数据结构
CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): str,
    vol.Optional(CONF_API_BASE, default=DEFAULT_API_BASE): str,
    vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): cv.small_float,
    vol.Optional(CONF_MAX_TOKENS, default=DEFAULT_MAX_TOKENS): cv.positive_int,
})

class DeepSeekAIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理 DeepSeek AI 配置流"""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """处理用户初始步骤"""
        errors = {}
        
        if user_input is not None:
            # 验证 API 密钥格式
            api_key = user_input[CONF_API_KEY]
            api_base = user_input[CONF_API_BASE]
            
            # 1. 格式验证
            if not API_KEY_REGEX.match(api_key):
                errors[CONF_API_KEY] = "invalid_api_key_format"
            # 2. API 连通性验证
            elif not await self._test_api_endpoint(api_base, api_key):
                errors["base"] = "connection_failed"
            else:
                # 创建唯一ID
                await self.async_set_unique_id(api_key[:6])
                self._abort_if_unique_id_configured()
                
                # 创建配置项
                return self.async_create_entry(
                    title="DeepSeek AI",
                    data=user_input
                )
        
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors,
            description_placeholders={
                "api_key_format": "32位字母数字组合"
            }
        )
    
    async def _test_api_endpoint(self, api_base: str, api_key: str) -> bool:
        """测试API端点连通性"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{api_base}/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10
                ) as response:
                    return response.status == 200
        except Exception:
            return False
    
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
        if user_input is not None:
            # 更新配置
            return self.async_create_entry(title="", data=user_input)
        
        # 显示当前配置值
        options_schema = vol.Schema({
            vol.Optional(
                CONF_TEMPERATURE,
                default=self.config_entry.data.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
            ): cv.small_float,
            vol.Optional(
                CONF_MAX_TOKENS,
                default=self.config_entry.data.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)
            ): cv.positive_int,
        })
        
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )