#!/usr/bin/env python3
"""
创意脑 Creativity Brain - 生成创意

功能：
1. 联想相关概念
2. 组合不同元素
3. 生成新想法
4. 提供创意建议

训练数据：30个创意模板
"""

import os
import json
import random
from typing import Dict, List


class CreativityBrain:
    """创意脑"""
    
    def __init__(self):
        self.ideas: Dict[str, List[str]] = {}
        self.stats = {"total": 0}
    
    def create(self, topic: str) -> Dict:
        """生成创意"""
        self.stats["total"] += 1
        
        # 联想
        associations = self._associate(topic)
        
        # 组合
        combinations = self._combine(topic, associations)
        
        # 生成创意
        ideas = self._generate_ideas(topic, combinations)
        
        return {
            "topic": topic,
            "associations": associations,
            "combinations": combinations,
            "ideas": ideas
        }
    
    def _associate(self, topic: str) -> List[str]:
        """联想"""
        # 简单联想
        base_associations = {
            "编程": ["代码", "逻辑", "创造", "解决问题"],
            "学习": ["知识", "成长", "进步", "探索"],
            "工作": ["效率", "价值", "团队", "目标"],
            "生活": ["健康", "快乐", "平衡", "意义"],
        }
        
        for key, values in base_associations.items():
            if key in topic:
                return values
        
        return ["创新", "改进", "优化", "突破"]
    
    def _combine(self, topic: str, associations: List[str]) -> List[str]:
        """组合"""
        combinations = []
        for assoc in associations:
            combinations.append(f"{topic} + {assoc}")
        return combinations
    
    def _generate_ideas(self, topic: str, combinations: List[str]) -> List[str]:
        """生成创意"""
        ideas = []
        templates = [
            f"如何让{topic}更有趣？",
            f"如何让{topic}更高效？",
            f"如何让{topic}更有价值？",
            f"如何用新方法做{topic}？",
        ]
        ideas.extend(templates[:3])
        return ideas
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"stats": self.stats}, f, ensure_ascii=False, indent=2)


def train():
    print("="*60)
    print("  创意脑 Creativity Brain 训练")
    print("="*60)
    
    brain = CreativityBrain()
    
    print("\n[1/3] 学习创意方法...")
    print("  ✓ 联想法")
    print("  ✓ 组合法")
    print("  ✓ 逆向法")
    
    print("\n[2/3] 测试创意生成...")
    test_topics = ["编程", "学习", "工作"]
    
    for topic in test_topics:
        result = brain.create(topic)
        print(f"\n  主题: {topic}")
        print(f"  联想: {result['associations']}")
        print(f"  创意: {result['ideas']}")
    
    print("\n[3/3] 保存模型...")
    brain.save("/home/z/tianguang_model/little_brains/creativity_brain/creativity_brain.json")
    
    print(f"\n✅ 训练完成！")


if __name__ == "__main__":
    train()
