#!/usr/bin/env python3
"""
小脑工厂 第二批 - 继续创建更多类型的小脑

新增类型：
- analysis (分析脑) - 50个
- learning (学习脑) - 50个
- emotion (情感脑) - 50个
- creativity (创意脑) - 50个
- dialogue (对话脑) - 50个

总计：250 + 250 = 500个小脑
"""

import os
import sys
import json
import pickle
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class LittleBrain:
    """小脑基类"""
    id: str
    brain_type: str
    knowledge: Dict[str, Any] = field(default_factory=dict)
    training_count: int = 0
    test_score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def learn(self, key: str, value: Any):
        """学习"""
        self.knowledge[key] = value
        self.training_count += 1
    
    def recall(self, key: str) -> Optional[Any]:
        """回忆"""
        return self.knowledge.get(key)
    
    def test(self, questions: List[tuple]) -> float:
        """测试"""
        correct = 0
        for q, a in questions:
            if self.recall(q) == a:
                correct += 1
        self.test_score = correct / len(questions) * 100 if questions else 0
        return self.test_score
    
    def save(self, path: str):
        """保存"""
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @classmethod
    def load(cls, path: str) -> 'LittleBrain':
        """加载"""
        with open(path, 'rb') as f:
            return pickle.load(f)


class BrainFactory:
    """小脑工厂"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.brains: List[LittleBrain] = []
        self.stats = {"total_created": 0, "total_trained": 0, "by_type": {}}
        os.makedirs(output_dir, exist_ok=True)
    
    def create_brain(self, brain_type: str, brain_id: int) -> LittleBrain:
        """创建单个小脑"""
        brain = LittleBrain(id=f"{brain_type}_{brain_id:03d}", brain_type=brain_type)
        self.stats["total_created"] += 1
        return brain
    
    def train_brain(self, brain: LittleBrain, data: List[tuple], rounds: int = 10):
        """训练单个小脑"""
        for _ in range(rounds):
            shuffled = data.copy()
            random.shuffle(shuffled)
            for item in shuffled:
                if len(item) >= 2:
                    key, value = item[0], item[1]
                    brain.learn(key, value)
        
        test_data = random.sample(data, min(20, len(data)))
        test_pairs = [(item[0], item[1]) for item in test_data]
        brain.test(test_pairs)
        self.stats["total_trained"] += 1
    
    def mass_create(self, brain_type: str, count: int, training_data: List[tuple]):
        """批量创建和训练"""
        print(f"\n创建 {count} 个 {brain_type}...")
        
        type_dir = os.path.join(self.output_dir, brain_type)
        os.makedirs(type_dir, exist_ok=True)
        
        brains = []
        scores = []
        
        for i in range(1, count + 1):
            brain = self.create_brain(brain_type, i)
            rounds = random.randint(5, 20)
            self.train_brain(brain, training_data, rounds)
            brain.save(os.path.join(type_dir, f"{brain.id}.pkl"))
            brains.append(brain)
            scores.append(brain.test_score)
            
            if i % 10 == 0:
                avg_score = sum(scores[-10:]) / 10
                print(f"  {i}/{count} 完成, 最近10个平均分: {avg_score:.1f}%")
        
        self.stats["by_type"][brain_type] = {
            "count": count,
            "avg_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "min_score": min(scores)
        }
        self.brains.extend(brains)
        return brains, scores
    
    def get_top_brains(self, brain_type: str, top_n: int = 10) -> List[LittleBrain]:
        """获取某类型最强的N个小脑"""
        type_brains = [b for b in self.brains if b.brain_type == brain_type]
        sorted_brains = sorted(type_brains, key=lambda x: x.test_score, reverse=True)
        return sorted_brains[:top_n]
    
    def save_stats(self):
        """保存统计"""
        stats_path = os.path.join(self.output_dir, "factory_stats.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)


# ==================== 训练数据 ====================

ANALYSIS_TRAINING_DATA = [
    ("什么是人工智能", "定义类问题"),
    ("为什么学习编程", "原因类问题"),
    ("怎么学习Python", "方法类问题"),
    ("Python和Java哪个好", "比较类问题"),
    ("编程难学吗", "判断类问题"),
    ("AI未来会怎样", "预测类问题"),
    ("如何提高效率", "优化类问题"),
    ("代码为什么报错", "调试类问题"),
    ("什么是机器学习", "定义类问题"),
    ("为什么Python受欢迎", "原因类问题"),
    ("如何写好代码", "方法类问题"),
    ("前端后端区别", "比较类问题"),
    ("这个方案可行吗", "判断类问题"),
    ("技术发展趋势", "预测类问题"),
    ("怎么优化算法", "优化类问题"),
]

LEARNING_TRAINING_DATA = [
    ("编程入门", "从Python开始每天写代码"),
    ("Python基础", "多写小程序理解概念"),
    ("Web开发", "先静态后动态"),
    ("数据库", "理解模型多写SQL"),
    ("算法", "理解原理手动实现"),
    ("Git使用", "每天用理解工作流"),
    ("调试技巧", "先理解问题再定位"),
    ("代码规范", "遵循PEP8保持一致"),
    ("学习方法", "明确目标小步快跑"),
    ("时间管理", "重要的事先做"),
]

EMOTION_TRAINING_DATA = [
    ("我今天很开心", "高兴听到这个"),
    ("这件事让我难过", "抱歉听到这个"),
    ("我很生气", "理解你的感受"),
    ("我有点焦虑", "焦虑是正常的"),
    ("我不太明白", "我来帮你理清"),
    ("太激动了", "太棒了"),
    ("今天真倒霉", "明天会更好"),
    ("我好累啊", "记得休息"),
    ("这个问题困扰我", "我们一起分析"),
    ("终于成功了", "恭喜你"),
]

CREATIVITY_TRAINING_DATA = [
    ("编程", "如何让编程更有趣"),
    ("学习", "如何让学习更高效"),
    ("工作", "如何让工作更有意义"),
    ("生活", "如何让生活更美好"),
    ("创业", "如何发现创业机会"),
    ("写作", "如何写出好文章"),
    ("设计", "如何做出好设计"),
    ("营销", "如何做好营销"),
    ("产品", "如何打造好产品"),
    ("团队", "如何建设好团队"),
]

DIALOGUE_TRAINING_DATA = [
    ("你好", "你好有什么可以帮助你"),
    ("谢谢", "不客气还有其他问题吗"),
    ("再见", "再见祝你一切顺利"),
    ("什么是AI", "AI是人工智能技术"),
    ("怎么学习", "从基础开始循序渐进"),
    ("你叫什么", "我是天光模型小助手"),
    ("你能做什么", "回答问题提供建议"),
    ("今天天气", "无法获取实时天气"),
    ("讲个笑话", "程序员喜欢暗黑模式"),
    ("我很无聊", "可以学点新东西"),
]


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║            小脑工厂 第二批 - 继续创建                  ║
╠══════════════════════════════════════════════════════════╣
║  目标：再创建250个小脑，总计500个                    ║
╚══════════════════════════════════════════════════════════╝
""")
    
    factory = BrainFactory("/home/z/tianguang_model/little_brains/brain_instances")
    
    configs = [
        ("analysis", 50, ANALYSIS_TRAINING_DATA),
        ("learning", 50, LEARNING_TRAINING_DATA),
        ("emotion", 50, EMOTION_TRAINING_DATA),
        ("creativity", 50, CREATIVITY_TRAINING_DATA),
        ("dialogue", 50, DIALOGUE_TRAINING_DATA),
    ]
    
    all_results = {}
    
    for brain_type, count, data in configs:
        brains, scores = factory.mass_create(brain_type, count, data)
        all_results[brain_type] = {
            "count": count,
            "avg_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "top_brains": [b.id for b in factory.get_top_brains(brain_type, 5)]
        }
    
    factory.save_stats()
    
    print("\n" + "="*60)
    print("  第二批结果")
    print("="*60)
    
    for brain_type, result in all_results.items():
        print(f"\n  {brain_type}:")
        print(f"    数量: {result['count']}")
        print(f"    平均分: {result['avg_score']:.1f}%")
        print(f"    最高分: {result['max_score']:.1f}%")
    
    print("\n" + "="*60)
    print(f"  总计创建: {factory.stats['total_created']} 个小脑")
    print("="*60)
    
    # 统计总数
    total_brains = 0
    for dirpath, dirnames, filenames in os.walk("/home/z/tianguang_model/little_brains/brain_instances"):
        total_brains += len([f for f in filenames if f.endswith('.pkl')])
    
    print(f"\n✅ 第二批完成！总小脑数: {total_brains}")


if __name__ == "__main__":
    main()
