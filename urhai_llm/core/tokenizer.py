"""
洱海分词器 - 轻量级中文分词器

特点：
1. 支持中文分词
2. BPE子词分割
3. 轻量级，训练快
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple
from collections import Counter


class UrhaiTokenizer:
    """洱海分词器"""
    
    def __init__(
        self,
        vocab_size: int = 32000,
        min_freq: int = 2,
        special_tokens: List[str] = None
    ):
        self.vocab_size = vocab_size
        self.min_freq = min_freq
        
        # 特殊token
        self.special_tokens = special_tokens or ["<pad>", "<unk>", "<bos>", "<eos>", "<sep>"]
        self.pad_token = "<pad>"
        self.unk_token = "<unk>"
        self.bos_token = "<bos>"
        self.eos_token = "<eos>"
        self.sep_token = "<sep>"
        
        # 词表
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: Dict[int, str] = {}
        
        # BPE合并规则
        self.merges: List[Tuple[str, str]] = []
        
        # 是否已训练
        self.is_trained = False
    
    def _tokenize_chinese(self, text: str) -> List[str]:
        """中文分词"""
        # 简单的中文分词（按字符）
        tokens = []
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                tokens.append(char)
            else:
                tokens.append(char)
        return tokens
    
    def _get_pairs(self, word: Tuple[str, ...]) -> Counter:
        """获取相邻字符对"""
        pairs = Counter()
        for i in range(len(word) - 1):
            pairs[(word[i], word[i + 1])] += 1
        return pairs
    
    def _merge_pair(self, word: Tuple[str, ...], pair: Tuple[str, str]) -> Tuple[str, ...]:
        """合并字符对"""
        new_word = []
        i = 0
        while i < len(word):
            if i < len(word) - 1 and word[i] == pair[0] and word[i + 1] == pair[1]:
                new_word.append(pair[0] + pair[1])
                i += 2
            else:
                new_word.append(word[i])
                i += 1
        return tuple(new_word)
    
    def train(self, texts: List[str], verbose: bool = True):
        """训练分词器"""
        if verbose:
            print(f"训练分词器，目标词表大小: {self.vocab_size}")
        
        # 初始化词表
        self.token_to_id = {token: i for i, token in enumerate(self.special_tokens)}
        
        # 统计词频
        word_freqs: Counter = Counter()
        for text in texts:
            tokens = self._tokenize_chinese(text)
            word = tuple(tokens)
            word_freqs[word] += 1
        
        # 初始化词汇表
        vocab = set()
        for word in word_freqs:
            for token in word:
                vocab.add(token)
        
        # 添加到词表
        for token in sorted(vocab):
            if token not in self.token_to_id:
                self.token_to_id[token] = len(self.token_to_id)
        
        # BPE训练
        num_merges = self.vocab_size - len(self.token_to_id)
        
        for i in range(num_merges):
            # 统计所有词中的字符对
            pairs = Counter()
            for word, freq in word_freqs.items():
                word_pairs = self._get_pairs(word)
                for pair, count in word_pairs.items():
                    pairs[pair] += count * freq
            
            if not pairs:
                break
            
            # 找最高频的字符对
            best_pair = max(pairs, key=pairs.get)
            
            if pairs[best_pair] < self.min_freq:
                break
            
            # 合并
            self.merges.append(best_pair)
            new_token = best_pair[0] + best_pair[1]
            
            if new_token not in self.token_to_id:
                self.token_to_id[new_token] = len(self.token_to_id)
            
            # 更新词频
            new_word_freqs = Counter()
            for word, freq in word_freqs.items():
                new_word = self._merge_pair(word, best_pair)
                new_word_freqs[new_word] += freq
            word_freqs = new_word_freqs
            
            if verbose and (i + 1) % 1000 == 0:
                print(f"  合并 {i + 1}/{num_merges}, 词表大小: {len(self.token_to_id)}")
        
        # 构建反向映射
        self.id_to_token = {v: k for k, v in self.token_to_id.items()}
        self.is_trained = True
        
        if verbose:
            print(f"训练完成，词表大小: {len(self.token_to_id)}")
    
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """编码文本"""
        if not self.is_trained:
            raise ValueError("分词器未训练，请先调用train方法")
        
        tokens = self._tokenize_chinese(text)
        
        # 应用BPE合并
        word = tuple(tokens)
        for pair in self.merges:
            word = self._merge_pair(word, pair)
        
        # 转换为ID
        ids = []
        
        if add_special_tokens:
            ids.append(self.token_to_id[self.bos_token])
        
        for token in word:
            if token in self.token_to_id:
                ids.append(self.token_to_id[token])
            else:
                ids.append(self.token_to_id[self.unk_token])
        
        if add_special_tokens:
            ids.append(self.token_to_id[self.eos_token])
        
        return ids
    
    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """解码ID序列"""
        tokens = []
        for id in ids:
            if id in self.id_to_token:
                token = self.id_to_token[id]
                if skip_special_tokens and token in self.special_tokens:
                    continue
                tokens.append(token)
            else:
                tokens.append(self.unk_token)
        
        return "".join(tokens)
    
    def __len__(self) -> int:
        return len(self.token_to_id)
    
    def save(self, path: str):
        """保存分词器"""
        os.makedirs(path, exist_ok=True)
        
        with open(os.path.join(path, "tokenizer.json"), 'w', encoding='utf-8') as f:
            json.dump({
                "vocab_size": self.vocab_size,
                "min_freq": self.min_freq,
                "special_tokens": self.special_tokens,
                "token_to_id": self.token_to_id,
                "merges": [list(m) for m in self.merges]
            }, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, path: str) -> "UrhaiTokenizer":
        """加载分词器"""
        with open(os.path.join(path, "tokenizer.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tokenizer = cls(
            vocab_size=data["vocab_size"],
            min_freq=data["min_freq"],
            special_tokens=data["special_tokens"]
        )
        
        tokenizer.token_to_id = data["token_to_id"]
        tokenizer.id_to_token = {int(v): k for k, v in tokenizer.token_to_id.items()}
        tokenizer.merges = [tuple(m) for m in data["merges"]]
        tokenizer.is_trained = True
        
        return tokenizer


def train_tokenizer_from_texts(
    texts: List[str],
    vocab_size: int = 32000,
    save_path: Optional[str] = None
) -> UrhaiTokenizer:
    """从文本训练分词器"""
    tokenizer = UrhaiTokenizer(vocab_size=vocab_size)
    tokenizer.train(texts)
    
    if save_path:
        tokenizer.save(save_path)
    
    return tokenizer


if __name__ == "__main__":
    # 测试分词器
    print("测试洱海分词器...")
    
    # 训练数据
    texts = [
        "人工智能是计算机科学的一个分支。",
        "机器学习是人工智能的核心技术。",
        "深度学习使用神经网络进行学习。",
        "自然语言处理让计算机理解人类语言。",
        "洱海是一个美丽的湖泊。",
    ]
    
    # 训练分词器
    tokenizer = UrhaiTokenizer(vocab_size=1000)
    tokenizer.train(texts)
    
    # 测试编码解码
    text = "人工智能很强大"
    ids = tokenizer.encode(text)
    decoded = tokenizer.decode(ids)
    
    print(f"原文: {text}")
    print(f"编码: {ids}")
    print(f"解码: {decoded}")
    
    print("\n✅ 分词器测试通过！")
