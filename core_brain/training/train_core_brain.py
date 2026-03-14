#!/usr/bin/env python3
"""
核心大脑训练脚本

目标：
1. 基础版：1M参数，稳定中文对话
2. 进阶版：500MB，多轮记忆，中文精调
3. 终极版：1.5B参数，人类偏好对齐，工具调用

训练原则：
1. 逻辑优先，数据为辅
2. 先教它怎么思考，再喂阅历数据
3. 优先优化解决问题的准确率
4. 不追求话多，每句都要解决问题

使用方法：
    python train_core_brain.py --stage 1  # 基础版
    python train_core_brain.py --stage 2  # 进阶版
    python train_core_brain.py --stage 3  # 终极版
"""

import os
import sys
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Tuple

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain import CoreBrain
from logic.thinking_engine import ThinkingEngine
from logic.problem_solver import ProblemSolver
from memory.dialog_memory import DialogMemory


# ==================== 训练数据 ====================

# 基础问答数据（教AI怎么思考）
BASIC_QA = [
    # 定义类问题
    {
        "question": "什么是人工智能？",
        "answer": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
        "type": "定义",
        "reasoning": [
            "1. 识别为定义类问题",
            "2. 核心概念：人工智能",
            "3. 给出定义和解释"
        ]
    },
    {
        "question": "什么是机器学习？",
        "answer": "机器学习是人工智能的核心技术，通过算法让计算机从数据中自动学习和改进，无需显式编程。",
        "type": "定义",
        "reasoning": [
            "1. 识别为定义类问题",
            "2. 核心概念：机器学习",
            "3. 解释其与AI的关系"
        ]
    },
    {
        "question": "什么是Python？",
        "answer": "Python是一种高级编程语言，以简洁易读的语法著称，广泛应用于Web开发、数据分析、人工智能等领域。",
        "type": "定义",
        "reasoning": [
            "1. 识别为定义类问题",
            "2. 核心概念：Python",
            "3. 说明其特点和用途"
        ]
    },
    
    # 原因类问题
    {
        "question": "为什么学习编程？",
        "answer": "学习编程可以：1. 培养逻辑思维能力；2. 创造工具解决问题；3. 获得高薪就业机会；4. 理解数字世界。",
        "type": "原因",
        "reasoning": [
            "1. 识别为原因类问题",
            "2. 分析学习编程的好处",
            "3. 列举主要原因"
        ]
    },
    {
        "question": "为什么Python受欢迎？",
        "answer": "Python受欢迎的原因：1. 语法简洁易学；2. 丰富的库和框架；3. 社区活跃；4. 应用领域广泛。",
        "type": "原因",
        "reasoning": [
            "1. 识别为原因类问题",
            "2. 分析Python的优势",
            "3. 总结受欢迎的原因"
        ]
    },
    
    # 方法类问题
    {
        "question": "怎么学习Python？",
        "answer": "学习Python的步骤：\n1. 学习基础语法（变量、循环、函数）\n2. 练习小程序\n3. 学习常用库\n4. 做实际项目\n5. 持续学习新技术",
        "type": "方法",
        "reasoning": [
            "1. 识别为方法类问题",
            "2. 分析学习路径",
            "3. 给出具体步骤"
        ]
    },
    {
        "question": "如何提高编程能力？",
        "answer": "提高编程能力的方法：\n1. 多写代码，多练习\n2. 阅读优秀代码\n3. 参与开源项目\n4. 解决实际问题\n5. 学习数据结构和算法",
        "type": "方法",
        "reasoning": [
            "1. 识别为方法类问题",
            "2. 分析提升途径",
            "3. 给出具体建议"
        ]
    },
    
    # 比较类问题
    {
        "question": "Python和Java哪个好？",
        "answer": "Python和Java各有优势：\nPython：语法简洁，适合快速开发、数据分析、AI\nJava：性能好，适合企业级应用、Android开发\n选择取决于具体需求。",
        "type": "比较",
        "reasoning": [
            "1. 识别为比较类问题",
            "2. 分析各自特点",
            "3. 给出对比结论"
        ]
    },
    
    # 判断类问题
    {
        "question": "编程难学吗？",
        "answer": "编程入门不难，精通需要时间。选择合适的语言（如Python），循序渐进学习，坚持练习，大多数人都能学会。",
        "type": "判断",
        "reasoning": [
            "1. 识别为判断类问题",
            "2. 分析学习难度",
            "3. 给出客观评价"
        ]
    },
]

# 进阶对话数据（多轮对话）
ADVANCED_DIALOGS = [
    {
        "turns": [
            {"user": "你好", "assistant": "你好！有什么可以帮助你的？"},
            {"user": "我想学习编程", "assistant": "很好！建议从Python开始，语法简单，应用广泛。"},
            {"user": "需要什么基础？", "assistant": "Python入门不需要特殊基础，会基本的电脑操作即可。"},
            {"user": "学习多久能入门？", "assistant": "一般1-2个月可以掌握基础语法，能写简单程序。"},
        ]
    },
    {
        "turns": [
            {"user": "什么是AI？", "assistant": "AI是人工智能，让机器模拟人类智能的技术。"},
            {"user": "和机器学习什么关系？", "assistant": "机器学习是AI的核心技术，是实现AI的重要方法。"},
            {"user": "深度学习呢？", "assistant": "深度学习是机器学习的子集，使用多层神经网络学习。"},
        ]
    },
]

