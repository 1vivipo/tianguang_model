"""
对话记忆系统 - 让AI记住对话

功能：
1. 短期记忆 - 当前对话
2. 长期记忆 - 重要信息
3. 经验积累 - 学到的知识
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Message:
    """一条消息"""
    role: str  # user / assistant
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DialogTurn:
    """一轮对话"""
    user_message: str
    assistant_message: str
    timestamp: str
    important: bool = False  # 是否重要


class DialogMemory:
    """对话记忆"""
    
    def __init__(self, max_short_term: int = 10, max_long_term: int = 100):
        # 短期记忆（当前对话）
        self.short_term: List[DialogTurn] = []
        self.max_short_term = max_short_term
        
        # 长期记忆（重要对话）
        self.long_term: List[DialogTurn] = []
        self.max_long_term = max_long_term
        
        # 学到的知识
        self.learned_knowledge: Dict[str, str] = {}
        
        # 用户偏好
        self.user_preferences: Dict[str, any] = {}
    
    def add_turn(self, user_msg: str, assistant_msg: str, important: bool = False):
        """添加一轮对话"""
        turn = DialogTurn(
            user_message=user_msg,
            assistant_message=assistant_msg,
            timestamp=datetime.now().isoformat(),
            important=important
        )
        
        # 添加到短期记忆
        self.short_term.append(turn)
        
        # 如果短期记忆满了，移除最旧的
        if len(self.short_term) > self.max_short_term:
            removed = self.short_term.pop(0)
            # 如果是重要的，保存到长期记忆
            if removed.important:
                self._save_to_long_term(removed)
        
        # 如果是重要的，直接保存到长期记忆
        if important:
            self._save_to_long_term(turn)
    
    def _save_to_long_term(self, turn: DialogTurn):
        """保存到长期记忆"""
        self.long_term.append(turn)
        
        # 长期记忆满了就移除最旧的
        if len(self.long_term) > self.max_long_term:
            self.long_term.pop(0)
    
    def get_context(self, max_turns: int = 5) -> str:
        """获取对话上下文"""
        turns = self.short_term[-max_turns:]
        
        context_parts = []
        for turn in turns:
            context_parts.append(f"用户：{turn.user_message}")
            context_parts.append(f"助手：{turn.assistant_message}")
        
        return "\n".join(context_parts)
    
    def learn(self, question: str, answer: str):
        """学习知识"""
        self.learned_knowledge[question] = answer
    
    def recall(self, question: str) -> Optional[str]:
        """回忆知识"""
        # 先查学到的知识
        if question in self.learned_knowledge:
            return self.learned_knowledge[question]
        
        # 再查长期记忆
        for turn in reversed(self.long_term):
            if question in turn.user_message:
                return turn.assistant_message
        
        # 最后查短期记忆
        for turn in reversed(self.short_term):
            if question in turn.user_message:
                return turn.assistant_message
        
        return None
    
    def set_preference(self, key: str, value: any):
        """设置用户偏好"""
        self.user_preferences[key] = value
    
    def get_preference(self, key: str, default: any = None) -> any:
        """获取用户偏好"""
        return self.user_preferences.get(key, default)
    
    def summarize(self) -> str:
        """总结对话"""
        if not self.short_term:
            return "暂无对话记录"
        
        summary = f"对话轮数：{len(self.short_term)}\n"
        summary += f"长期记忆：{len(self.long_term)}条\n"
        summary += f"学到的知识：{len(self.learned_knowledge)}条\n"
        
        # 提取关键话题
        topics = set()
        for turn in self.short_term:
            # 简单提取关键词
            words = turn.user_message.split()
            for word in words:
                if len(word) > 1:
                    topics.add(word)
        
        if topics:
            summary += f"讨论话题：{', '.join(list(topics)[:5])}"
        
        return summary
    
    def save(self, path: str):
        """保存记忆"""
        data = {
            "short_term": [
                {
                    "user": t.user_message,
                    "assistant": t.assistant_message,
                    "timestamp": t.timestamp,
                    "important": t.important
                }
                for t in self.short_term
            ],
            "long_term": [
                {
                    "user": t.user_message,
                    "assistant": t.assistant_message,
                    "timestamp": t.timestamp,
                    "important": t.important
                }
                for t in self.long_term
            ],
            "learned_knowledge": self.learned_knowledge,
            "user_preferences": self.user_preferences
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, path: str):
        """加载记忆"""
        if not os.path.exists(path):
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.short_term = [
            DialogTurn(
                user_message=t["user"],
                assistant_message=t["assistant"],
                timestamp=t["timestamp"],
                important=t.get("important", False)
            )
            for t in data.get("short_term", [])
        ]
        
        self.long_term = [
            DialogTurn(
                user_message=t["user"],
                assistant_message=t["assistant"],
                timestamp=t["timestamp"],
                important=t.get("important", False)
            )
            for t in data.get("long_term", [])
        ]
        
        self.learned_knowledge = data.get("learned_knowledge", {})
        self.user_preferences = data.get("user_preferences", {})
    
    def clear_short_term(self):
        """清空短期记忆"""
        self.short_term = []
    
    def clear_all(self):
        """清空所有记忆"""
        self.short_term = []
        self.long_term = []
        self.learned_knowledge = {}
        self.user_preferences = {}


if __name__ == "__main__":
    # 测试
    memory = DialogMemory()
    
    # 添加对话
    memory.add_turn("你好", "你好！有什么可以帮助你的？")
    memory.add_turn("什么是Python？", "Python是一种编程语言。", important=True)
    memory.add_turn("怎么学习？", "建议从基础语法开始...")
    
    # 获取上下文
    print("对话上下文：")
    print(memory.get_context())
    
    # 回忆
    print("\n回忆'Python'：")
    print(memory.recall("Python"))
    
    # 总结
    print("\n对话总结：")
    print(memory.summarize())
