"""智能设备分类器"""
import logging

_LOGGER = logging.getLogger(__name__)

class IntelligentDeviceClassifier:
    """智能设备分类器"""
    
    def classify_device(self, device_entry, entities):
        """根据设备实体分类设备角色"""
        # 摄像头 -> 眼睛
        if any(e.domain == "camera" for e in entities):
            return "eyes"
        
        # 麦克风/语音设备 -> 耳朵
        if device_entry.manufacturer and "xiaomi" in device_entry.manufacturer.lower() and device_entry.model and "speaker" in device_entry.model.lower():
            return "ears"
        
        # 音箱 -> 嘴巴
        if any(e.domain == "media_player" for e in entities):
            return "mouth"
        
        # 开关/灯光 -> 手
        if any(e.domain in ["switch", "light", "cover"] for e in entities):
            return "hands"
        
        # 传感器 -> 传感器
        if any(e.domain in ["sensor", "binary_sensor", "climate"] for e in entities):
            return "sensors"
        
        return None
