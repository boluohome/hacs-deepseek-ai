"""存在感知 - 检测用户状态"""
import logging
import asyncio
from datetime import datetime, timedelta
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class PresenceDetector:
    """检测用户存在状态"""
    
    def __init__(self, hass, brain):
        self.hass = hass
        self.brain = brain
        self.last_detected = datetime.now()
        self.status = "home"  # home/away/missing
        self.check_interval = 300  # 5分钟检查一次
        self.check_task = None
        
    async def async_setup(self):
        """设置存在检测"""
        # 注册设备状态监听
        for entity_id in self.hass.states.async_entity_ids():
            if entity_id.startswith(("device_tracker.", "person.")):
                self.hass.bus.async_listen(
                    f"state_changed.{entity_id}",
                    self.handle_presence_change
                )
        
        # 定时检查
        self.check_task = async_track_time_interval(
            self.hass,
            self.check_presence_status,
            timedelta(seconds=self.check_interval)
        )
    
    async def async_cleanup(self):
        """清理资源"""
        if self.check_task:
            self.check_task()
    
    async def handle_presence_change(self, event):
        """处理存在状态变化"""
        new_state = event.data.get("new_state")
        if new_state and new_state.state == "home":
            self.last_detected = datetime.now()
            self.status = "home"
            _LOGGER.info("用户到家")
            
            # 如果之前处于担心状态，现在用户回来了
            if self.brain.emotion_engine.emotion_state in ["concerned", "worried"]:
                await self.brain.emotion_engine.express_joy()
    
    async def check_presence_status(self, now=None):
        """检查存在状态"""
        # 如果超过4小时没有检测到活动
        if (datetime.now() - self.last_detected) > timedelta(hours=4):
            if self.status != "missing":
                _LOGGER.warning("用户可能失踪")
                self.status = "missing"
                # 触发关心响应
                await self.hass.services.async_call(
                    DOMAIN,
                    "express_concern",
                    {"reason": "long_time_no_detection"}
                )
                
                # 尝试寻找用户
                await self.try_find_user()
        elif (datetime.now() - self.last_detected) > timedelta(hours=1):
            self.status = "away"
    
    async def try_find_user(self):
        """尝试寻找失踪的用户"""
        # 1. 检查最后位置
        last_location = await self.get_last_known_location()
        
        # 2. 通过摄像头寻找
        if last_location:
            await self.check_camera_for_user(last_location)
        
        # 3. 通知紧急联系人
        await self.notify_emergency_contact()
    
    async def get_last_known_location(self):
        """获取最后已知位置"""
        # 这里简化实现，实际应获取用户最后位置
        return "客厅"
    
    async def check_camera_for_user(self, location):
        """通过摄像头寻找用户"""
        # 这里简化实现，实际应调用视觉处理器
        _LOGGER.info(f"正在检查{location}的摄像头寻找用户")
    
    async def notify_emergency_contact(self):
        """通知紧急联系人"""
        # 这里简化实现，实际应发送通知
        _LOGGER.info("通知紧急联系人用户可能失踪")