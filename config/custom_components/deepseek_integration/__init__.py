"""DeepSeek 智能家居集成"""
from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.conversation import agent
from homeassistant.components.conversation.default_agent import DefaultAgent
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT

from .const import DOMAIN, CONF_DEEPSEEK_API_KEY, CONF_AUTO_DISCOVER_INTERVAL, DEFAULT_AUTO_DISCOVER_INTERVAL
from .brain import DeepSeekBrain
from .config_flow import DeepseekIntegrationConfigFlow

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """设置集成组件 - 处理旧式配置"""
    if DOMAIN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=config[DOMAIN],
            )
        )
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """通过配置项设置集成"""
    # 从配置项获取设置
    api_key = entry.data[CONF_DEEPSEEK_API_KEY]
    auto_discover_interval = entry.data.get(
        CONF_AUTO_DISCOVER_INTERVAL, 
        DEFAULT_AUTO_DISCOVER_INTERVAL
    )
    
    # 初始化智能中枢
    deepseek_brain = DeepSeekBrain(hass, api_key)
    await deepseek_brain.async_setup()
    
    # 存储到hass.data
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
        timedelta(seconds=auto_discover_interval)
    )
    
    # 覆盖默认的对话代理
    agent.async_set_agent(hass, deepseek_brain)
    
    # 设置更新监听
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    _LOGGER.info("DeepSeek集成初始化完成")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载集成"""
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        deepseek_brain = hass.data[DOMAIN][entry.entry_id]
        
        # 停止定时任务
        if deepseek_brain.discovery_listener:
            deepseek_brain.discovery_listener()
        
        # 从数据存储中移除
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # 如果这是最后一个实例，移除整个DOMAIN
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    
    # 恢复默认对话代理
    agent.async_set_agent(hass, DefaultAgent(hass))
    
    _LOGGER.info("DeepSeek集成已卸载")
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """配置项更新时处理"""
    await hass.config_entries.async_reload(entry.entry_id)