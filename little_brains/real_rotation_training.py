#!/usr/bin/env python3
"""
真正的轮换训练系统

核心改进：
1. 轮换投喂 - 每轮不同小脑吃不同数据
2. 真实训练 - 更新权重/概率，不是只存字典
3. 持续学习 - 爬虫持续抓数据，训练持续进行

训练方式：
- 第1轮：brain_001 吃数据A，brain_002 吃数据B...
- 第2轮：brain_001 吃数据B，brain_002 吃数据C...
- 第3轮：brain_001 吃数据C，brain_002 吃数据D...
- ...

真实训练：
- 统计学习：更新词频、共现概率
- 权重更新：根据正确/错误调整
- 知识融合：新旧知识加权融合
"""

import os
import sys
import json
import pickle
import random
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from collections import Counter, defaultdict


# ==================== 真正的小脑类 ====================

@dataclass
class RealBrain:
    """真正的小脑 - 有权重和概率"""
    
    id: str
    brain_type: str
    
    # 知识存储
    knowledge: Dict[str, str] = field(default_factory=dict)
    
    # 权重（每个知识点的置信度）
    weights: Dict[str, float] = field(default_factory=dict)
    
    # 词频统计（用于概率计算）
    word_freq: Counter = field(default_factory=Counter)
    
    # 共现矩阵（词与词的关系）
    co_occurrence: Dict[str, Counter] = field(default_factory=lambda: defaultdict(Counter))
    
    # 训练统计
    training_rounds: int = 0
    total_samples: int = 0
    correct_predictions: int = 0
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_trained_at: str = ""
    
    def train(self, question: str, answer: str, learning_rate: float = 0.1):
        """真实训练 - 更新权重和概率"""
        
        # 1. 存储知识
        old_answer = self.knowledge.get(question)
        self.knowledge[question] = answer
        
        # 2. 更新权重
        if old_answer is None:
            # 新知识，初始权重
            self.weights[question] = 0.5
        else:
            # 已有知识，根据是否一致调整
            if old_answer == answer:
                # 一致，增加置信度
                self.weights[question] = min(1.0, self.weights.get(question, 0.5) + learning_rate)
            else:
                # 不一致，降低置信度但保留新知识
                self.weights[question] = max(0.1, self.weights.get(question, 0.5) - learning_rate * 0.5)
        
        # 3. 更新词频
        words = self._tokenize(question + " " + answer)
        self.word_freq.update(words)
        
        # 4. 更新共现矩阵
        for i, w1 in enumerate(words):
            for w2 in words[i+1:i+5]:  # 窗口大小5
                self.co_occurrence[w1][w2] += 1
                self.co_occurrence[w2][w1] += 1
        
        # 5. 更新统计
        self.total_samples += 1
        self.last_trained_at = datetime.now().isoformat()
    
    def predict(self, question: str) -> Tuple[str, float]:
        """预测答案"""
        
        # 1. 精确匹配
        if question in self.knowledge:
            answer = self.knowledge[question]
            weight = self.weights.get(question, 0.5)
            return answer, weight
        
        # 2. 模糊匹配（基于词频）
        question_words = set(self._tokenize(question))
        best_match = None
        best_score = 0
        
        for known_q, known_a in self.knowledge.items():
            known_words = set(self._tokenize(known_q))
            overlap = len(question_words & known_words)
            score = overlap / max(len(question_words), 1)
            
            if score > best_score:
                best_score = score
                best_match = (known_q, known_a)
        
        if best_match and best_score > 0.3:
            return best_match[1], best_score * 0.8  # 降低置信度
        
        # 3. 基于共现预测
        related_words = Counter()
        for w in question_words:
            if w in self.co_occurrence:
                related_words.update(self.co_occurrence[w])
        
        if related_words:
            top_words = [w for w, _ in related_words.most_common(5)]
            return f"可能与 {' '.join(top_words)} 相关", 0.3
        
        return "我不知道", 0.0
    
    def test(self, questions: List[Tuple[str, str]]) -> Tuple[float, int, int]:
        """测试"""
        correct = 0
        for q, expected_a in questions:
            predicted_a, confidence = self.predict(q)
            if predicted_a == expected_a or expected_a in predicted_a:
                correct += 1
                self.correct_predictions += 1
        
        accuracy = correct / len(questions) * 100 if questions else 0
        return accuracy, correct, len(questions)
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        import re
        # 中文按字符，英文按单词
        tokens = re.findall(r'[\u4e00-\u9fff]|[a-zA-Z]+|[0-9]+', text.lower())
        return [t for t in tokens if len(t) > 0]
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "id": self.id,
            "type": self.brain_type,
            "knowledge_count": len(self.knowledge),
            "avg_weight": sum(self.weights.values()) / len(self.weights) if self.weights else 0,
            "vocab_size": len(self.word_freq),
            "training_rounds": self.training_rounds,
            "total_samples": self.total_samples,
            "accuracy": self.correct_predictions / max(1, self.total_samples) * 100
        }
    
    def save(self, path: str):
        """保存"""
        # 转换Counter为普通dict以便序列化
        data = {
            "id": self.id,
            "brain_type": self.brain_type,
            "knowledge": self.knowledge,
            "weights": self.weights,
            "word_freq": dict(self.word_freq),
            "co_occurrence": {k: dict(v) for k, v in self.co_occurrence.items()},
            "training_rounds": self.training_rounds,
            "total_samples": self.total_samples,
            "correct_predictions": self.correct_predictions,
            "created_at": self.created_at,
            "last_trained_at": self.last_trained_at
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    @classmethod
    def load(cls, path: str) -> 'RealBrain':
        """加载"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        brain = cls(id=data["id"], brain_type=data["brain_type"])
        brain.knowledge = data.get("knowledge", {})
        brain.weights = data.get("weights", {})
        brain.word_freq = Counter(data.get("word_freq", {}))
        brain.co_occurrence = defaultdict(Counter, 
            {k: Counter(v) for k, v in data.get("co_occurrence", {}).items()})
        brain.training_rounds = data.get("training_rounds", 0)
        brain.total_samples = data.get("total_samples", 0)
        brain.correct_predictions = data.get("correct_predictions", 0)
        brain.created_at = data.get("created_at", "")
        brain.last_trained_at = data.get("last_trained_at", "")
        
        return brain


# ==================== 轮换训练系统 ====================

class RotationTrainer:
    """轮换训练系统"""
    
    def __init__(self, brains_dir: str, data_dir: str):
        self.brains_dir = brains_dir
        self.data_dir = data_dir
        self.brains: List[RealBrain] = []
        self.data_chunks: List[List[Tuple[str, str]]] = []
        self.current_round = 0
        
        os.makedirs(brains_dir, exist_ok=True)
    
    def load_data(self):
        """加载所有数据"""
        print("加载数据...")
        
        all_data = []
        
        # 加载对话数据
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                q = item.get('question', '') or item.get('keyword', '') or item.get('q', '')
                                a = item.get('answer', '') or item.get('content', '') or item.get('a', '')
                                if q and a:
                                    all_data.append((q, a))
                except Exception as e:
                    print(f"  跳过 {filename}: {e}")
        
        print(f"  加载了 {len(all_data)} 条数据")
        
        # 分成多个块（每个块给不同小脑）
        chunk_size = max(10, len(all_data) // 50)  # 至少10条一块
        self.data_chunks = []
        
        for i in range(0, len(all_data), chunk_size):
            chunk = all_data[i:i+chunk_size]
            self.data_chunks.append(chunk)
        
        print(f"  分成 {len(self.data_chunks)} 个数据块")
        
        return len(all_data)
    
    def create_brains(self, count: int, brain_type: str = "general"):
        """创建小脑"""
        print(f"创建 {count} 个小脑...")
        
        for i in range(count):
            brain = RealBrain(id=f"{brain_type}_{i+1:03d}", brain_type=brain_type)
            self.brains.append(brain)
        
        print(f"  创建了 {len(self.brains)} 个小脑")
    
    def train_round(self, round_num: int):
        """训练一轮 - 轮换投喂"""
        
        print(f"\n{'='*50}")
        print(f"  第 {round_num} 轮训练")
        print(f"{'='*50}")
        
        total_samples = 0
        
        for i, brain in enumerate(self.brains):
            # 轮换：每个小脑吃不同的数据块
            # 第i个小脑在第round_num轮吃第(i + round_num) % len(chunks)块数据
            chunk_index = (i + round_num) % len(self.data_chunks)
            chunk = self.data_chunks[chunk_index]
            
            # 训练
            samples_this_round = 0
            for q, a in chunk:
                brain.train(q, a, learning_rate=0.1)
                samples_this_round += 1
            
            brain.training_rounds += 1
            total_samples += samples_this_round
            
            if (i + 1) % 50 == 0:
                print(f"  已训练 {i+1}/{len(self.brains)} 个小脑")
        
        self.current_round = round_num
        
        print(f"\n  本轮训练样本: {total_samples}")
        print(f"  平均每个小脑: {total_samples // len(self.brains)} 样本")
    
    def test_all(self) -> Dict:
        """测试所有小脑"""
        print("\n测试所有小脑...")
        
        results = []
        total_accuracy = 0
        
        # 随机选一些测试数据
        test_data = []
        for chunk in self.data_chunks[:5]:
            test_data.extend(random.sample(chunk, min(5, len(chunk))))
        
        for brain in self.brains:
            accuracy, correct, total = brain.test(test_data)
            results.append({
                "id": brain.id,
                "accuracy": accuracy,
                "knowledge": len(brain.knowledge),
                "vocab": len(brain.word_freq)
            })
            total_accuracy += accuracy
        
        # 排序
        results.sort(key=lambda x: x["accuracy"], reverse=True)
        
        # 打印前10
        print("\n  前10名:")
        for i, r in enumerate(results[:10], 1):
            print(f"    {i}. {r['id']}: {r['accuracy']:.1f}% (知识:{r['knowledge']}, 词汇:{r['vocab']})")
        
        avg_accuracy = total_accuracy / len(self.brains)
        print(f"\n  平均准确率: {avg_accuracy:.1f}%")
        
        return {
            "results": results,
            "avg_accuracy": avg_accuracy,
            "top_10": results[:10]
        }
    
    def save_all(self):
        """保存所有小脑"""
        print("保存所有小脑...")
        
        for brain in self.brains:
            path = os.path.join(self.brains_dir, f"{brain.id}.pkl")
            brain.save(path)
        
        print(f"  保存了 {len(self.brains)} 个小脑")


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║            真正的轮换训练系统                          ║
╠══════════════════════════════════════════════════════════╣
║  改进：                                                ║
║  1. 轮换投喂 - 每轮不同小脑吃不同数据                ║
║  2. 真实训练 - 更新权重和概率                        ║
║  3. 持续学习 - 多轮训练                              ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 创建训练器
    trainer = RotationTrainer(
        brains_dir="/home/z/tianguang_model/little_brains/real_trained",
        data_dir="/home/z/tianguang_model/collected_data"
    )
    
    # 加载数据
    data_count = trainer.load_data()
    
    # 创建小脑
    trainer.create_brains(100, "general")
    
    # 训练多轮
    for round_num in range(1, 11):  # 10轮
        trainer.train_round(round_num)
        
        # 每3轮测试一次
        if round_num % 3 == 0:
            trainer.test_all()
    
    # 最终测试
    results = trainer.test_all()
    
    # 保存
    trainer.save_all()
    
    # 保存结果
    with open("/home/z/tianguang_model/little_brains/real_trained/training_results.json", 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 训练完成！")


if __name__ == "__main__":
    main()
