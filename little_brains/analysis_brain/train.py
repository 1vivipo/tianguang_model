#!/usr/bin/env python3
"""
分析脑 Analysis Brain - 拆解问题

功能：
1. 识别问题类型
2. 拆解复杂问题
3. 找出核心问题
4. 制定解决步骤

训练目标：
- 能够拆解复杂问题
- 准确识别核心问题
- 给出清晰的解决步骤

大小目标：~5MB
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class ProblemType(Enum):
    """问题类型"""
    DEFINITION = "定义类"      # 是什么
    REASON = "原因类"          # 为什么
    METHOD = "方法类"          # 怎么做
    COMPARISON = "比较类"      # 哪个好
    JUDGMENT = "判断类"        # 是不是
    PREDICTION = "预测类"      # 会怎样
    OPTIMIZATION = "优化类"    # 如何更好
    DEBUG = "调试类"           # 哪里错了


@dataclass
class AnalysisResult:
    """分析结果"""
    original_problem: str
    problem_type: ProblemType
    core_question: str
    sub_questions: List[str]
    key_factors: List[str]
    solution_steps: List[str]
    priority: int  # 1-5，5最重要


class AnalysisBrain:
    """分析脑"""
    
    def __init__(self):
        # 问题模式
        self.patterns = {
            ProblemType.DEFINITION: [r"什么是", r"是什么", r"什么叫", r"定义"],
            ProblemType.REASON: [r"为什么", r"为何", r"原因", r"怎么会"],
            ProblemType.METHOD: [r"怎么", r"如何", r"怎样", r"方法", r"步骤"],
            ProblemType.COMPARISON: [r"哪个好", r"区别", r"对比", r"还是"],
            ProblemType.JUDGMENT: [r"是不是", r"对不对", r"能否", r"是否"],
            ProblemType.PREDICTION: [r"会怎样", r"将来", r"预测", r"可能"],
            ProblemType.OPTIMIZATION: [r"如何更好", r"优化", r"改进", r"提升"],
            ProblemType.DEBUG: [r"哪里错", r"为什么不行", r"问题", r"报错"],
        }
        
        # 分析模板
        self.templates = {
            ProblemType.DEFINITION: self._analyze_definition,
            ProblemType.REASON: self._analyze_reason,
            ProblemType.METHOD: self._analyze_method,
            ProblemType.COMPARISON: self._analyze_comparison,
            ProblemType.JUDGMENT: self._analyze_judgment,
            ProblemType.PREDICTION: self._analyze_prediction,
            ProblemType.OPTIMIZATION: self._analyze_optimization,
            ProblemType.DEBUG: self._analyze_debug,
        }
        
        # 统计
        self.stats = {
            "total_analyses": 0,
            "successful_analyses": 0
        }
    
    def analyze(self, problem: str) -> AnalysisResult:
        """分析问题"""
        self.stats["total_analyses"] += 1
        
        # 识别问题类型
        problem_type = self._identify_type(problem)
        
        # 使用对应模板分析
        if problem_type in self.templates:
            result = self.templates[problem_type](problem)
        else:
            result = self._analyze_general(problem)
        
        self.stats["successful_analyses"] += 1
        
        return result
    
    def _identify_type(self, problem: str) -> ProblemType:
        """识别问题类型"""
        for ptype, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, problem):
                    return ptype
        return ProblemType.DEFINITION
    
    def _analyze_definition(self, problem: str) -> AnalysisResult:
        """分析定义类问题"""
        # 提取核心概念
        concept = re.sub(r"什么是|是什么|什么叫|定义", "", problem)
        concept = concept.replace("？", "").replace("?", "").strip()
        
        return AnalysisResult(
            original_problem=problem,
            problem_type=ProblemType.DEFINITION,
            core_question=f"{concept}是什么？",
            sub_questions=[
                f"{concept}的定义是什么？",
                f"{concept}有什么特点？",
                f"{concept}有什么用途？"
            ],
            key_factors=["定义", "特点", "用途"],
            solution_steps=[
                "1. 给出标准定义",
                "2. 说明主要特点",
                "3. 介绍应用场景"
            ],
            priority=3
        )
    
    def _analyze_reason(self, problem: str) -> AnalysisResult:
        """分析原因类问题"""
        # 提取核心事件
        event = re.sub(r"为什么|为何|原因|怎么会", "", problem)
        event = event.replace("？", "").replace("?", "").strip()
        
        return AnalysisResult(
            original_problem=problem,
            problem_type=ProblemType.REASON,
            core_question=f"为什么{event}？",
            sub_questions=[
                "直接原因是什么？",
                "根本原因是什么？",
                "有什么背景因素？"
            ],
            key_factors=["直接原因", "根本原因", "背景因素"],
            solution_steps=[
                "1. 分析直接原因",
                "2. 追溯根本原因",
                "3. 考虑背景因素",
                "4. 总结因果关系"
            ],
            priority=4
        )
    
    def _analyze_method(self, problem: str) -> AnalysisResult:
        """分析方法类问题"""
        # 提取目标
        goal = re.sub(r"怎么|如何|怎样|方法|步骤", "", problem)
        goal = goal.replace("？", "").replace("?", "").strip()
        
        return AnalysisResult(
            original_problem=problem,
            problem_type=ProblemType.METHOD,
            core_question=f"如何{goal}？",
            sub_questions=[
                "需要什么前提条件？",
                "具体步骤是什么？",
                "有什么注意事项？"
            ],
            key_factors=["前提条件", "具体步骤", "注意事项"],
            solution_steps=[
                "1. 确认前提条件",
                "2. 列出具体步骤",
                "3. 说明注意事项",
                "4. 给出示例"
            ],
            priority=5
        )
    
    def _analyze_comparison(self, problem: str) -> AnalysisResult:
        """分析比较类问题"""
        # 提取比较对象
        objects = re.findall(r"[\u4e00-\u9fff]+", problem)
        objects = [o for o in objects if len(o) > 1 and o not in ["哪个", "区别", "对比"]][:2]
        
        return AnalysisResult(
            original_problem=problem,
            problem_type=ProblemType.COMPARISON,
            core_question=f"{'和'.join(objects)}有什么区别？",
            sub_questions=[
                f"{objects[0] if objects else 'A'}有什么特点？",
                f"{objects[1] if len(objects) > 1 else 'B'}有什么特点？",
                "哪个更适合？"
            ],
            key_factors=["各自特点", "相同点", "不同点", "适用场景"],
            solution_steps=[
                "1. 分析各自特点",
                "2. 找出相同点",
                "3. 找出不同点",
                "4. 给出选择建议"
            ],
            priority=4
        )
    
    def _analyze_judgment(self, problem: str) -> AnalysisResult:
        """分析判断类问题"""
        return AnalysisResult(
            original_problem=problem,
            problem_type=ProblemType.JUDGMENT,
            core_question="是还是不是？",
            sub_questions=[
                "判断依据是什么？",
                "有什么支持证据？",
                "有什么反对证据？"
            ],
            key_factors=["判断依据", "支持证据", "反对证据"],
            solution_steps=[
                "1. 明确判断标准",
                "2. 收集证据",
                "3. 权衡利弊",
                "4. 给出判断"
            ],
            priority=4
        )
    
    def _analyze_prediction(self, problem: str) -> AnalysisResult:
        """分析预测类问题"""
        return AnalysisResult(
            original_problem=problem,
            problem_type=ProblemType.PREDICTION,
            core_question="未来会怎样？",
            sub_questions=[
                "当前趋势是什么？",
                "有哪些影响因素？",
                "可能的结果有哪些？"
            ],
            key_factors=["当前趋势", "影响因素", "可能结果"],
            solution_steps=[
                "1. 分析当前趋势",
                "2. 识别影响因素",
                "3. 预测可能结果",
                "4. 说明不确定性"
            ],
            priority=3
        )
    
    def _analyze_optimization(self, problem: str) -> AnalysisResult:
        """分析优化类问题"""
        return AnalysisResult(
            original_problem=problem,
            problem_type=ProblemType.OPTIMIZATION,
            core_question="如何做得更好？",
            sub_questions=[
                "当前状况如何？",
                "有什么问题？",
                "如何改进？"
            ],
            key_factors=["现状分析", "问题识别", "改进方案"],
            solution_steps=[
                "1. 分析当前状况",
                "2. 识别问题",
                "3. 提出改进方案",
                "4. 评估效果"
            ],
            priority=5
        )
    
    def _analyze_debug(self, problem: str) -> AnalysisResult:
        """分析调试类问题"""
        return AnalysisResult(
            original_problem=problem,
            problem_type=ProblemType.DEBUG,
            core_question="问题出在哪里？",
            sub_questions=[
                "期望结果是什么？",
                "实际结果是什么？",
                "差异在哪里？"
            ],
            key_factors=["期望结果", "实际结果", "差异分析"],
            solution_steps=[
                "1. 明确期望结果",
                "2. 确认实际结果",
                "3. 分析差异原因",
                "4. 提出解决方案"
            ],
            priority=5
        )
    
    def _analyze_general(self, problem: str) -> AnalysisResult:
        """通用分析"""
        return AnalysisResult(
            original_problem=problem,
            problem_type=ProblemType.DEFINITION,
            core_question=problem,
            sub_questions=["这是什么问题？", "关键点是什么？"],
            key_factors=["问题本身"],
            solution_steps=["1. 理解问题", "2. 分析关键点", "3. 给出回答"],
            priority=3
        )
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            **self.stats,
            "success_rate": self.stats["successful_analyses"] / max(1, self.stats["total_analyses"])
        }
    
    def save(self, path: str):
        """保存"""
        data = {
            "stats": self.stats
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, path: str):
        """加载"""
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.stats = data.get("stats", self.stats)


# ==================== 训练数据 ====================

TRAINING_DATA = [
    {"problem": "什么是人工智能？", "type": "定义类"},
    {"problem": "为什么学习编程？", "type": "原因类"},
    {"problem": "怎么学习Python？", "type": "方法类"},
    {"problem": "Python和Java哪个好？", "type": "比较类"},
    {"problem": "编程难学吗？", "type": "判断类"},
    {"problem": "AI未来会怎样？", "type": "预测类"},
    {"problem": "如何提高编程效率？", "type": "优化类"},
    {"problem": "代码为什么报错？", "type": "调试类"},
    {"problem": "什么是机器学习？", "type": "定义类"},
    {"problem": "为什么Python受欢迎？", "type": "原因类"},
    {"problem": "如何写好代码？", "type": "方法类"},
    {"problem": "前端和后端有什么区别？", "type": "比较类"},
    {"problem": "这个方案可行吗？", "type": "判断类"},
    {"problem": "技术发展趋势如何？", "type": "预测类"},
    {"problem": "怎么优化算法？", "type": "优化类"},
]


def train_analysis_brain():
    """训练分析脑"""
    print("""
