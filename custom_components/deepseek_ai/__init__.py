"""DeepSeek AI 集成主模块"""
import logging
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .brain import DeepSeekBrain
from .presence_detector import PresenceDetector

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """设置集成组件 (旧式配置)"""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """通过配置项设置集成"""
    # 初始化智能中枢
    brain = DeepSeekBrain(hass, entry.data)
    await brain.async_setup()
    
    # 初始化存在检测器
    presence_detector = PresenceDetector(hass, brain)
    await presence_detector.async_setup()
    
    # 存储到hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "brain": brain,
        "presence_detector": presence_detector
    }
    
    # 注册服务
    async def handle_command(call):
        """处理命令服务调用"""
        command = call.data.get("command", "")
        return await brain.async_handle_command(command)
    
    hass.services.async_register(
        DOMAIN, 
        "execute_command", 
        handle_command
    )
    
    async def express_concern(call):
        """表达关心服务"""
        reason = call.data.get("reason", "long_time_no_detection")
        await brain.emotion_engine.express_concern(reason)
    
    hass.services.async_register(
        DOMAIN,
        "express_concern",
        express_concern
    )
    
    async def speak_message(call):
        """语音消息服务"""
        message = call.data.get("message", "")
        await brain.speech_processor.text_to_speech(message)
    
    hass.services.async_register(
        DOMAIN,
        "speak_message",
        speak_message
    )
    
    # 注册对话代理
    if "conversation" in hass.config.components:
        from homeassistant.components.conversation import agent
        
        class DeepSeekConversationAgent(agent.AbstractConversationAgent):
            async def async_process(self, user_input):
                result = await brain.async_handle_command(user_input.text)
                return agent.ConversationResult(
                    response=result.get("response", "操作已完成"),
                    conversation_id=user_input.conversation_id
                )
        
        agent.async_set_agent(hass, DeepSeekConversationAgent())
        _LOGGER.info("DeepSeek对话代理已注册")
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载集成"""
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        components = hass.data[DOMAIN][entry.entry_id]
        
        # 清理资源
        await components["brain"].async_cleanup()
        await components["presence_detector"].async_cleanup()
        
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return True