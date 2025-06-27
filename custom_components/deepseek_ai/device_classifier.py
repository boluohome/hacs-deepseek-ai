"""智能设备分类器"""
import logging
from .const import DEVICE_ROLE_MAPPING, ROLE_SENSORS

_LOGGER = logging.getLogger(__name__)

class DeviceClassifier:
    """根据设备特性分配角色"""
    
    def classify_device(self, device_entry, entities):
        """分类设备角色"""
        # 1. 根据设备类型分类
        for entity in entities:
            entity_type = entity.domain
            if entity_type in DEVICE_ROLE_MAPPING:
                return DEVICE_ROLE_MAPPING[entity_type]
            
            if entity_type == "binary_sensor":
                if "motion" in entity.entity_id:
                    return "eyes"
                elif "sound" in entity.entity_id:
                    return "ears"
        
        # 2. 根据制造商信息分类
        if device_entry.manufacturer:
            manufacturer = device_entry.manufacturer.lower()
            if "xiaomi" in manufacturer or "mijia" in manufacturer:
                if "camera" in (device_entry.model or "").lower():
                    return "eyes"
                if "speaker" in (device_entry.model or "").lower():
                    return "mouth"
        
        # 3. 默认分类为传感器
        return ROLE_SENSORS