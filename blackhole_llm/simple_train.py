#!/usr/bin/env python3
"""
简化训练脚本 - 不需要PyTorch

用纯Python实现一个简单的语言模型：
- 基于统计的N-gram模型
- 简单的文本生成
- 可以在CPU上快速训练

使用方法：
    python simple_train.py --data ./collected_data --epochs 5
"""

import os
import sys
import json
import random
import math
import pickle
from datetime import datetime
from typing import List, Dict, Tuple
from collections import Counter, defaultdict

# 配置
DATA_DIR = "/home/z/tianguang_model/collected_data"
OUTPUT_DIR = "/home/z/tianguang_model/trained_model"

class SimpleTokenizer:
    """简单分词器"""
    
    def __init__(self):
        self.word2id = {"<pad>": 0, "<unk>": 1, "<bos>": 2, "<eos>": 3}
        self.id2word = {0: "<pad>", 1: "<unk>", 2: "<bos>", 3: "<eos>"}
        self.word_freq = Counter()
    
    def train(self, texts: List[str], min_freq: int = 2):
        """训练分词器"""
        print(f"训练分词器，文本数: {len(texts)}")
        
        # 统计词频
        for text in texts:
            words = self._tokenize(text)
            self.word_freq.update(words)
        
        # 构建词表
        for word, freq in self.word_freq.most_common(10000):
            if freq >= min_freq and word not in self.word2id:
                idx = len(self.word2id)
                self.word2id[word] = idx
                self.id2word[idx] = word
        
        print(f"词表大小: {len(self.word2id)}")
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        import re
        # 中文按字符，英文按单词
        words = re.findall(r'[\u4e00-\u9fff]|[a-zA-Z]+|[0-9]+', text.lower())
        return words
    
    def encode(self, text: str) -> List[int]:
        """编码"""
        words = self._tokenize(text)
        return [self.word2id.get(w, 1) for w in words]  # 1 = <unk>
    
    def decode(self, ids: List[int]) -> str:
        """解码"""
        return "".join(self.id2word.get(i, "<unk>") for i in ids)
    
    def save(self, path: str):
        """保存"""
        with open(path, 'wb') as f:
            pickle.dump({
                'word2id': self.word2id,
                'id2word': self.id2word,
                'word_freq': self.word_freq
            }, f)
    
    def load(self, path: str):
        """加载"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.word2id = data['word2id']
        self.id2word = data['id2word']
        self.word_freq = data['word_freq']


class NGramModel:
    """N-gram语言模型"""
    
    def __init__(self, n: int = 3):
        self.n = n
        self.ngram_counts = defaultdict(Counter)
        self.context_counts = Counter()
    
    def train(self, tokenized_texts: List[List[int]]):
        """训练"""
        print(f"训练N-gram模型，n={self.n}")
        
        for tokens in tokenized_texts:
            # 添加开始和结束标记
            tokens = [2] + tokens + [3]  # <bos> + tokens + <eos>
            
            for i in range(len(tokens) - self.n + 1):
                context = tuple(tokens[i:i+self.n-1])
                word = tokens[i+self.n-1]
                
                self.ngram_counts[context][word] += 1
                self.context_counts[context] += 1
        
        print(f"N-gram数量: {len(self.ngram_counts)}")
    
    def predict(self, context: Tuple[int, ...]) -> int:
        """预测下一个词"""
        context = tuple(context[-(self.n-1):])
        
        if context not in self.ngram_counts:
            return random.randint(0, 100)
        
        # 选择概率最高的词
        candidates = self.ngram_counts[context]
        total = self.context_counts[context]
        
        if total == 0:
            return random.randint(0, 100)
        
        # 加一点随机性
        r = random.random() * total
        cumsum = 0
        for word, count in candidates.items():
            cumsum += count
            if cumsum >= r:
                return word
        
        return random.choice(list(candidates.keys()))
    
    def generate(self, tokenizer, prompt: str = "", max_len: int = 50) -> str:
        """生成文本"""
        if prompt:
            context = tokenizer.encode(prompt)
        else:
            context = [2]  # <bos>
        
        for _ in range(max_len):
            next_word = self.predict(context)
            
            if next_word == 3:  # <eos>
                break
            
            context.append(next_word)
        
        return tokenizer.decode(context)
    
    def save(self, path: str):
        """保存"""
        with open(path, 'wb') as f:
            pickle.dump({
                'n': self.n,
                'ngram_counts': dict(self.ngram_counts),
                'context_counts': dict(self.context_counts)
            }, f)
    
    def load(self, path: str):
        """加载"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.n = data['n']
        self.ngram_counts = defaultdict(Counter, data['ngram_counts'])
        self.context_counts = Counter(data['context_counts'])


