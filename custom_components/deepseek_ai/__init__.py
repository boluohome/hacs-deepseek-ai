"""DeepSeek AI 集成主模块"""
import logging
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .brain import DeepSeekBrain
from .text_ai import async_setup_text_ai
from .stt import async_setup_stt

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置集成条目"""
    # 初始化智能中枢
    brain = DeepSeekBrain(hass, entry.data)
    await brain.async_setup()
    
    # 存储到hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = brain
    
    # 设置文本处理组件
    await async_setup_text_ai(hass, brain)
    
    # 设置语音转文本组件（可选）
    try:
        await async_setup_stt(hass, entry, brain)
    except Exception as e:
        _LOGGER.warning("无法设置语音转文本组件: %s", e)
    
    # 设置清理回调
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    entry.async_on_unload(brain.async_cleanup)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载集成条目"""
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        brain = hass.data[DOMAIN][entry.entry_id]
        await brain.async_cleanup()
        hass.data[DOMAIN].pop(entry.entry_id)
        
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """更新配置选项"""
    await hass.config_entries.async_reload(entry.entry_id)
