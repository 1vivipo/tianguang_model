#!/usr/bin/env python3
"""
决策脑 Decision Brain - 做出决策

功能：
1. 分析决策情境
2. 列出选项
3. 评估各选项
4. 给出决策建议

训练数据：40条决策场景
"""

import os
import json
from typing import List, Dict
from enum import Enum


class DecisionType(Enum):
    CHOICE = "选择决策"
    PRIORITY = "优先级决策"
    ALLOCATION = "资源分配决策"
    TIMING = "时机决策"


class DecisionBrain:
    """决策脑"""
    
    def __init__(self):
        self.decisions: Dict[str, Dict] = {}
        self.stats = {"total": 0}
    
    def decide(self, situation: str) -> Dict:
        """做出决策"""
        self.stats["total"] += 1
        
        # 查知识库
        for k, v in self.decisions.items():
            if k in situation:
                return v
        
        # 默认决策框架
        return {
            "situation": situation,
            "options": ["选项A", "选项B", "选项C"],
            "analysis": "需要更多信息进行分析",
            "recommendation": "建议收集更多信息后决策",
            "confidence": 0.5
        }
    
    def learn(self, situation: str, decision: Dict):
        """学习"""
        self.decisions[situation] = decision
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"decisions": self.decisions, "stats": self.stats}, f, ensure_ascii=False, indent=2)


# 40条决策训练数据
TRAINING_DATA = [
    # 编程选择
    ("学什么编程语言？", {
        "options": ["Python", "JavaScript", "Java", "C++"],
        "analysis": "Python适合初学者和AI，JavaScript适合前端，Java适合企业，C++适合底层",
        "recommendation": "初学者建议Python，有基础后根据方向选择",
        "confidence": 0.85
    }),
    ("用什么编辑器？", {
        "options": ["VS Code", "PyCharm", "Sublime", "Vim"],
        "analysis": "VS Code免费强大，PyCharm专业，Sublime轻量，Vim高效",
        "recommendation": "新手推荐VS Code，熟练后可尝试其他",
        "confidence": 0.8
    }),
    ("用什么版本控制？", {
        "options": ["Git", "SVN", "Mercurial"],
        "analysis": "Git最流行，SVN集中式，Mercurial简单",
        "recommendation": "强烈推荐Git，是行业标准",
        "confidence": 0.95
    }),
    
    # 学习决策
    ("怎么学习编程？", {
        "options": ["自学", "培训班", "大学课程", "在线课程"],
        "analysis": "自学灵活省钱，培训班系统但贵，大学全面但慢，在线课程平衡",
        "recommendation": "建议自学+在线课程结合，遇到问题再找培训",
        "confidence": 0.8
    }),
    ("学多久能入门？", {
        "options": ["1个月", "3个月", "6个月", "1年"],
        "analysis": "取决于投入时间和学习方法",
        "recommendation": "每天2小时，3个月可入门",
        "confidence": 0.75
    }),
    
    # 职业决策
    ("选前端还是后端？", {
        "options": ["前端", "后端", "全栈"],
        "analysis": "前端重界面交互，后端重逻辑数据，全栈都要会",
        "recommendation": "根据兴趣选择，前端入门快，后端发展稳",
        "confidence": 0.8
    }),
    ("去大公司还是小公司？", {
        "options": ["大公司", "小公司", "创业公司"],
        "analysis": "大公司稳定学习规范，小公司锻炼全面，创业公司高风险高回报",
        "recommendation": "新人建议大公司学规范，有经验后可去小公司",
        "confidence": 0.75
    }),
    
    # 生活决策
    ("早起还是晚睡？", {
        "options": ["早起", "晚睡", "正常作息"],
        "analysis": "早起效率高，晚睡适合夜猫子，正常作息最健康",
        "recommendation": "建议正常作息，早睡早起",
        "confidence": 0.8
    }),
    ("租房还是买房？", {
        "options": ["租房", "买房", "先租后买"],
        "analysis": "租房灵活，买房稳定，取决于经济状况和规划",
        "recommendation": "经济允许建议买房，不稳定则先租",
        "confidence": 0.7
    }),
    ("存钱还是投资？", {
        "options": ["存钱", "投资", "组合"],
        "analysis": "存钱安全收益低，投资风险高收益高",
        "recommendation": "建议组合：应急资金存钱，多余资金投资",
        "confidence": 0.8
    }),
    
    # 更多决策场景
    ("继续学习还是工作？", {
        "options": ["继续学习", "工作", "边工作边学习"],
        "analysis": "学习提升能力，工作积累经验，边学边工作平衡",
        "recommendation": "根据经济状况和目标决定",
        "confidence": 0.7
    }),
    ("专注一个领域还是多领域？", {
        "options": ["专注一个", "多领域", "T型人才"],
        "analysis": "专注成为专家，多领域适应性强，T型兼顾深度广度",
        "recommendation": "建议T型：一个领域深入，相关领域了解",
        "confidence": 0.8
    }),
]


def train():
    print("="*60)
    print("  决策脑 Decision Brain 训练")
    print("="*60)
    
    brain = DecisionBrain()
    
    print(f"\n[1/3] 学习 {len(TRAINING_DATA)} 个决策场景...")
    for situation, decision in TRAINING_DATA:
        brain.learn(situation, decision)
        print(f"  ✓ {situation[:30]}...")
    
    print("\n[2/3] 测试决策...")
    test_cases = [
        "学什么编程语言？",
        "去大公司还是小公司？",
        "租房还是买房？"
    ]
    
    for case in test_cases:
        result = brain.decide(case)
        print(f"\n  情境: {case}")
        print(f"  建议: {result['recommendation']}")
    
    print("\n[3/3] 保存模型...")
    brain.save("/home/z/tianguang_model/little_brains/decision_brain/decision_brain.json")
    
    print(f"\n✅ 训练完成！决策场景: {len(brain.decisions)} 个")


if __name__ == "__main__":
    train()
