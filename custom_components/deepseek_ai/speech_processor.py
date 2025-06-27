"""语音处理器 - 处理语音输入/输出"""
import logging
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class SpeechProcessor:
    """处理语音输入和输出"""
    
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
    
    async def text_to_speech(self, text: str):
        """文本转语音并通过指定设备播放"""
        # 查找语音输出设备
        if DOMAIN in self.hass.data:
            device_manager = self.hass.data[DOMAIN].get("device_manager")
            if device_manager:
                device = device_manager.get_primary_device("mouth")
                if device and device["entities"]:
                    entity_id = device["entities"][0]
                    
                    # 调用TTS服务
                    await self.hass.services.async_call(
                        "tts", 
                        "xiaomi_miot_say", 
                        {
                            "entity_id": entity_id,
                            "message": text
                        },
                        blocking=True
                    )
                    return True
        
        _LOGGER.warning("未找到语音输出设备")
        return False