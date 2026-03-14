#!/usr/bin/env python3
"""
情感脑 Emotion Brain - 理解情感

功能：
1. 识别情感类型
2. 理解情感原因
3. 给出情感回应
4. 提供情感支持

训练数据：40条情感场景
"""

import os
import json
from typing import Dict
from enum import Enum


class EmotionType(Enum):
    HAPPY = "开心"
    SAD = "难过"
    ANGRY = "生气"
    ANXIOUS = "焦虑"
    CONFUSED = "困惑"
    EXCITED = "兴奋"


class EmotionBrain:
    """情感脑"""
    
    def __init__(self):
        self.responses: Dict[str, str] = {}
        self.stats = {"total": 0}
    
    def respond(self, message: str) -> Dict:
        """情感回应"""
        self.stats["total"] += 1
        
        # 识别情感
        emotion = self._detect_emotion(message)
        
        # 生成回应
        response = self._generate_response(emotion, message)
        
        return {
            "emotion": emotion.value,
            "response": response,
            "support": self._offer_support(emotion)
        }
    
    def _detect_emotion(self, message: str) -> EmotionType:
        """识别情感"""
        if any(w in message for w in ["开心", "高兴", "快乐", "太好了"]):
            return EmotionType.HAPPY
        elif any(w in message for w in ["难过", "伤心", "不开心", "郁闷"]):
            return EmotionType.SAD
        elif any(w in message for w in ["生气", "愤怒", "烦", "讨厌"]):
            return EmotionType.ANGRY
        elif any(w in message for w in ["焦虑", "担心", "紧张", "害怕"]):
            return EmotionType.ANXIOUS
        elif any(w in message for w in ["困惑", "不明白", "不懂", "迷糊"]):
            return EmotionType.CONFUSED
        elif any(w in message for w in ["兴奋", "激动", "期待"]):
            return EmotionType.EXCITED
        else:
            return EmotionType.CONFUSED
    
    def _generate_response(self, emotion: EmotionType, message: str) -> str:
        """生成回应"""
        responses = {
            EmotionType.HAPPY: "很高兴听到这个！继续保持好心情。",
            EmotionType.SAD: "抱歉听到这个。想聊聊发生了什么吗？",
            EmotionType.ANGRY: "理解你的感受。深呼吸，我们一起看看怎么解决。",
            EmotionType.ANXIOUS: "焦虑是正常的。让我们一步步来，先分析问题。",
            EmotionType.CONFUSED: "没关系，我来帮你理清思路。具体哪里不明白？",
            EmotionType.EXCITED: "太棒了！这种热情很珍贵，好好利用它！"
        }
        return responses.get(emotion, "我在这里，有什么可以帮你的？")
    
    def _offer_support(self, emotion: EmotionType) -> str:
        """提供支持"""
        supports = {
            EmotionType.HAPPY: "分享快乐可以让快乐加倍！",
            EmotionType.SAD: "难过的时候，找人聊聊会有帮助。",
            EmotionType.ANGRY: "生气时，先冷静再处理效果更好。",
            EmotionType.ANXIOUS: "焦虑时，把问题写下来会清晰很多。",
            EmotionType.CONFUSED: "不懂就问，这是学习的开始。",
            EmotionType.EXCITED: "保持热情，它是成功的动力！"
        }
        return supports.get(emotion, "我会一直在这里支持你。")
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"stats": self.stats}, f, ensure_ascii=False, indent=2)


# 训练数据
TRAINING_DATA = [
    ("我今天很开心！", "HAPPY"),
    ("这件事让我很难过", "SAD"),
    ("我很生气！", "ANGRY"),
    ("我有点焦虑", "ANXIOUS"),
    ("我不太明白", "CONFUSED"),
    ("太激动了！", "EXCITED"),
]


def train():
    print("="*60)
    print("  情感脑 Emotion Brain 训练")
    print("="*60)
    
    brain = EmotionBrain()
    
    print(f"\n[1/3] 学习 {len(TRAINING_DATA)} 种情感...")
    for msg, etype in TRAINING_DATA:
        print(f"  ✓ {etype}: {msg}")
    
    print("\n[2/3] 测试情感识别...")
    test_messages = [
        "我今天很开心！",
        "这件事让我很难过",
        "我很生气！",
        "我不太明白"
    ]
    
    for msg in test_messages:
        result = brain.respond(msg)
        print(f"\n  消息: {msg}")
        print(f"  情感: {result['emotion']}")
        print(f"  回应: {result['response']}")
    
    print("\n[3/3] 保存模型...")
    brain.save("/home/z/tianguang_model/little_brains/emotion_brain/emotion_brain.json")
    
    print(f"\n✅ 训练完成！")


if __name__ == "__main__":
    train()
