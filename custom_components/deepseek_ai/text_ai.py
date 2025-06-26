"""DeepSeek 文本处理组件"""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.components.conversation import agent

from .const import DOMAIN
from .brain import DeepSeekBrain

_LOGGER = logging.getLogger(__name__)

SERVICE_PROCESS_TEXT = "process_text"
SERVICE_SCHEMA = cv.make_entity_service_schema({
    vol.Required("text"): cv.string,
})

async def async_setup_text_ai(hass: HomeAssistant, brain: DeepSeekBrain):
    """设置文本处理组件"""
    # 注册服务
    async def async_process_text(call):
        """处理文本服务调用"""
        text = call.data.get("text")
        return await brain.async_send_text(text)
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_PROCESS_TEXT,
        async_process_text,
        schema=SERVICE_SCHEMA
    )
    
    # 注册对话代理
    class DeepSeekConversationAgent(agent.AbstractConversationAgent):
        """DeepSeek 对话代理"""
        @property
        def supported_languages(self):
            """支持的语言列表"""
            return ["zh", "en"]
        
        async def async_process(self, user_input: agent.ConversationInput) -> agent.ConversationResult:
            """处理对话输入"""
            try:
                response = await brain.async_send_text(user_input.text)
                return agent.ConversationResult(
                    response=response,
                    conversation_id=user_input.conversation_id
                )
            except Exception as e:
                _LOGGER.error("处理对话时出错: %s", e)
                return agent.ConversationResult(
                    response="抱歉，处理请求时出错",
                    conversation_id=user_input.conversation_id
                )
    
    agent.async_set_agent(hass, DeepSeekConversationAgent())
    _LOGGER.info("DeepSeek 对话代理已注册")
    
    return True
