"""
问题解决器 - 专注于解决问题

核心原则：
1. 不追求话多，每句话都要解决问题
2. 优先优化解决问题的准确率
3. 先教它怎么思考，再喂阅历数据
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Solution:
    """解决方案"""
    question: str
    answer: str
    confidence: float
    reasoning: List[str]  # 推理过程


class ProblemSolver:
    """问题解决器"""
    
    def __init__(self):
        # 知识库（简单的问答对）
        self.knowledge: Dict[str, str] = {}
        
        # 问题解决模板
        self.templates = {
            "是什么": self._solve_definition,
            "为什么": self._solve_reason,
            "怎么": self._solve_method,
            "如何": self._solve_method,
            "哪个": self._solve_comparison,
            "是不是": self._solve_yes_no,
        }
    
    def solve(self, question: str, context: str = "") -> Solution:
        """解决问题"""
        # 1. 识别问题类型
        q_type = self._identify_type(question)
        
        # 2. 查找知识
        known_answer = self._search_knowledge(question)
        
        if known_answer:
            return Solution(
                question=question,
                answer=known_answer,
                confidence=0.9,
                reasoning=["从知识库中找到答案"]
            )
        
        # 3. 使用模板推理
        if q_type in self.templates:
            answer, reasoning = self.templates[q_type](question, context)
        else:
            answer, reasoning = self._solve_generic(question, context)
        
        return Solution(
            question=question,
            answer=answer,
            confidence=0.7,
            reasoning=reasoning
        )
    
    def _identify_type(self, question: str) -> str:
        """识别问题类型"""
        for key in self.templates:
            if key in question:
                return key
        return "generic"
    
    def _search_knowledge(self, question: str) -> Optional[str]:
        """搜索知识库"""
        # 简单的关键词匹配
        for key, value in self.knowledge.items():
            if key in question or question in key:
                return value
        return None
    
    def _solve_definition(self, question: str, context: str) -> tuple:
        """解决定义类问题"""
        reasoning = [
            "1. 识别为定义类问题",
            "2. 提取核心概念",
            "3. 给出定义"
        ]
        
        # 提取概念
        concept = question.replace("什么是", "").replace("是什么", "").replace("？", "")
        
        answer = f"【{concept}】\n"
        answer += f"定义：{concept}是指...\n"
        answer += f"特点：...\n"
        answer += f"应用：..."
        
        return answer, reasoning
    
    def _solve_reason(self, question: str, context: str) -> tuple:
        """解决原因类问题"""
        reasoning = [
            "1. 识别为原因类问题",
            "2. 分析因果关系",
            "3. 给出原因"
        ]
        
        answer = "原因分析：\n"
        answer += "1. 直接原因：...\n"
        answer += "2. 根本原因：...\n"
        answer += "3. 相关因素：..."
        
        return answer, reasoning
    
    def _solve_method(self, question: str, context: str) -> tuple:
        """解决方法类问题"""
        reasoning = [
            "1. 识别为方法类问题",
            "2. 分析所需条件",
            "3. 给出步骤"
        ]
        
        answer = "解决步骤：\n"
        answer += "第一步：...\n"
        answer += "第二步：...\n"
        answer += "第三步：...\n"
        answer += "注意事项：..."
        
        return answer, reasoning
    
    def _solve_comparison(self, question: str, context: str) -> tuple:
        """解决比较类问题"""
        reasoning = [
            "1. 识别为比较类问题",
            "2. 分析各自特点",
            "3. 给出对比结论"
        ]
        
        answer = "对比分析：\n"
        answer += "相同点：...\n"
        answer += "不同点：...\n"
        answer += "建议：..."
        
        return answer, reasoning
    
    def _solve_yes_no(self, question: str, context: str) -> tuple:
        """解决判断类问题"""
        reasoning = [
            "1. 识别为判断类问题",
            "2. 分析条件",
            "3. 给出判断"
        ]
        
        answer = "判断：\n"
        answer += "结论：是/不是\n"
        answer += "理由：..."
        
        return answer, reasoning
    
    def _solve_generic(self, question: str, context: str) -> tuple:
        """解决通用问题"""
        reasoning = [
            "1. 分析问题",
            "2. 尝试理解意图",
            "3. 给出回答"
        ]
        
        answer = f"关于「{question}」：\n"
        answer += "我理解您的问题是...\n"
        answer += "我的回答是..."
        
        return answer, reasoning
    
    def learn(self, question: str, answer: str):
        """学习新知识"""
        self.knowledge[question] = answer
    
    def save_knowledge(self, path: str):
        """保存知识"""
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    def load_knowledge(self, path: str):
        """加载知识"""
        import json
        import os
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)


if __name__ == "__main__":
    solver = ProblemSolver()
    
    # 学习一些知识
    solver.learn("什么是Python", "Python是一种高级编程语言，以简洁易读著称。")
    solver.learn("什么是AI", "AI是人工智能的缩写，指让机器模拟人类智能的技术。")
    
    # 测试
    questions = [
        "什么是Python？",
        "为什么学习编程？",
        "怎么学习Python？",
        "Python和Java哪个好？"
    ]
    
    for q in questions:
        print(f"\n问题：{q}")
        print("-" * 40)
        result = solver.solve(q)
        print(f"答案：{result.answer}")
        print(f"置信度：{result.confidence}")