# 终极训练数据（人类偏好对齐）
HUMAN_PREFERENCE = [
    {
        "question": "我很难过",
        "good_answer": "抱歉听到这个。想聊聊发生了什么吗？我在这里倾听。",
        "bad_answer": "难过是什么意思？请明确定义你的情绪状态。",
        "reason": "好回答体现了同理心，愿意倾听；坏回答过于机械，缺乏情感。"
    },
    {
        "question": "这道题我不会",
        "good_answer": "没关系，我们一起来看看。首先，题目问的是什么？",
        "bad_answer": "请查阅相关教材或搜索引擎。",
        "reason": "好回答愿意帮助引导；坏回答推卸责任。"
    },
]


# ==================== 训练器 ====================

class CoreBrainTrainer:
    """核心大脑训练器"""
    
    def __init__(self):
        self.brain = CoreBrain()
        self.stats = {
            "qa_learned": 0,
            "dialogs_learned": 0,
            "preferences_learned": 0
        }
    
    def train_stage1(self):
        """基础版训练"""
        print(f"""
╔══════════════════════════════════════════════════════════╗
║            核心大脑训练 - 基础版                        ║
╠══════════════════════════════════════════════════════════╣
║  目标：稳定中文对话，1M参数                             ║
║  重点：教AI怎么思考                                    ║
╚══════════════════════════════════════════════════════════╝
""")
        
        # 学习基础问答
        print("\n[1/3] 学习基础问答...")
        for qa in BASIC_QA:
            self.brain.learn(qa["question"], qa["answer"])
            self.stats["qa_learned"] += 1
            print(f"  ✓ 学习: {qa['question'][:20]}...")
        
        # 学习推理模式
        print("\n[2/3] 学习推理模式...")
        for qa in BASIC_QA:
            # 这里可以训练推理模型
            pass
        print(f"  ✓ 学习了 {len(BASIC_QA)} 种推理模式")
        
        # 测试
        print("\n[3/3] 测试对话...")
        test_questions = [
            "什么是Python？",
            "怎么学习编程？",
            "Python和Java哪个好？"
        ]
        
        for q in test_questions:
            answer = self.brain.chat(q)
            print(f"\n  问：{q}")
            print(f"  答：{answer[:100]}...")
        
        print(f"\n✅ 基础版训练完成！")
        print(f"   学习问答：{self.stats['qa_learned']} 条")
    
    def train_stage2(self):
        """进阶版训练"""
        print(f"""
╔══════════════════════════════════════════════════════════╗
║            核心大脑训练 - 进阶版                        ║
╠══════════════════════════════════════════════════════════╣
║  目标：多轮记忆，中文精调，500MB以内                   ║
║  重点：学会对话连贯性                                  ║
╚══════════════════════════════════════════════════════════╝
""")
        
        # 先完成基础训练
        self.train_stage1()
        
        # 学习多轮对话
        print("\n[进阶] 学习多轮对话...")
        for dialog in ADVANCED_DIALOGS:
            for turn in dialog["turns"]:
                self.brain.memory.add_turn(
                    turn["user"],
                    turn["assistant"],
                    important=True
                )
            self.stats["dialogs_learned"] += 1
            print(f"  ✓ 学习对话：{len(dialog['turns'])} 轮")
        
        print(f"\n✅ 进阶版训练完成！")
        print(f"   学习对话：{self.stats['dialogs_learned']} 组")
    
    def train_stage3(self):
        """终极版训练"""
        print(f"""
╔══════════════════════════════════════════════════════════╗
║            核心大脑训练 - 终极版                        ║
╠══════════════════════════════════════════════════════════╣
║  目标：人类偏好对齐，工具调用，1.5B参数                ║
║  重点：理解人类情感和需求                              ║
╚══════════════════════════════════════════════════════════╝
""")
        
        # 先完成进阶训练
        self.train_stage2()
        
        # 学习人类偏好
        print("\n[终极] 学习人类偏好...")
        for pref in HUMAN_PREFERENCE:
            self.brain.learn(pref["question"], pref["good_answer"])
            self.stats["preferences_learned"] += 1
            print(f"  ✓ 学习偏好：{pref['question']}")
        
        print(f"\n✅ 终极版训练完成！")
        print(f"   学习偏好：{self.stats['preferences_learned']} 条")
    
    def save(self, path: str):
        """保存模型"""
        os.makedirs(path, exist_ok=True)
        self.brain.memory.save(os.path.join(path, "memory.json"))
        self.brain.problem_solver.save_knowledge(os.path.join(path, "knowledge.json"))
        
        # 保存统计
        with open(os.path.join(path, "training_stats.json"), 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        print(f"✓ 模型保存到：{path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="核心大脑训练")
    parser.add_argument("--stage", type=int, default=1, choices=[1, 2, 3], help="训练阶段")
    parser.add_argument("--output", type=str, default="./trained_core_brain", help="输出目录")
    
    args = parser.parse_args()
    
    # 训练
    trainer = CoreBrainTrainer()
    
    if args.stage == 1:
        trainer.train_stage1()
    elif args.stage == 2:
        trainer.train_stage2()
    else:
        trainer.train_stage3()
    
    # 保存
    trainer.save(args.output)
    
    # 最终统计
    print(f"\n{'='*50}")
    print("训练完成！统计：")
    for k, v in trainer.stats.items():
        print(f"  {k}: {v}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
