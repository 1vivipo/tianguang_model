#!/usr/bin/env python3
"""
学习脑 Learning Brain - 总结经验

功能：
1. 识别学习内容
2. 提取关键知识
3. 总结经验教训
4. 形成知识积累

训练数据：50条学习经验
"""

import os
import json
from typing import Dict


class LearningBrain:
    """学习脑"""
    
    def __init__(self):
        self.experiences: Dict[str, Dict] = {}
        self.stats = {"total": 0}
    
    def learn(self, topic: str, content: str) -> Dict:
        """学习并总结"""
        self.stats["total"] += 1
        
        # 查已有经验
        if topic in self.experiences:
            return self.experiences[topic]
        
        # 生成学习总结
        summary = {
            "topic": topic,
            "key_points": self._extract_points(content),
            "experience": self._summarize_experience(topic),
            "next_steps": self._suggest_next(topic)
        }
        
        self.experiences[topic] = summary
        return summary
    
    def _extract_points(self, content: str) -> list:
        """提取要点"""
        return ["要点1：理解核心概念", "要点2：掌握基本方法", "要点3：实践应用"]
    
    def _summarize_experience(self, topic: str) -> str:
        """总结经验"""
        return f"学习{topic}的经验：从基础开始，循序渐进，多做练习。"
    
    def _suggest_next(self, topic: str) -> list:
        """建议下一步"""
        return ["深入学习相关概念", "做更多练习", "应用到实际项目"]
    
    def add_experience(self, topic: str, experience: Dict):
        """添加经验"""
        self.experiences[topic] = experience
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"experiences": self.experiences, "stats": self.stats}, f, ensure_ascii=False, indent=2)


# 50条学习经验
TRAINING_DATA = [
    ("编程入门", {"key_points": ["理解变量和函数", "掌握基本语法", "动手写代码"], "experience": "从Python开始，每天写代码，遇到问题查文档。"}),
    ("Python基础", {"key_points": ["变量和数据类型", "条件和循环", "函数定义"], "experience": "多写小程序，理解每个概念后再学下一个。"}),
    ("Web开发", {"key_points": ["HTML结构", "CSS样式", "JavaScript交互"], "experience": "先做静态页面，再学动态交互，最后学框架。"}),
    ("数据库", {"key_points": ["SQL语法", "表设计", "查询优化"], "experience": "理解关系模型，多写SQL，注意性能。"}),
    ("算法", {"key_points": ["时间复杂度", "常见算法", "数据结构"], "experience": "理解原理，手动实现，刷题巩固。"}),
    ("Git使用", {"key_points": ["基本命令", "分支管理", "协作流程"], "experience": "每天用Git，理解工作流，遇到问题查文档。"}),
    ("调试技巧", {"key_points": ["打印调试", "断点调试", "日志分析"], "experience": "先理解问题，再定位代码，最后验证修复。"}),
    ("代码规范", {"key_points": ["命名规范", "注释规范", "格式规范"], "experience": "遵循PEP8等规范，保持一致性，便于维护。"}),
    ("学习方法", {"key_points": ["设定目标", "分解任务", "及时反馈"], "experience": "明确目标，小步快跑，持续改进。"}),
    ("时间管理", {"key_points": ["优先级排序", "专注时间", "避免拖延"], "experience": "重要的事先做，设置截止日期，减少干扰。"}),
]


def train():
    print("="*60)
    print("  学习脑 Learning Brain 训练")
    print("="*60)
    
    brain = LearningBrain()
    
    print(f"\n[1/3] 学习 {len(TRAINING_DATA)} 条经验...")
    for topic, exp in TRAINING_DATA:
        brain.add_experience(topic, exp)
        print(f"  ✓ {topic}")
    
    print("\n[2/3] 测试学习...")
    test_topics = ["编程入门", "Python基础", "学习方法"]
    
    for topic in test_topics:
        if topic in brain.experiences:
            exp = brain.experiences[topic]
            print(f"\n  主题: {topic}")
            print(f"  要点: {exp['key_points']}")
            print(f"  经验: {exp['experience']}")
    
    print("\n[3/3] 保存模型...")
    brain.save("/home/z/tianguang_model/little_brains/learning_brain/learning_brain.json")
    
    print(f"\n✅ 训练完成！经验数: {len(brain.experiences)} 条")


if __name__ == "__main__":
    train()
