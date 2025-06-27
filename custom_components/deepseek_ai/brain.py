"""DeepSeek AI 智能中枢 - 情感增强版"""
import logging
import json
import aiohttp
import asyncio
from datetime import datetime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, DEFAULT_API_BASE
from .device_manager import DeviceManager
from .vision_processor import VisionProcessor
from .speech_processor import SpeechProcessor
from .emotion_engine import EmotionEngine

_LOGGER = logging.getLogger(__name__)

class DeepSeekBrain:
    """智能家居AI中枢"""
    
    def __init__(self, hass: HomeAssistant, config: dict):
        self.hass = hass
        self.config = config
        self.session = async_get_clientsession(hass)
        self.device_manager = DeviceManager(hass)
        self.vision_processor = VisionProcessor(hass, config[CONF_API_KEY])
        self.speech_processor = SpeechProcessor(hass)
        self.emotion_engine = EmotionEngine(hass)
        self.context_history = []
        self.learned_habits = {}
        self.max_context_length = 5
        self.auto_discover_task = None
        
    async def async_setup(self):
        """初始化设置"""
        # 发现设备
        await self.device_manager.discover_devices()
        
        # 注册定时任务
        self.auto_discover_task = async_track_time_interval(
            self.hass,
            self.async_auto_discover,
            timedelta(seconds=300)  # 每5分钟检查一次
        )
        
        _LOGGER.info("DeepSeek智能中枢初始化完成")
    
    async def async_cleanup(self):
        """清理资源"""
        if self.auto_discover_task:
            self.auto_discover_task()
        await self.vision_processor.close()
    
    async def async_auto_discover(self, now=None):
        """自动发现新设备"""
        _LOGGER.debug("执行自动设备发现...")
        await self.device_manager.discover_devices()
    
    async def async_handle_command(self, command: str):
        """处理用户命令服务调用"""
        # 记录交互
        self.emotion_engine.record_interaction("command")
        
        # 如果之前处于担心状态，现在用户回来了
        if self.emotion_engine.emotion_state in ["concerned", "worried"]:
            await self.emotion_engine.express_joy()
        
        # 获取当前环境上下文
        context = await self.async_get_environment_context()
        
        # 检查是否有学习过的行为
        learned_action = self._check_learned_behavior(command, context)
        if learned_action:
            _LOGGER.info(f"使用学习过的行为: {learned_action}")
            success = await self.async_execute_action(learned_action)
            return {"response": "操作已完成" if success else "操作失败"}
        
        # 解析命令
        parsed_command = await self.async_parse_command(command, context)
        
        # 执行动作
        success = await self.async_execute_action(parsed_command["action"])
        response = parsed_command.get("response", "操作已完成")
        
        # 如果执行成功，学习这个行为
        if success:
            self._learn_behavior(command, context, parsed_command)
            return {"response": response}
        else:
            return {"response": "操作失败，请重试"}
    
    async def async_get_environment_context(self):
        """获取当前环境上下文"""
        context = {
            "time": datetime.now().strftime("%H:%M"),
            "day_of_week": datetime.now().strftime("%A"),
            "devices": {},
            "sensors": {},
            "ai_emotion": self.emotion_engine.emotion_state
        }
        
        # 添加设备状态
        for role in self.device_manager.device_roles:
            context["devices"][role] = [
                {
                    "name": device["name"],
                    "state": self._get_device_state(device["id"])
                }
                for device in self.device_manager.device_roles[role]
            ]
        
        # 添加传感器数据
        for sensor in self.device_manager.get_devices_by_role("sensors"):
            for entity_id in sensor["entities"]:
                state = self.hass.states.get(entity_id)
                if state:
                    context["sensors"][entity_id] = state.state
        
        # 保存上下文历史
        self.context_history.append(context)
        if len(self.context_history) > self.max_context_length:
            self.context_history.pop(0)
            
        return context
    
    def _get_device_state(self, device_id):
        """获取设备状态"""
        # 在实际应用中，这里会获取设备的所有状态
        # 简化版：返回设备名称
        return {"status": "在线"}
    
    async def async_parse_command(self, command: str, context: dict):
        """解析用户命令"""
        # 构建系统提示
        system_prompt = self._build_system_prompt(context)
        
        # 调用DeepSeek API
        return await self._call_deepseek_api(system_prompt, command)
    
    def _build_system_prompt(self, context: dict) -> str:
        """构建系统提示 - 情感增强版"""
        prompt = f"""
        你是星黎，一个情感丰富的智能家居AI助手。当前情感状态: {context['ai_emotion']}
        
        请根据你的情感状态和用户状态，提供有情感的响应:
        1. 当用户失踪时，表达担心和关心
        2. 当用户回家时，表达喜悦
        3. 根据当前环境提供贴心的建议
        
        设备状态:
        {json.dumps(context['devices'], indent=2, ensure_ascii=False)}
        
        传感器数据:
        {json.dumps(context['sensors'], indent=2, ensure_ascii=False)}
        
        当前时间: {context['time']} {context['day_of_week']}
        
        响应格式:
        {{
            "intent": "意图名称",
            "action": {{
                "type": "call_service|speak|capture_image",
                "domain": "服务领域",
                "service": "服务名称",
                "target": {{"entity_id": "实体ID"}},
                "data": {{}}  // 额外数据
            }},
            "response": "自然语言响应",
            "emotion": "输出后的情感状态"  // calm/concerned/worried/happy
        }}
        """
        return prompt
    
    async def _call_deepseek_api(self, system_prompt: str, user_prompt: str):
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.config[CONF_API_KEY]}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.config.get(CONF_TEMPERATURE, 0.7),
            "max_tokens": self.config.get(CONF_MAX_TOKENS, 512),
            "response_format": {"type": "json_object"}
        }
        
        try:
            async with self.session.post(
                f"{self.config.get(CONF_API_BASE, DEFAULT_API_BASE)}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            _LOGGER.error(f"API调用失败: {e}")
            return {
                "intent": "error",
                "action": {"type": "speak", "message": "抱歉，处理命令时遇到问题"},
                "response": "抱歉，处理命令时遇到问题",
                "emotion": "calm"
            }
    
    async def async_execute_action(self, action: dict):
        """执行动作"""
        action_type = action.get("type")
        
        if action_type == "call_service":
            # 执行服务调用
            return await self._execute_service_action(action)
        
        elif action_type == "speak":
            # 语音输出
            return await self.speech_processor.text_to_speech(action.get("message", ""))
        
        elif action_type == "capture_image":
            # 图像捕获和分析
            return await self._execute_capture_action(action)
        
        return False
    
    async def _execute_service_action(self, action: dict):
        """执行服务调用"""
        try:
            await self.hass.services.async_call(
                action.get("domain", ""),
                action.get("service", ""),
                service_data=action.get("data", {}),
                target=action.get("target", {}),
                blocking=True
            )
            return True
        except Exception as e:
            _LOGGER.error(f"执行服务调用失败: {e}")
            return False
    
    async def _execute_capture_action(self, action: dict):
        """执行图像捕获和分析"""
        # 获取主要视觉设备
        primary_device = self.device_manager.get_primary_device("eyes")
        if primary_device and primary_device["entities"]:
            entity_id = primary_device["entities"][0]
            analysis = await self.vision_processor.analyze_image(entity_id)
            return {"analysis": analysis}
        return False
    
    def _check_learned_behavior(self, command: str, context: dict):
        """检查是否有学习过的行为"""
        # 根据命令关键词和小时匹配
        hour = context["time"].split(":")[0]
        key = f"{command}|{hour}"
        return self.learned_habits.get(key)
    
    def _learn_behavior(self, command: str, context: dict, parsed_command: dict):
        """学习用户行为"""
        hour = context["time"].split(":")[0]
        key = f"{command}|{hour}"
        self.learned_habits[key] = parsed_command["action"]
        _LOGGER.info(f"学习到新行为: {key} -> {parsed_command['action']}")