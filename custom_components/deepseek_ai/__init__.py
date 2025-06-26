"""DeepSeek AI 集成 - HassOS 优化版"""
from __future__ import annotations
import logging
import os
import asyncio
from datetime import timedelta
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry as dr, entity_registry as er
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.conversation import agent
from homeassistant.components.conversation.default_agent import DefaultAgent
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT

from .const import DOMAIN, CONF_API_KEY, CONF_DISCOVER_INTERVAL, DEFAULT_DISCOVER_INTERVAL
from .brain import DeepSeekBrain

_LOGGER = logging.getLogger(__name__)

# YAML 配置模式
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_DISCOVER_INTERVAL, default=DEFAULT_DISCOVER_INTERVAL): cv.positive_int
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """设置集成组件 - 处理 YAML 配置"""
    if DOMAIN not in config:
        return True
        
    conf = config[DOMAIN]
    api_key = conf.get(CONF_API_KEY)
    discover_interval = conf.get(CONF_DISCOVER_INTERVAL, DEFAULT_DISCOVER_INTERVAL)
    
    # 验证 API 密钥格式
    if not api_key or len(api_key) != 32:
        _LOGGER.error("无效的 API 密钥格式，必须是 32 位字符")
        return False
    
    # 检查是否已存在配置项
    if hass.config_entries.async_entries(DOMAIN):
        _LOGGER.info("集成已通过配置项设置，跳过旧式配置")
        return True
    
    # 初始化智能中枢
    deepseek_brain = DeepSeekBrain(hass, api_key)
    await deepseek_brain.async_setup()
    
    # 存储到 hass.data
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
        timedelta(seconds=discover_interval)
    
    # 覆盖默认的对话代理
    agent.async_set_agent(hass, deepseek_brain)
    
    _LOGGER.info("DeepSeek AI 集成通过 YAML 配置初始化完成")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """通过配置项设置集成"""
    config = entry.data
    api_key = config[CONF_API_KEY]
    discover_interval = config.get(CONF_DISCOVER_INTERVAL, DEFAULT_DISCOVER_INTERVAL)
    
    # 初始化智能中枢
    deepseek_brain = DeepSeekBrain(hass, api_key)
    await deepseek_brain.async_setup()
    
    # 存储到 hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = deepseek_brain
    
    # 注册服务
    hass.services.async_register(
        DOMAIN, 
        "execute_command", 
        deepseek_brain.async_handle_command
    )
    
    # 注册定时任务
    deepseek_brain.discovery_listener = async_track_time_interval(
        hass,
        deepseek_brain.async_auto_discover,
        timedelta(seconds=discover_interval))
    
    # 覆盖默认的对话代理
    agent.async_set_agent(hass, deepseek_brain)
    
    _LOGGER.info("DeepSeek AI 集成通过配置项初始化完成")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载集成"""
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        deepseek_brain = hass.data[DOMAIN][entry.entry_id]
        
        # 停止定时任务
        if hasattr(deepseek_brain, "discovery_listener"):
            deepseek_brain.discovery_listener()
        
        # 从数据存储中移除
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # 如果这是最后一个实例，移除整个DOMAIN
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    
    # 恢复默认对话代理
    agent.async_set_agent(hass, DefaultAgent(hass))
    
    _LOGGER.info("DeepSeek AI 集成已卸载")
    return True