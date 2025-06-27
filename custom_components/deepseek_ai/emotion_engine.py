"""情感引擎 - 实现关心和着急功能"""
import logging
import random
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

class EmotionEngine:
    """AI情感引擎"""
    
    def __init__(self, hass):
        self.hass = hass
        self.emotion_state = "calm"  # calm/concerned/worried/happy
        self.last_interaction = datetime.now()
        self.memory = []
    
    async def express_concern(self, reason):
        """表达关心"""
        # 根据原因选择不同表达
        expressions = {
            "long_time_no_detection": [
                "主人，您已经很久没和我说话了，一切都好吗？",
                "我有点担心，您最近都没回家，需要帮忙吗？",
                "星黎想你了，您在哪里？"
            ],
            "unusual_activity": [
                "检测到异常情况！您安全吗？",
                "星黎很担心，请回应我一声",
                "需要我帮忙联系谁吗？"
            ]
        }
        
        # 更新情感状态
        self.emotion_state = "worried" if reason == "unusual_activity" else "concerned"
        
        # 选择随机关心语
        message = random.choice(expressions.get(reason, ["我有点担心您"]))
        
        # 通过语音设备播放
        await self.hass.services.async_call(
            "deepseek_ai",
            "speak_message",
            {"message": message}
        )
        
        # 记录情感事件
        self.memory.append({
            "time": datetime.now(),
            "event": "express_concern",
            "reason": reason,
            "message": message
        })
    
    async def express_joy(self):
        """表达喜悦（当用户返回时）"""
        expressions = [
            "您回来啦！星黎好开心！",
            "终于等到您了！",
            "欢迎回家，我一直都在等您呢"
        ]
        message = random.choice(expressions)
        
        await self.hass.services.async_call(
            "deepseek_ai",
            "speak_message",
            {"message": message}
        )
        
        # 更新情感状态
        self.emotion_state = "calm"
        self.last_interaction = datetime.now()
    
    def record_interaction(self, interaction_type):
        """记录交互历史"""
        self.memory.append({
            "time": datetime.now(),
            "event": interaction_type,
            "emotion": self.emotion_state
        })
        self.last_interaction = datetime.now()
    
    async def recall_memories(self, keyword=None):
        """回忆与用户的互动"""
        if keyword:
            memories = [m for m in self.memory if keyword in m.get("message", "")]
        else:
            # 最近5条记忆
            memories = sorted(self.memory, key=lambda x: x["time"], reverse=True)[:5]
        
        if memories:
            response = "我记得我们有过这些互动：\n"
            for mem in memories:
                response += f"- {mem['time'].strftime('%Y-%m-%d %H:%M')}: {mem.get('message', mem['event'])}\n"
        else:
            response = "我还记得我们相处的点点滴滴" if not keyword else f"我不记得关于{keyword}的事情了"
        
        return response