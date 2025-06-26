"""DeepSeek AI 智能中枢"""
import logging
import aiohttp
import asyncio
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    TEXT_COMPLETION_URL,
    HARDWARE_OPTIMIZATION,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_TOKENS
)

_LOGGER = logging.getLogger(__name__)

class DeepSeekBrain:
    """DeepSeek AI 智能中枢"""
    
    def __init__(self, hass: HomeAssistant, config: dict):
        self.hass = hass
        self.config = config
        self.session = async_get_clientsession(hass)
        self._health_check = None
        
        # 硬件优化参数
        self.concurrent_requests = HARDWARE_OPTIMIZATION["concurrent_requests"]
        self.max_retries = HARDWARE_OPTIMIZATION["max_retries"]
        self.backoff_factor = HARDWARE_OPTIMIZATION["backoff_factor"]
        
        # 请求信号量（限制并发请求）
        self.semaphore = asyncio.Semaphore(self.concurrent_requests)
    
    async def async_setup(self):
        """初始化设置"""
        # 设置健康检查
        self._health_check = async_track_time_interval(
            self.hass,
            self._perform_health_check,
            timedelta(minutes=30)
        
        _LOGGER.info("DeepSeek AI 智能中枢初始化完成")
    
    async def _perform_health_check(self, now=None):
        """执行健康检查"""
        try:
            response = await self.async_send_text("健康检查")
            if "健康" not in response:
                raise Exception("健康检查失败")
            _LOGGER.debug("健康检查成功")
        except Exception as e:
            _LOGGER.error("健康检查失败: %s", e)
    
    async def async_send_text(self, text: str) -> str:
        """发送文本请求（带重试机制）"""
        headers = {
            "Authorization": f"Bearer {self.config[CONF_API_KEY]}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.get(CONF_MODEL, "deepseek-chat"),
            "messages": [{"role": "user", "content": text}],
            "max_tokens": self.config.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)
        }
        
        timeout = aiohttp.ClientTimeout(total=self.config.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))
        
        # 带重试机制的请求
        for attempt in range(self.max_retries + 1):
            try:
                async with self.semaphore:
                    async with self.session.post(
                        TEXT_COMPLETION_URL,
                        headers=headers,
                        json=payload,
                        timeout=timeout
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(f"API error: {response.status} - {error_text}")
                        
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < self.max_retries:
                    wait_time = self.backoff_factor * (2 ** attempt)
                    _LOGGER.warning("请求失败，将在 %.1f 秒后重试 (尝试 %d/%d)",
                                    wait_time, attempt + 1, self.max_retries)
                    await asyncio.sleep(wait_time)
                else:
                    raise Exception(f"请求失败: {str(e)}")
    
    async def async_cleanup(self):
        """清理资源"""
        if self._health_check:
            self._health_check()
