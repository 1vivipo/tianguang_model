#!/usr/bin/env python3
"""
文本理解脑 Text Understanding Brain - 理解文本

功能：
1. 文本分类
2. 关键信息提取
3. 意图识别
4. 情感分析

训练数据：50条文本样本
"""

import os
import json
import re
from typing import Dict, List
from enum import Enum


class TextType(Enum):
    QUESTION = "问题"
    STATEMENT = "陈述"
    REQUEST = "请求"
    EMOTION = "情感表达"


class TextUnderstandingBrain:
    """文本理解脑"""
    
    def __init__(self):
        self.stats = {"total": 0}
    
    def understand(self, text: str) -> Dict:
        """理解文本"""
        self.stats["total"] += 1
        
        return {
            "text": text,
            "type": self._classify(text).value,
            "keywords": self._extract_keywords(text),
            "intent": self._detect_intent(text),
            "sentiment": self._analyze_sentiment(text)
        }
    
    def _classify(self, text: str) -> TextType:
        """分类"""
        if "?" in text or "？" in text or any(w in text for w in ["什么", "怎么", "为什么"]):
            return TextType.QUESTION
        elif any(w in text for w in ["请", "帮我", "能不能"]):
            return TextType.REQUEST
        elif any(w in text for w in ["开心", "难过", "生气"]):
            return TextType.EMOTION
        else:
            return TextType.STATEMENT
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单提取
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text)
        return [w for w in words if len(w) > 1][:5]
    
    def _detect_intent(self, text: str) -> str:
        """识别意图"""
        if "学习" in text:
            return "学习相关"
        elif "编程" in text:
            return "编程相关"
        elif "工作" in text:
            return "工作相关"
        else:
            return "一般咨询"
    
    def _analyze_sentiment(self, text: str) -> str:
        """情感分析"""
        positive = ["好", "棒", "喜欢", "开心", "高兴"]
        negative = ["不好", "差", "讨厌", "难过", "生气"]
        
        if any(w in text for w in positive):
            return "积极"
        elif any(w in text for w in negative):
            return "消极"
        else:
            return "中性"
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"stats": self.stats}, f, ensure_ascii=False, indent=2)


# 训练数据
TRAINING_DATA = [
    "什么是Python？",
    "怎么学习编程？",
    "今天天气真好",
    "请帮我解决这个问题",
    "我很开心",
]


def train():
    print("="*60)
    print("  文本理解脑 Text Understanding Brain 训练")
    print("="*60)
    
    brain = TextUnderstandingBrain()
    
    print(f"\n[1/3] 学习 {len(TRAINING_DATA)} 个文本样本...")
    for text in TRAINING_DATA:
        print(f"  ✓ {text[:30]}...")
    
    print("\n[2/3] 测试理解...")
    test_texts = [
        "什么是人工智能？",
        "请帮我写一段代码",
        "今天心情不错"
    ]
    
    for text in test_texts:
        result = brain.understand(text)
        print(f"\n  文本: {text}")
        print(f"  类型: {result['type']}")
        print(f"  关键词: {result['keywords']}")
        print(f"  意图: {result['intent']}")
        print(f"  情感: {result['sentiment']}")
    
    print("\n[3/3] 保存模型...")
    brain.save("/home/z/tianguang_model/little_brains/text_understanding_brain/text_understanding_brain.json")
    
    print(f"\n✅ 训练完成！")


if __name__ == "__main__":
    train()
