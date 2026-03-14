"""
思考引擎 - 核心大脑的心脏

设计原则：
1. 问题拆解 - 把复杂问题拆成小问题
2. 定位核心 - 找到问题的本质
3. 分步解决 - 一步步给出答案
4. 输出答案 - 说清楚，不废话

思考流程：
用户问题
    ↓
┌─────────────────┐
│ 1. 理解问题     │ → 这是什么问题？
└────────┬────────┘
         ↓
┌─────────────────┐
│ 2. 拆解问题     │ → 这个问题包含哪些子问题？
└────────┬────────┘
         ↓
┌─────────────────┐
│ 3. 定位核心     │ → 哪个子问题最关键？
└────────┬────────┘
         ↓
┌─────────────────┐
│ 4. 分步解决     │ → 按什么顺序解决？
└────────┬────────┘
         ↓
┌─────────────────┐
│ 5. 输出答案     │ → 怎么说清楚？
└─────────────────┘
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ProblemType(Enum):
    """问题类型"""
    WHAT = "是什么"      # 定义类问题
    WHY = "为什么"      # 原因类问题
    HOW = "怎么做"      # 方法类问题
    WHICH = "哪个/哪些"  # 选择类问题
    WHEN = "什么时候"    # 时间类问题
    WHERE = "在哪里"     # 地点类问题
    WHO = "谁"          # 人物类问题
    YES_NO = "是不是"    # 判断类问题
    COMPARISON = "比较"   # 比较类问题
    UNKNOWN = "未知"     # 未知类型


@dataclass
class Thought:
    """一个思考步骤"""
    step: int
    action: str      # 动作：理解/拆解/定位/解决/输出
    content: str     # 内容
    confidence: float # 置信度


@dataclass
class ThinkingResult:
    """思考结果"""
    problem_type: ProblemType
    core_question: str
    sub_questions: List[str]
    solution_steps: List[str]
    final_answer: str
    thoughts: List[Thought]


class ThinkingEngine:
    """思考引擎"""
    
    def __init__(self):
        # 问题类型识别模式
        self.patterns = {
            ProblemType.WHAT: [
                r"什么是", r"是什么", r"什么叫", r"指的是什么",
                r"介绍一下", r"说说", r"讲讲"
            ],
            ProblemType.WHY: [
                r"为什么", r"为何", r"怎么会", r"原因是什么"
            ],
            ProblemType.HOW: [
                r"怎么", r"如何", r"怎样", r"方法", r"步骤",
                r"怎么办", r"怎么做"
            ],
            ProblemType.WHICH: [
                r"哪个", r"哪些", r"什么区别", r"还是"
            ],
            ProblemType.WHEN: [
                r"什么时候", r"何时", r"几点", r"哪天"
            ],
            ProblemType.WHERE: [
                r"在哪里", r"在哪", r"什么地方", r"哪里"
            ],
            ProblemType.WHO: [
                r"谁", r"哪个人", r"什么人"
            ],
            ProblemType.YES_NO: [
                r"是不是", r"对不对", r"能不能", r"可不可以",
                r"是否", r"有没"
            ],
            ProblemType.COMPARISON: [
                r"和.*比", r"对比", r"区别", r"不同", r"哪个好"
            ],
        }
    
    def think(self, question: str) -> ThinkingResult:
        """思考一个问题"""
        thoughts = []
        
        # 第一步：理解问题
        step1 = self._understand(question)
        thoughts.append(step1)
        
        # 第二步：拆解问题
        step2, sub_questions = self._decompose(question, step1.content)
        thoughts.append(step2)
        
        # 第三步：定位核心
        step3, core = self._locate_core(question, sub_questions)
        thoughts.append(step3)
        
        # 第四步：分步解决
        step4, solutions = self._solve_step_by_step(core, sub_questions)
        thoughts.append(step4)
        
        # 第五步：输出答案
        step5, answer = self._formulate_answer(solutions)
        thoughts.append(step5)
        
        return ThinkingResult(
            problem_type=self._classify_problem(question),
            core_question=core,
            sub_questions=sub_questions,
            solution_steps=solutions,
            final_answer=answer,
            thoughts=thoughts
        )
    
    def _understand(self, question: str) -> Thought:
        """理解问题"""
        # 清理问题
        q = question.strip()
        
        # 识别问题类型
        ptype = self._classify_problem(q)
        
        content = f"这是一个【{ptype.value}】类问题"
        
        return Thought(
            step=1,
            action="理解问题",
            content=content,
            confidence=0.9
        )
    
    def _classify_problem(self, question: str) -> ProblemType:
        """分类问题"""
        for ptype, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, question):
                    return ptype
        return ProblemType.UNKNOWN
    
    def _decompose(self, question: str, understanding: str) -> Tuple[Thought, List[str]]:
        """拆解问题"""
        sub_questions = []
        
        # 根据问题类型拆解
        ptype = self._classify_problem(question)
        
        if ptype == ProblemType.WHAT:
            sub_questions = [
                f"定义：{question}的核心定义是什么？",
                f"特征：{question}有什么特点？",
                f"应用：{question}有什么用？"
            ]
        elif ptype == ProblemType.WHY:
            sub_questions = [
                "原因：直接原因是什么？",
                "背景：有什么背景因素？",
                "影响：会带来什么结果？"
            ]
        elif ptype == ProblemType.HOW:
            sub_questions = [
                "前提：需要什么条件？",
                "步骤：具体怎么做？",
                "注意：有什么要注意的？"
            ]
        elif ptype == ProblemType.YES_NO:
            sub_questions = [
                "判断：是还是不是？",
                "理由：为什么？",
                "例外：有什么特殊情况？"
            ]
        else:
            sub_questions = [question]
        
        content = f"拆解为{len(sub_questions)}个子问题"
        
        return Thought(
            step=2,
            action="拆解问题",
            content=content,
            confidence=0.8
        ), sub_questions
    
    def _locate_core(self, question: str, sub_questions: List[str]) -> Tuple[Thought, str]:
        """定位核心问题"""
        # 核心通常是第一个子问题
        if sub_questions:
            core = sub_questions[0]
        else:
            core = question
        
        return Thought(
            step=3,
            action="定位核心",
            content=f"核心问题：{core[:30]}...",
            confidence=0.85
        ), core
    
    def _solve_step_by_step(self, core: str, sub_questions: List[str]) -> Tuple[Thought, List[str]]:
        """分步解决"""
        solutions = []
        
        for i, sq in enumerate(sub_questions, 1):
            solutions.append(f"步骤{i}：解决「{sq[:20]}...」")
        
        return Thought(
            step=4,
            action="分步解决",
            content=f"共{len(solutions)}个解决步骤",
            confidence=0.75
        ), solutions
    
    def _formulate_answer(self, solutions: List[str]) -> Tuple[Thought, str]:
        """组织答案"""
        # 简单拼接
        answer = "\n".join(f"• {s}" for s in solutions[:3])
        
        return Thought(
            step=5,
            action="输出答案",
            content="答案已组织完成",
            confidence=0.8
        ), answer


class ProblemSolver:
    """问题解决器"""
    
    def __init__(self, thinking_engine: ThinkingEngine = None):
        self.thinking_engine = thinking_engine or ThinkingEngine()
    
    def solve(self, question: str) -> str:
        """解决一个问题"""
        result = self.thinking_engine.think(question)
        
        # 构建回答
        lines = []
        lines.append(f"【问题分析】")
        lines.append(f"类型：{result.problem_type.value}")
        lines.append(f"核心：{result.core_question[:50]}...")
        lines.append(f"")
        lines.append(f"【思考过程】")
        for thought in result.thoughts:
            lines.append(f"  {thought.step}. {thought.action}：{thought.content}")
        lines.append(f"")
        lines.append(f"【答案】")
        lines.append(result.final_answer)
        
        return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    engine = ThinkingEngine()
    solver = ProblemSolver(engine)
    
    questions = [
        "什么是人工智能？",
        "为什么天是蓝的？",
        "怎么学习Python？",
        "Python和Java哪个好？"
    ]
    
    for q in questions:
        print(f"\n{'='*50}")
        print(f"问题：{q}")
        print("="*50)
        print(solver.solve(q))
