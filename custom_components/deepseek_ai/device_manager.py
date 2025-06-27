"""设备管理器 - 发现、分类和管理设备"""
import logging
from homeassistant.helpers import device_registry as dr, entity_registry as er
from .const import ROLE_EYES, ROLE_EARS, ROLE_MOUTH, ROLE_HANDS, ROLE_SENSORS
from .device_classifier import DeviceClassifier

_LOGGER = logging.getLogger(__name__)

class DeviceManager:
    """管理所有智能家居设备及其角色"""
    
    def __init__(self, hass):
        self.hass = hass
        self.classifier = DeviceClassifier()
        self.device_roles = {
            ROLE_EYES: [],
            ROLE_EARS: [],
            ROLE_MOUTH: [],
            ROLE_HANDS: [],
            ROLE_SENSORS: []
        }
    
    async def discover_devices(self):
        """发现并分类所有设备"""
        _LOGGER.info("开始设备发现...")
        
        # 重置设备列表
        for role in self.device_roles:
            self.device_roles[role] = []
        
        # 获取设备注册表
        device_registry = dr.async_get(self.hass)
        entity_registry = er.async_get(self.hass)
        
        # 遍历所有设备
        for device_entry in device_registry.devices.values():
            device_entities = er.async_entries_for_device(
                entity_registry, device_entry.id
            )
            
            # 分类设备
            role = self.classifier.classify_device(device_entry, device_entities)
            if role:
                device_info = {
                    "id": device_entry.id,
                    "name": device_entry.name or device_entry.id,
                    "manufacturer": device_entry.manufacturer or "Unknown",
                    "model": device_entry.model or "Unknown",
                    "entities": [e.entity_id for e in device_entities],
                    "role": role
                }
                
                self.device_roles[role].append(device_info)
                _LOGGER.debug(f"设备分类: {device_info['name']} -> {role}")
        
        _LOGGER.info(f"设备发现完成: {sum(len(v) for v in self.device_roles.values())} 个设备")
    
    def get_devices_by_role(self, role):
        """获取指定角色的设备"""
        return self.device_roles.get(role, [])
    
    def get_primary_device(self, role):
        """获取主要设备（例如：主要摄像头）"""
        devices = self.get_devices_by_role(role)
        if devices:
            # 优先选择名称包含"主"或"客厅"的设备
            for device in devices:
                if "主" in device["name"] or "客厅" in device["name"]:
                    return device
            return devices[0]
        return None