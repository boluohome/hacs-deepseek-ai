"""视觉处理器 - 处理摄像头输入"""
import logging
import base64
import aiohttp
import os
from homeassistant.core import HomeAssistant
from .const import DOMAIN, DEFAULT_API_BASE

_LOGGER = logging.getLogger(__name__)

class VisionProcessor:
    """处理视觉输入和图像分析"""
    
    def __init__(self, hass: HomeAssistant, api_key: str):
        self.hass = hass
        self.api_key = api_key
        self.session = aiohttp.ClientSession()
    
    async def analyze_image(self, entity_id: str):
        """分析指定摄像头的图像"""
        # 获取摄像头快照
        snapshot_path = "/tmp/deepseek_snapshot.jpg"
        await self.hass.services.async_call(
            "camera", 
            "snapshot", 
            {"entity_id": entity_id, "filename": snapshot_path},
            blocking=True
        )
        
        # 检查文件是否存在
        if not os.path.exists(snapshot_path):
            return "无法获取图像"
        
        # 读取图像数据
        try:
            with open(snapshot_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            return f"读取图像失败: {str(e)}"
        
        # 调用视觉API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-vision",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "描述图像中的场景"},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        try:
            async with self.session.post(
                f"{DEFAULT_API_BASE}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                if response.status != 200:
                    return f"视觉API错误: {response.status}"
                
                data = await response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"视觉处理错误: {str(e)}"
        finally:
            # 清理临时文件
            try:
                os.remove(snapshot_path)
            except:
                pass
    
    async def close(self):
        """关闭资源"""
        await self.session.close()