╔══════════════════════════════════════════════════════════╗
║            分析脑 Analysis Brain 训练                  ║
╠══════════════════════════════════════════════════════════╣
║  目标：拆解问题                                        ║
║  大小：~5MB                                            ║
║  数据：{} 条问题                                       ║
╚══════════════════════════════════════════════════════════╝
""".format(len(TRAINING_DATA)))
    
    brain = AnalysisBrain()
    
    # 测试分析
    print("\n[1/3] 测试问题分析...")
    for item in TRAINING_DATA:
        result = brain.analyze(item["problem"])
        print(f"\n  问题: {item['problem']}")
        print(f"  类型: {result.problem_type.value}")
        print(f"  核心: {result.core_question}")
        print(f"  子问题: {len(result.sub_questions)}个")
    
    # 详细测试几个
    print("\n[2/3] 详细分析测试...")
    test_problems = [
        "怎么学习编程？",
        "为什么Python受欢迎？",
        "前端和后端有什么区别？"
    ]
    
    for problem in test_problems:
        result = brain.analyze(problem)
        print(f"\n{'='*50}")
        print(f"问题: {problem}")
        print(f"类型: {result.problem_type.value}")
        print(f"核心问题: {result.core_question}")
        print(f"子问题:")
        for sq in result.sub_questions:
            print(f"  - {sq}")
        print(f"解决步骤:")
        for step in result.solution_steps:
            print(f"  {step}")
    
    # 保存
    print("\n[3/3] 保存模型...")
    brain.save("/home/z/tianguang_model/little_brains/analysis_brain/analysis_brain.json")
    
    # 统计
    stats = brain.get_stats()
    print(f"\n✅ 训练完成！")
    print(f"   分析次数: {stats['total_analyses']}")
    print(f"   成功率: {stats['success_rate']:.1%}")
    
    return brain


if __name__ == "__main__":
    train_analysis_brain()