class SimpleNeuralNet:
    """简单神经网络（纯Python实现）"""
    
    def __init__(self, vocab_size: int, embed_dim: int = 64, hidden_dim: int = 128):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        
        # 初始化权重（小随机值）
        scale = 0.1
        
        # 嵌入层
        self.embeddings = [[random.gauss(0, scale) for _ in range(embed_dim)] 
                          for _ in range(vocab_size)]
        
        # 隐藏层
        self.W1 = [[random.gauss(0, scale) for _ in range(hidden_dim)] 
                  for _ in range(embed_dim)]
        self.b1 = [0.0] * hidden_dim
        
        # 输出层
        self.W2 = [[random.gauss(0, scale) for _ in range(vocab_size)] 
                  for _ in range(hidden_dim)]
        self.b2 = [0.0] * vocab_size
    
    def forward(self, x: List[int]) -> List[List[float]]:
        """前向传播"""
        # 嵌入
        embedded = [self.embeddings[idx] for idx in x]
        
        # 平均池化
        if embedded:
            hidden_input = [sum(e[i] for e in embedded) / len(embedded) 
                           for i in range(self.embed_dim)]
        else:
            hidden_input = [0.0] * self.embed_dim
        
        # 隐藏层 + ReLU
        hidden = []
        for j in range(self.hidden_dim):
            h = sum(hidden_input[i] * self.W1[i][j] for i in range(self.embed_dim)) + self.b1[j]
            h = max(0, h)  # ReLU
            hidden.append(h)
        
        # 输出层
        output = []
        for k in range(self.vocab_size):
            o = sum(hidden[j] * self.W2[j][k] for j in range(self.hidden_dim)) + self.b2[k]
            output.append(o)
        
        return output
    
    def predict(self, x: List[int]) -> int:
        """预测"""
        output = self.forward(x)
        return output.index(max(output))
    
    def train_step(self, x: List[int], target: int, lr: float = 0.01):
        """训练一步（简化版）"""
        # 前向传播
        output = self.forward(x)
        
        # 计算损失（简化：只更新目标词）
        # 这里用非常简化的梯度下降
        
        # 更新输出层权重（只更新目标词相关的）
        for j in range(self.hidden_dim):
            self.W2[j][target] += lr * 0.1  # 简化更新
        
        return -output[target]  # 返回负对数似然（简化）
    
    def save(self, path: str):
        """保存"""
        with open(path, 'wb') as f:
            pickle.dump({
                'vocab_size': self.vocab_size,
                'embed_dim': self.embed_dim,
                'hidden_dim': self.hidden_dim,
                'embeddings': self.embeddings,
                'W1': self.W1,
                'b1': self.b1,
                'W2': self.W2,
                'b2': self.b2
            }, f)


def load_data(data_dir: str) -> List[str]:
    """加载数据"""
    print(f"加载数据: {data_dir}")
    
    texts = []
    
    # 遍历所有JSON文件
    for root, dirs, files in os.walk(data_dir):
        for filename in files:
            if filename.endswith('.json'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        for item in data:
                            # 提取文本内容
                            if isinstance(item, dict):
                                content = item.get('content', '') or item.get('text', '') or item.get('question', '') or item.get('answer', '')
                                if content:
                                    texts.append(content)
                    elif isinstance(data, dict):
                        content = data.get('content', '') or data.get('text', '')
                        if content:
                            texts.append(content)
                except Exception as e:
                    print(f"  跳过 {filename}: {e}")
    
    print(f"加载了 {len(texts)} 条文本")
    return texts


def train(data_dir: str, output_dir: str, epochs: int = 5):
    """训练模型"""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║            简化训练脚本 - 纯Python实现                  ║
╠══════════════════════════════════════════════════════════╣
║  数据目录: {data_dir:<42} ║
║  输出目录: {output_dir:<42} ║
║  训练轮数: {epochs:<42} ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载数据
    texts = load_data(data_dir)
    
    if len(texts) < 10:
        print("数据太少，添加示例数据...")
        texts.extend([
            "人工智能是计算机科学的一个分支",
            "机器学习是人工智能的核心技术",
            "深度学习使用神经网络进行学习",
            "自然语言处理让计算机理解人类语言",
            "Python是一种流行的编程语言",
            "编程是创建计算机程序的过程",
            "数据是信息的载体",
            "算法是解决问题的步骤",
            "模型是对现实世界的抽象",
            "训练是让模型学习的过程"
        ])
    
    # 训练分词器
    print("\n[1/3] 训练分词器...")
    tokenizer = SimpleTokenizer()
    tokenizer.train(texts)
    
    # 训练N-gram模型
    print("\n[2/3] 训练N-gram模型...")
    tokenized = [tokenizer.encode(t) for t in texts]
    ngram_model = NGramModel(n=3)
    ngram_model.train(tokenized)
    
    # 训练简单神经网络
    print("\n[3/3] 训练简单神经网络...")
    nn_model = SimpleNeuralNet(vocab_size=len(tokenizer.word2id))
    
    for epoch in range(epochs):
        total_loss = 0
        for i, tokens in enumerate(tokenized[:100]):  # 只用前100条
            if len(tokens) > 1:
                for j in range(len(tokens) - 1):
                    context = tokens[:j+1]
                    target = tokens[j+1]
                    loss = nn_model.train_step(context, target)
                    total_loss += loss
        
        avg_loss = total_loss / max(1, len(tokenized))
        print(f"  Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
    
    # 保存模型
    print("\n保存模型...")
    tokenizer.save(os.path.join(output_dir, "tokenizer.pkl"))
    ngram_model.save(os.path.join(output_dir, "ngram_model.pkl"))
    nn_model.save(os.path.join(output_dir, "nn_model.pkl"))
    
    # 保存训练信息
    info = {
        "trained_at": datetime.now().isoformat(),
        "num_texts": len(texts),
        "vocab_size": len(tokenizer.word2id),
        "epochs": epochs
    }
    with open(os.path.join(output_dir, "training_info.json"), 'w') as f:
        json.dump(info, f, indent=2)
    
    # 测试生成
    print("\n测试生成...")
    for prompt in ["人工智能", "Python", "机器学习"]:
        generated = ngram_model.generate(tokenizer, prompt, max_len=20)
        print(f"  提示: {prompt} -> 生成: {generated}")
    
    print(f"\n✅ 训练完成！模型保存在: {output_dir}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="简化训练脚本")
    parser.add_argument("--data", type=str, default=DATA_DIR, help="数据目录")
    parser.add_argument("--output", type=str, default=OUTPUT_DIR, help="输出目录")
    parser.add_argument("--epochs", type=int, default=5, help="训练轮数")
    
    args = parser.parse_args()
    
    train(args.data, args.output, args.epochs)


if __name__ == "__main__":
    main()
