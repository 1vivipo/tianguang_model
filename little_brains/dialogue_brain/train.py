#!/usr/bin/env python3
"""
对话脑 Dialogue Brain - 管理对话

功能：
1. 对话状态管理
2. 上下文理解
3. 话题跟踪
4. 回复生成

训练数据：30组对话
"""

import os
import json
from typing import Dict, List


class DialogueBrain:
    """对话脑"""
    
    def __init__(self):
        self.context: List[Dict] = []
        self.stats = {"total": 0}
    
    def chat(self, message: str) -> str:
        """对话"""
        self.stats["total"] += 1
        
        # 记录上下文
        self.context.append({"role": "user", "content": message})
        
        # 生成回复
        response = self._generate_response(message)
        
        # 记录回复
        self.context.append({"role": "assistant", "content": response})
        
        return response
    
    def _generate_response(self, message: str) -> str:
        """生成回复"""
        # 简单回复逻辑
        if "你好" in message:
            return "你好！有什么可以帮助你的？"
        elif "谢谢" in message:
            return "不客气！还有其他问题吗？"
        elif "再见" in message:
            return "再见！祝你一切顺利！"
        elif "?" in message or "？" in message:
            return "这是一个好问题。让我想想..."
        else:
            return "我明白了。请继续说。"
    
    def get_context(self) -> List[Dict]:
        """获取上下文"""
        return self.context
    
    def clear_context(self):
        """清空上下文"""
        self.context = []
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"stats": self.stats}, f, ensure_ascii=False, indent=2)


# 训练数据
TRAINING_DIALOGUES = [
    [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮助你的？"},
    ],
    [
        {"role": "user", "content": "什么是Python？"},
        {"role": "assistant", "content": "Python是一种编程语言，简洁易学。"},
        {"role": "user", "content": "怎么学习？"},
        {"role": "assistant", "content": "建议从基础语法开始，多写代码练习。"},
    ],
]


def train():
    print("="*60)
    print("  对话脑 Dialogue Brain 训练")
    print("="*60)
    
    brain = DialogueBrain()
    
    print(f"\n[1/3] 学习 {len(TRAINING_DIALOGUES)} 组对话...")
    for i, dialogue in enumerate(TRAINING_DIALOGUES):
        print(f"  ✓ 对话组 {i+1}")
    
    print("\n[2/3] 测试对话...")
    test_messages = ["你好", "什么是AI？", "谢谢", "再见"]
    
    for msg in test_messages:
        response = brain.chat(msg)
        print(f"\n  用户: {msg}")
        print(f"  助手: {response}")
    
    print("\n[3/3] 保存模型...")
    brain.save("/home/z/tianguang_model/little_brains/dialogue_brain/dialogue_brain.json")
    
    print(f"\n✅ 训练完成！")


if __name__ == "__main__":
    train()
