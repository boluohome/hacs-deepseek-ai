"""DeepSeek 智能家居集成"""
from __future__ import annotations
import logging
import re
import json
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.conversation import agent
from homeassistant.components.conversation.default_agent import DefaultAgent
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_DEEPSEEK_API_KEY, CONF_AUTO_DISCOVER_INTERVAL, DEFAULT_AUTO_DISCOVER_INTERVAL
from .brain import DeepSeekBrain

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """设置集成组件"""
    if DOMAIN in config:
        conf = config[DOMAIN]
        api_key = conf.get(CONF_DEEPSEEK_API_KEY)
        auto_discover_interval = conf.get(CONF_AUTO_DISCOVER_INTERVAL, DEFAULT_AUTO_DISCOVER_INTERVAL)
        
        # 初始化智能中枢
        deepseek_brain = DeepSeekBrain(hass, api_key)
        await deepseek_brain.async_setup()
        
        # 存储到hass.data
        hass.data[DOMAIN] = deepseek_brain
        
        # 注册服务
        hass.services.async_register(
            DOMAIN, 
            "execute_command", 
            deepseek_brain.async_handle_command
        )
        
        # 注册定时任务
        async_track_time_interval(
            hass,
            deepseek_brain.async_auto_discover,
            timedelta(seconds=auto_discover_interval)
        )
        
        # 覆盖默认的对话代理
        agent.async_set_agent(hass, deepseek_brain)
        
        _LOGGER.info("DeepSeek集成初始化完成")
        return True
    
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry):
    """通过配置项设置集成"""
    config = config_entry.data
    api_key = config[CONF_DEEPSEEK_API_KEY]
    auto_discover_interval = config.get(CONF_AUTO_DISCOVER_INTERVAL, DEFAULT_AUTO_DISCOVER_INTERVAL)
    
    # 初始化智能中枢
    deepseek_brain = DeepSeekBrain(hass, api_key)
    await deepseek_brain.async_setup()
    
    # 存储到hass.data
    hass.data[DOMAIN] = deepseek_brain
    
    # 注册服务
    hass.services.async_register(
        DOMAIN, 
        "execute_command", 
        deepseek_brain.async_handle_command
    )
    
    # 注册定时任务
    async_track_time_interval(
        hass,
        deepseek_brain.async_auto_discover,
        timedelta(seconds=auto_discover_interval)
    )
    
    # 覆盖默认的对话代理
    agent.async_set_agent(hass, deepseek_brain)
    
    _LOGGER.info("DeepSeek集成通过配置项初始化完成")
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry):
    """卸载集成"""
    if DOMAIN in hass.data:
        del hass.data[DOMAIN]
    
    # 恢复默认对话代理
    agent.async_set_agent(hass, DefaultAgent(hass))
    
    _LOGGER.info("DeepSeek集成已卸载")
    return True
