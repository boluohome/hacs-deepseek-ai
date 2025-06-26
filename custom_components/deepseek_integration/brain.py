"""DeepSeek 智能中枢实现"""
import logging
import re
import json
from datetime import datetime, timedelta
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.components.conversation.default_agent import DefaultAgent
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN, 
    ROLE_EYES, 
    ROLE_EARS, 
    ROLE_MOUTH, 
    ROLE_HANDS, 
    ROLE_SENSORS,
    SERVICE_EXECUTE_COMMAND
)
from .device_classifier import IntelligentDeviceClassifier

_LOGGER = logging.getLogger(__name__)

class DeepSeekBrain(DefaultAgent):
    """DeepSeek 智能中枢"""
    
    def __init__(self, hass: HomeAssistant, api_key: str):
        super().__init__(hass)
        self.hass = hass
        self.api_key = api_key
        self.device_roles = {
            ROLE_EYES: [],
            ROLE_EARS: [],
            ROLE_MOUTH: [],
            ROLE_HANDS: [],
            ROLE_SENSORS: []
        }
        self.learned_habits = {}
        self.context_history = []
        self.device_classifier = IntelligentDeviceClassifier()
        self.session = async_get_clientsession(hass)
    
    async def async_setup(self):
        """初始化设置"""
        await self.async_discover_and_configure()
        _LOGGER.info("DeepSeek智能中枢初始化完成")
    
    async def async_discover_and_configure(self):
        """自动发现设备并配置角色"""
        _LOGGER.info("开始自动发现设备并配置角色...")
        
        # 获取所有设备
        device_registry = dr.async_get(self.hass)
        entity_registry = er.async_get(self.hass)
        
        # 分类设备
        for device_entry in device_registry.devices.values():
            device_entities = er.async_entries_for_device(
                entity_registry, device_entry.id
            )
            
            # 分类设备
            await self._classify_device(device_entry, device_entities)
        
        _LOGGER.info("设备配置完成")
        
    async def _classify_device(self, device_entry, entities):
        """根据设备实体分类设备角色"""
        # 使用分类器分类设备
        role = self.device_classifier.classify_device(device_entry, entities)
        
        if role:
            self.device_roles[role].append({
                "device_id": device_entry.id,
                "name": device_entry.name or device_entry.id,
                "manufacturer": device_entry.manufacturer or "Unknown",
                "model": device_entry.model or "Unknown",
                "entities": [e.entity_id for e in entities]
            })
            _LOGGER.debug(f"设备分类: {device_entry.name} -> {role}")
    
    async def async_auto_discover(self, now=None):
        """定时自动发现新设备"""
        _LOGGER.info("执行自动设备发现...")
        await self.async_discover_and_configure()
        
    async def async_handle_command(self, call):
        """处理用户命令服务调用"""
        command = call.data.get("command", "")
        return await self.async_process_command(command)
    
    async def async_process_command(self, command: str):
        """处理用户命令"""
        _LOGGER.info(f"处理命令: {command}")
        
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
            "sensors": {}
        }
        
        # 获取所有传感器数据
        for sensor in self.device_roles[ROLE_SENSORS]:
            for entity_id in sensor["entities"]:
                state = self.hass.states.get(entity_id)
                if state:
                    context["sensors"][entity_id] = state.state
        
        # 保存上下文历史
        self.context_history.append(context)
        if len(self.context_history) > 100:  # 限制历史记录大小
            self.context_history.pop(0)
            
        return context
    
    def _check_learned_behavior(self, command: str, context: dict):
        """检查是否有学习过的行为"""
        # 根据命令关键词和小时匹配
        hour = context["time"].split(":")[0]
        key = f"{command}|{hour}"
        
        if key in self.learned_habits:
            return self.learned_habits[key]
        
        # 模糊匹配
        for learned_key, action in self.learned_habits.items():
            cmd_part = learned_key.split("|")[0]
            hour_part = learned_key.split("|")[1]
            
            # 命令相似度检查
            if cmd_part in command and hour_part == hour:
                return action
                
        return None
    
    async def async_parse_command(self, command: str, context: dict):
        """解析用户命令"""
        # 尝试本地解析
        parsed = self._local_command_parser(command)
        if parsed["intent"] != "unknown":
            return parsed
        
        # 使用DeepSeek API进行解析
        return await self._call_deepseek_api(command, context)
    
    def _local_command_parser(self, command: str):
        """本地命令解析器"""
        parsed = {
            "intent": "unknown",
            "action": {"type": "unknown"},
            "entities": []
        }
        
        # 简单命令识别
        if "打开" in command and "灯" in command:
            parsed["intent"] = "turn_on_light"
            parsed["action"] = {
                "type": "call_service",
                "domain": "light",
                "service": "turn_on",
                "target": {"entity_id": "light.living_room"}
            }
            
            # 识别具体灯光
            if "客厅" in command:
                parsed["action"]["target"] = {"entity_id": "light.living_room"}
            elif "卧室" in command:
                parsed["action"]["target"] = {"entity_id": "light.bedroom"}
                
        elif "关闭" in command and "灯" in command:
            parsed["intent"] = "turn_off_light"
            parsed["action"] = {
                "type": "call_service",
                "domain": "light",
                "service": "turn_off",
                "target": {"entity_id": "light.living_room"}
            }
            
        elif "摄像头" in command:
            parsed["intent"] = "view_camera"
            parsed["action"] = {
                "type": "call_service",
                "domain": "camera",
                "service": "snapshot",
                "target": {"entity_id": "camera.front_door"}
            }
        
        return parsed
    
    async def _call_deepseek_api(self, command: str, context: dict):
        """调用DeepSeek API解析命令"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": f"""
                    你是一个智能家居控制系统，负责解析用户命令并执行相应的家庭自动化操作。
                    当前环境上下文：
                    {json.dumps(context, indent=2)}
                    
                    可用设备：
                    {json.dumps(self.device_roles, indent=2)}
                    
                    请将用户命令解析为JSON格式的操作指令，格式如下：
                    {{
                      "intent": "意图名称",
                      "action": {{
                        "type": "call_service" | "speak" | "other",
                        "domain": "服务领域",
                        "service": "服务名称",
                        "target": {{"entity_id": "实体ID"}},
                        "data": {{}}  # 额外数据
                      }},
                      "response": "给用户的自然语言响应"
                    }}
                    """
                },
                {
                    "role": "user",
                    "content": command
                }
            ]
        }
        
        try:
            async with self.session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                
                # 提取JSON部分
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                else:
                    # 尝试直接解析整个响应
                    return json.loads(content)
        except Exception as e:
            _LOGGER.error(f"调用DeepSeek API失败: {e}")
            return {
                "intent": "error",
                "action": {"type": "speak", "message": "抱歉，处理命令时遇到问题"},
                "response": "抱歉，处理命令时遇到问题"
            }
    
    async def async_execute_action(self, action: dict):
        """执行动作"""
        action_type = action.get("type")
        
        if action_type == "call_service":
            domain = action.get("domain")
            service = action.get("service")
            target = action.get("target", {})
            service_data = action.get("data", {})
            
            try:
                await self.hass.services.async_call(
                    domain, 
                    service, 
                    service_data=service_data,
                    target=target,
                    blocking=True
                )
                return True
            except Exception as e:
                _LOGGER.error(f"执行服务调用失败: {e}")
                return False
        
        elif action_type == "speak":
            message = action.get("message", "操作完成")
            return await self.async_speak_message(message)
        
        return False
    
    async def async_speak_message(self, message: str):
        """使用小爱音箱播放消息"""
        if self.device_roles[ROLE_MOUTH]:
            for mouth in self.device_roles[ROLE_MOUTH]:
                await self.hass.services.async_call(
                    "xiaomi_miot", 
                    "speak_text", 
                    {
                        "entity_id": mouth["entities"][0],
                        "text": message
                    }
                )
            return True
        return False
    
    def _learn_behavior(self, command: str, context: dict, parsed_command: dict):
        """学习用户行为"""
        # 基于时间和命令创建唯一键
        hour = context["time"].split(":")[0]
        key = f"{command}|{hour}"
        
        # 保存学习到的行为
        self.learned_habits[key] = parsed_command["action"]
        _LOGGER.info(f"学习到新行为: {key} -> {parsed_command['action']}")
    
    async def async_get_agent_extra(self) -> dict:
        """返回代理额外信息"""
        return {"device_roles": self.device_roles}
    
    async def async_process(self, user_input: agent.ConversationInput) -> agent.ConversationResult:
        """处理对话输入"""
        result = await self.async_process_command(user_input.text)
        return agent.ConversationResult(
            response=result.get("response", "操作已完成"),
            conversation_id=user_input.conversation_id
        )
