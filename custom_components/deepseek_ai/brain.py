"""DeepSeek AI 智能中枢"""
import logging
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.components.conversation.default_agent import DefaultAgent
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_API_KEY, API_ENDPOINT

_LOGGER = logging.getLogger(__name__)

class DeepSeekBrain(DefaultAgent):
    """DeepSeek AI 智能中枢"""
    
    def __init__(self, hass: HomeAssistant, api_key: str):
        super().__init__(hass)
        self.hass = hass
        self.api_key = api_key
        self.session = async_get_clientsession(hass)
        self.discovery_listener = None
    
    async def async_setup(self):
        """初始化设置"""
        _LOGGER.info("DeepSeek AI 智能中枢初始化完成")
    
    async def async_handle_command(self, call):
        """处理用户命令服务调用"""
        command = call.data.get("command", "")
        _LOGGER.info(f"收到命令: {command}")
        
        try:
            # 调用 DeepSeek API
            response = await self._call_deepseek_api(command)
            return {"response": response}
        except Exception as e:
            _LOGGER.error(f"处理命令时出错: {e}")
            return {"response": "处理命令时出错，请检查日志"}
    
    async def _call_deepseek_api(self, command: str):
        """调用 DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": command}]
        }
        
        async with self.session.post(
            API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                _LOGGER.error(f"API 请求失败: {response.status} - {error_text}")
                return "API 请求失败，请检查API密钥和网络连接"
            
            data = await response.json()
            return data["choices"][0]["message"]["content"]
    
    async def async_auto_discover(self, now=None):
        """自动发现设备（简化）"""
        _LOGGER.debug("执行自动设备发现...")
        
    async def async_process(self, user_input):
        """处理对话输入"""
        try:
            response = await self._call_deepseek_api(user_input.text)
            return agent.ConversationResult(
                response=response,
                conversation_id=user_input.conversation_id
            )
        except Exception as e:
            _LOGGER.error(f"处理对话时出错: {e}")
            return agent.ConversationResult(
                response="处理请求时出错",
                conversation_id=user_input.conversation_id
            )