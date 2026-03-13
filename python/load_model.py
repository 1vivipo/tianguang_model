#!/usr/bin/env python3
"""
天光AI - Python模型加载器
用于在Python中加载浏览器训练的模型

安装依赖:
pip install torch numpy

使用方法:
python load_model.py tianguang_model.json
"""

import json
import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Optional

class GRULanguageModel(nn.Module):
    """
    GRU语言模型
    与浏览器端TensorFlow.js模型架构一致
    """
    
    def __init__(
        self,
        vocab_size: int = 500,
        embedding_dim: int = 64,
        hidden_dim: int = 128,
        num_layers: int = 2,
        max_seq_len: int = 32
    ):
        super().__init__()
        
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.max_seq_len = max_seq_len
        
        # 嵌入层
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        
        # GRU层
        self.gru = nn.GRU(
            embedding_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0
        )
        
        # 输出层
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(x)
        output, hidden = self.gru(embedded)
        logits = self.fc(output)
        return logits
    
    def generate(
        self,
        start_tokens: List[int],
        max_length: int = 50,
        temperature: float = 1.0
    ) -> List[int]:
        self.eval()
        
        with torch.no_grad():
            tokens = start_tokens.copy()
            
            for _ in range(max_length):
                x = torch.tensor([tokens[-self.max_seq_len:]], dtype=torch.long)
                logits = self(x)
                next_logits = logits[0, -1, :] / temperature
                probs = torch.softmax(next_logits, dim=-1)
                next_token = torch.multinomial(probs, 1).item()
                tokens.append(next_token)
                if next_token == 3:
                    break
            
            return tokens
    
    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters())


class TianguangTokenizer:
    """天光AI分词器"""
    
    def __init__(self, vocab: Optional[Dict] = None):
        self.char2idx = {'<pad>': 0, '<unk>': 1, '<bos>': 2, '<eos>': 3}
        self.idx2char = {0: '<pad>', 1: '<unk>', 2: '<bos>', 3: '<eos>'}
        
        if vocab:
            self.char2idx = vocab
            self.idx2char = {v: k for k, v in vocab.items()}
    
    def encode(self, text: str, add_bos: bool = True, add_eos: bool = True) -> List[int]:
        tokens = []
        if add_bos:
            tokens.append(2)
        tokens.extend(self.char2idx.get(c, 1) for c in text)
        if add_eos:
            tokens.append(3)
        return tokens
    
    def decode(self, indices: List[int], skip_special: bool = True) -> str:
        if skip_special:
            return ''.join(self.idx2char.get(i, '') for i in indices if i > 3)
        return ''.join(self.idx2char.get(i, '<unk>') for i in indices)
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'vocab': self.char2idx}, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'TianguangTokenizer':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data['vocab'])


def load_tianguang_model(model_path: str) -> tuple:
    """加载天光AI模型"""
    print(f"加载模型: {model_path}")
    
    with open(model_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取配置
    if 'architecture' in data:
        arch = data['architecture']
        vocab_size = arch.get('vocab_size', 500)
        embedding_dim = arch.get('embedding_dim', 64)
        hidden_dim = arch.get('hidden_dim', 128)
        num_layers = arch.get('num_layers', 2)
    elif 'config' in data:
        config = data['config']
        vocab_size = config.get('vocabSize', 500)
        embedding_dim = config.get('embedDim', 64)
        hidden_dim = config.get('hiddenDim', 128)
        num_layers = config.get('numLayers', 2)
    else:
        vocab_size, embedding_dim, hidden_dim, num_layers = 500, 64, 128, 2
    
    model = GRULanguageModel(vocab_size, embedding_dim, hidden_dim, num_layers)
    print(f"模型参数量: {model.count_parameters():,}")
    
    # 加载权重
    if 'weights' in data:
        weights = data['weights']
        for name, w in weights.items():
            if 'embedding' in name.lower():
                model.embedding.weight.data = torch.tensor(w, dtype=torch.float32)
                break
        for name, w in weights.items():
            if 'fc' in name.lower() or 'dense' in name.lower():
                if len(w.shape) == 2:
                    model.fc.weight.data = torch.tensor(w, dtype=torch.float32)
    
    # 创建分词器
    if 'tokenizer' in data:
        tokenizer = TianguangTokenizer(data['tokenizer'].get('vocab', data['tokenizer']))
    elif 'vocab' in data:
        tokenizer = TianguangTokenizer(data['vocab'])
    else:
        tokenizer = TianguangTokenizer()
    
    print("模型加载完成!")
    return model, tokenizer


def main():
    """交互式测试"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python load_model.py <model.json>")
        return
    
    model, tokenizer = load_tianguang_model(sys.argv[1])
    
    print("\n" + "="*50)
    print("天光AI - 模型测试 (输入 quit 退出)")
    print("="*50 + "\n")
    
    while True:
        try:
            prompt = input("你: ").strip()
            if prompt.lower() == 'quit':
                break
            if not prompt:
                continue
            tokens = tokenizer.encode(prompt, add_bos=True, add_eos=False)
            generated = model.generate(tokens, max_length=50, temperature=0.8)
            result = tokenizer.decode(generated, skip_special=True)
            print(f"AI: {result}\n")
        except KeyboardInterrupt:
            break
    
    print("再见!")


if __name__ == '__main__':
    main()
