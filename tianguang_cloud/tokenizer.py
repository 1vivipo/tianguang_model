"""
天光AI - 分词器
支持字符级和词级分词
"""

import json
import os
from collections import Counter
from typing import List, Dict, Optional


class TianguangTokenizer:
    """天光AI分词器"""
    
    # 特殊标记
    PAD_TOKEN = "<pad>"
    UNK_TOKEN = "<unk>"
    BOS_TOKEN = "<bos>"
    EOS_TOKEN = "<eos>"
    
    PAD_ID = 0
    UNK_ID = 1
    BOS_ID = 2
    EOS_ID = 3
    
    def __init__(
        self,
        vocab: Optional[Dict[str, int]] = None,
        vocab_size: int = 8000,
        model_type: str = "char"  # char, word, bpe
    ):
        self.vocab = vocab or {}
        self.vocab_size = vocab_size
        self.model_type = model_type
        self.id_to_token = {v: k for k, v in self.vocab.items()}
        
    def train(self, texts: List[str], min_freq: int = 2):
        """从文本训练词表"""
        print(f"训练分词器，目标词表大小: {self.vocab_size}")
        
        # 统计词频
        counter = Counter()
        for text in texts:
            if self.model_type == "char":
                # 字符级
                counter.update(list(text))
            else:
                # 词级（简单按空格分割）
                counter.update(text.split())
        
        # 添加特殊标记
        self.vocab = {
            self.PAD_TOKEN: self.PAD_ID,
            self.UNK_TOKEN: self.UNK_ID,
            self.BOS_TOKEN: self.BOS_ID,
            self.EOS_TOKEN: self.EOS_ID,
        }
        
        # 添加高频词
        idx = 4
        for token, freq in counter.most_common():
            if freq >= min_freq and idx < self.vocab_size:
                self.vocab[token] = idx
                idx += 1
        
        self.id_to_token = {v: k for k, v in self.vocab.items()}
        print(f"词表大小: {len(self.vocab)}")
        
        return self
    
    def encode(
        self,
        text: str,
        add_bos: bool = True,
        add_eos: bool = True,
        max_length: Optional[int] = None
    ) -> List[int]:
        """编码文本为ID序列"""
        tokens = []
        
        if add_bos:
            tokens.append(self.BOS_ID)
        
        if self.model_type == "char":
            for char in text:
                tokens.append(self.vocab.get(char, self.UNK_ID))
        else:
            for word in text.split():
                tokens.append(self.vocab.get(word, self.UNK_ID))
        
        if add_eos:
            tokens.append(self.EOS_ID)
        
        if max_length and len(tokens) > max_length:
            tokens = tokens[:max_length - 1] + [self.EOS_ID]
        
        return tokens
    
    def decode(
        self,
        ids: List[int],
        skip_special_tokens: bool = True
    ) -> str:
        """解码ID序列为文本"""
        tokens = []
        for id in ids:
            if id in self.id_to_token:
                token = self.id_to_token[id]
                if skip_special_tokens and id <= 3:
                    continue
                tokens.append(token)
            else:
                tokens.append(self.UNK_TOKEN)
        
        if self.model_type == "char":
            return "".join(tokens)
        else:
            return " ".join(tokens)
    
    def batch_encode(
        self,
        texts: List[str],
        max_length: int = 128,
        padding: bool = True
    ):
        """批量编码"""
        batch = []
        for text in texts:
            ids = self.encode(text, max_length=max_length)
            batch.append(ids)
        
        if padding:
            max_len = max(len(ids) for ids in batch)
            batch = [
                ids + [self.PAD_ID] * (max_len - len(ids))
                for ids in batch
            ]
        
        return batch
    
    def save(self, path: str):
        """保存分词器"""
        os.makedirs(path, exist_ok=True)
        
        config = {
            "vocab": self.vocab,
            "vocab_size": self.vocab_size,
            "model_type": self.model_type,
        }
        
        with open(os.path.join(path, "tokenizer.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"分词器已保存到: {path}")
    
    @classmethod
    def from_pretrained(cls, path: str) -> "TianguangTokenizer":
        """加载预训练分词器"""
        with open(os.path.join(path, "tokenizer.json"), "r", encoding="utf-8") as f:
            config = json.load(f)
        
        return cls(
            vocab=config["vocab"],
            vocab_size=config["vocab_size"],
            model_type=config["model_type"],
        )
    
    def __len__(self):
        return len(self.vocab)
    
    def __repr__(self):
        return f"TianguangTokenizer(vocab_size={len(self.vocab)}, type={self.model_type})"


if __name__ == "__main__":
    # 测试
    texts = [
        "人工智能是计算机科学的一个分支。",
        "机器学习是人工智能的核心技术。",
        "深度学习使用多层神经网络。",
    ]
    
    tokenizer = TianguangTokenizer(vocab_size=100, model_type="char")
    tokenizer.train(texts)
    
    text = "人工智能技术"
    ids = tokenizer.encode(text)
    decoded = tokenizer.decode(ids)
    
    print(f"原文: {text}")
    print(f"编码: {ids}")
    print(f"解码: {decoded}")
