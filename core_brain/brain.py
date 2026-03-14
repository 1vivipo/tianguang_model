"""
核心大脑 Core Brain - 主类

整合所有组件：
1. 思考引擎 - 问题拆解、推理
2. 问题解决器 - 给出答案
3. 对话记忆 - 记住对话
4. 知识接口 - 连接外部知识库

使用方法：
    brain = CoreBrain()
    answer = brain.chat("什么是人工智能？")
"""

import os
from typing import List, Dict, Optional

from .logic.thinking_engine import ThinkingEngine, ProblemSolver
from .memory.dialog_memory import DialogMemory


class CoreBrain:
    """核心大脑"""
    
    def __init__(self, memory_path: str = None):
        # 初始化组件
        self.thinking_engine = ThinkingEngine()
        self.problem_solver = ProblemSolver()
        self.memory = DialogMemory()
        
        # 记忆路径
        self.memory_path = memory_path or "./core_brain_memory.json"
        
        # 加载记忆
        if os.path.exists(self.memory_path):
            self.memory.load(self.memory_path)
        
        # 外部知识库接口
        self.external_knowledge = {}
        
        # 统计
        self.stats = {
            "total_conversations": 0,
            "questions_answered": 0,
            "knowledge_learned": 0
        }
    
    def chat(self, message: str) -> str:
        """对话"""
        self.stats["total_conversations"] += 1
        
        # 1. 先回忆是否有相关记忆
        recalled = self.memory.recall(message)
        
        # 2. 思考问题
        thinking_result = self.thinking_engine.think(message)
        
        # 3. 解决问题
        solution = self.problem_solver.solve(message)
        
        # 4. 构建回答
        if recalled:
            answer = recalled
        else:
            answer = self._build_answer(thinking_result, solution)
        
        # 5. 记住这轮对话
        is_important = self._is_important(message)
        self.memory.add_turn(message, answer, important=is_important)
        
        # 6. 保存记忆
        self._save_memory()
        
        self.stats["questions_answered"] += 1
        
        return answer
    
    def _build_answer(self, thinking_result, solution) -> str:
        """构建回答"""
        lines = []
        
        # 简洁的回答
        lines.append(f"【{thinking_result.problem_type.value}】")
        
        if solution.reasoning:
            lines.append("思考过程：")
            for r in solution.reasoning[:3]:
                lines.append(f"  {r}")
        
        lines.append("")
        lines.append(solution.answer)
        
        return "\n".join(lines)
    
    def _is_important(self, message: str) -> bool:
        """判断是否重要"""
        # 包含关键词的认为重要
        important_keywords = ["记住", "学习", "重要", "保存", "记住这个"]
        for kw in important_keywords:
            if kw in message:
                return True
        return False
    
    def _save_memory(self):
        """保存记忆"""
        self.memory.save(self.memory_path)
    
    def learn(self, question: str, answer: str):
        """学习新知识"""
        self.memory.learn(question, answer)
        self.problem_solver.learn(question, answer)
        self.stats["knowledge_learned"] += 1
        self._save_memory()
    
    def connect_knowledge(self, name: str, knowledge_base: Dict):
        """连接外部知识库"""
        self.external_knowledge[name] = knowledge_base
    
    def query_external(self, query: str) -> Optional[str]:
        """查询外部知识库"""
        for name, kb in self.external_knowledge.items():
            if query in kb:
                return kb[query]
        return None
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            **self.stats,
            "short_term_memory": len(self.memory.short_term),
            "long_term_memory": len(self.memory.long_term),
            "learned_knowledge": len(self.memory.learned_knowledge)
        }
    
    def clear_memory(self):
        """清空记忆"""
        self.memory.clear_all()
        self._save_memory()
    
    def export_knowledge(self, path: str):
        """导出知识"""
        self.problem_solver.save_knowledge(path)


def create_brain(memory_path: str = None) -> CoreBrain:
    """创建核心大脑"""
    return CoreBrain(memory_path)


if __name__ == "__main__":
    # 测试
    brain = CoreBrain()
    
    # 学习一些知识
    brain.learn("什么是Python", "Python是一种高级编程语言，简洁易读。")
    brain.learn("什么是AI", "AI是人工智能，让机器模拟人类智能。")
    
    # 对话测试
    questions = [
        "你好",
        "什么是Python？",
        "怎么学习编程？",
        "为什么学习Python？",
        "Python和Java哪个好？"
    ]
    
    for q in questions:
        print(f"\n用户：{q}")
        print("-" * 40)
        answer = brain.chat(q)
        print(f"助手：{answer}")
    
    # 统计
    print(f"\n{'='*40}")
    print("统计信息：")
    print(brain.get_stats())
