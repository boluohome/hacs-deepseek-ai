"""DeepSeek 语音转文本组件"""
import logging
import aiohttp
import asyncio

from homeassistant.components.stt import (
    AudioCodec,
    SpeechMetadata,
    SpeechResult,
    SpeechToTextEntity,
    async_get_engine_instance
)

from .const import DOMAIN, SPEECH_TO_TEXT_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_stt(hass, entry, brain):
    """设置语音转文本组件"""
    engine = async_get_engine_instance(hass)
    if engine:
        engine.async_register_entity(DeepSeekSTTEntity(hass, entry, brain))
        return True
    return False

class DeepSeekSTTEntity(SpeechToTextEntity):
    """DeepSeek 语音转文本实体"""
    
    def __init__(self, hass, entry, brain):
        self.hass = hass
        self._entry = entry
        self._brain = brain
        self._attr_name = "DeepSeek STT"
        self._attr_unique_id = f"{entry.entry_id}-stt"
    
    @property
    def supported_languages(self):
        """支持的语言列表"""
        return ["zh", "en"]
    
    @property
    def supported_codecs(self):
        """支持的音频编码"""
        return [AudioCodec.WAV, AudioCodec.OGG]
    
    @property
    def supported_bit_rates(self):
        """支持的比特率"""
        return [16000, 44100]
    
    @property
    def supported_channels(self):
        """支持的声道数"""
        return [1]  # 单声道
    
    @property
    def supported_formats(self):
        """支持的音频格式"""
        return ["wav", "ogg"]
    
    async def async_process_audio_stream(self, metadata: SpeechMetadata, stream):
        """处理音频流"""
        try:
            # 收集音频数据
            audio_data = b""
            async for chunk in stream:
                audio_data += chunk
            
            # 调用 DeepSeek API
            headers = {
                "Authorization": f"Bearer {self._brain.config[CONF_API_KEY]}",
            }
            
            data = aiohttp.FormData()
            data.add_field("file", audio_data, filename="audio.wav", content_type="audio/wav")
            data.add_field("model", "whisper-1")  # 假设DeepSeek支持类似API
            
            async with self._brain.session.post(
                SPEECH_TO_TEXT_URL,
                headers=headers,
                data=data,
                timeout=self._brain.config.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    _LOGGER.error("STT API error: %s - %s", response.status, error_text)
                    return SpeechResult("", SpeechResult.ResultState.ERROR)
                
                result = await response.json()
                return SpeechResult(result.get("text", ""), SpeechResult.ResultState.SUCCESS)
        
        except Exception as e:
            _LOGGER.error("处理音频流时出错: %s", e)
            return SpeechResult("", SpeechResult.ResultState.ERROR)
