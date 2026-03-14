"""
洱海 Transformer - 轻量级语言模型

架构特点：
1. 小型Transformer（4层，256维）
2. 支持CPU运行
3. 支持增量学习
4. 内存占用小（<100MB）
"""

import math
import json
import os
from typing import Optional, Tuple, List
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class TransformerConfig:
    """Transformer配置"""
    vocab_size: int = 32000
    d_model: int = 256
    d_ff: int = 512
    n_layers: int = 4
    n_heads: int = 4
    max_seq_len: int = 512
    dropout: float = 0.1
    pad_token_id: int = 0


class MultiHeadAttention(nn.Module):
    """多头注意力"""
    
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self, 
        query: torch.Tensor, 
        key: torch.Tensor, 
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        batch_size = query.size(0)
        
        # 线性变换
        Q = self.w_q(query).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        
        # 注意力计算
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        attn = F.softmax(scores, dim=-1)
        attn = self.dropout(attn)
        
        # 输出
        output = torch.matmul(attn, V)
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        
        return self.w_o(output)


class FeedForward(nn.Module):
    """前馈网络"""
    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear2(self.dropout(F.gelu(self.linear1(x))))


class TransformerBlock(nn.Module):
    """Transformer块"""
    
    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, n_heads, dropout)
        self.ff = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # 自注意力
        attn_out = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))
        
        # 前馈
        ff_out = self.ff(x)
        x = self.norm2(x + self.dropout(ff_out))
        
        return x


class UrhaiTransformer(nn.Module):
    """洱海Transformer模型"""
    
    def __init__(self, config: TransformerConfig):
        super().__init__()
        self.config = config
        
        # 词嵌入
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        self.position_embedding = nn.Embedding(config.max_seq_len, config.d_model)
        
        # Transformer层
        self.layers = nn.ModuleList([
            TransformerBlock(config.d_model, config.n_heads, config.d_ff, config.dropout)
            for _ in range(config.n_layers)
        ])
        
        # 输出层
        self.norm = nn.LayerNorm(config.d_model)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        
        # 权重绑定
        self.lm_head.weight = self.token_embedding.weight
        
        self.dropout = nn.Dropout(config.dropout)
        
        # 初始化权重
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """初始化权重"""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def forward(
        self, 
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        batch_size, seq_len = input_ids.shape
        
        # 位置编码
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
        
        # 嵌入
        x = self.token_embedding(input_ids) + self.position_embedding(positions)
        x = self.dropout(x)
        
        # 因果掩码
        if attention_mask is None:
            attention_mask = torch.tril(torch.ones(seq_len, seq_len, device=input_ids.device))
            attention_mask = attention_mask.unsqueeze(0).unsqueeze(0)
        
        # Transformer层
        for layer in self.layers:
            x = layer(x, attention_mask)
        
        # 输出
        x = self.norm(x)
        logits = self.lm_head(x)
        
        return logits
    
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 100,
        temperature: float = 0.8,
        top_k: int = 50,
        top_p: float = 0.9
    ) -> torch.Tensor:
        """生成文本"""
        self.eval()
        
        with torch.no_grad():
            for _ in range(max_new_tokens):
                # 截断到最大长度
                idx_cond = input_ids[:, -self.config.max_seq_len:]
                
                # 前向传播
                logits = self(idx_cond)
                
                # 只取最后一个位置
                logits = logits[:, -1, :] / temperature
                
                # Top-k过滤
                if top_k > 0:
                    v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                    logits[logits < v[:, [-1]]] = float('-inf')
                
                # Top-p过滤
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                    
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    
                    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                    logits[indices_to_remove] = float('-inf')
                
                # 采样
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # 拼接
                input_ids = torch.cat([input_ids, next_token], dim=1)
        
        return input_ids
    
    def save_pretrained(self, path: str):
        """保存模型"""
        os.makedirs(path, exist_ok=True)
        
        # 保存配置
        with open(os.path.join(path, "config.json"), 'w') as f:
            json.dump(self.config.__dict__, f, indent=2)
        
        # 保存权重
        torch.save(self.state_dict(), os.path.join(path, "model.bin"))
    
    @classmethod
    def from_pretrained(cls, path: str) -> "UrhaiTransformer":
        """加载模型"""
        # 加载配置
        with open(os.path.join(path, "config.json"), 'r') as f:
            config_dict = json.load(f)
        config = TransformerConfig(**config_dict)
        
        # 创建模型
        model = cls(config)
        
        # 加载权重
        model.load_state_dict(torch.load(os.path.join(path, "model.bin"), map_location='cpu'))
        
        return model
    
    def count_parameters(self) -> int:
        """计算参数量"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def create_model(
    vocab_size: int = 32000,
    d_model: int = 256,
    n_layers: int = 4,
    n_heads: int = 4
) -> UrhaiTransformer:
    """创建模型"""
    config = TransformerConfig(
        vocab_size=vocab_size,
        d_model=d_model,
        n_layers=n_layers,
        n_heads=n_heads
    )
    return UrhaiTransformer(config)


if __name__ == "__main__":
    # 测试模型
    print("创建洱海Transformer模型...")
    model = create_model()
    
    print(f"参数量: {model.count_parameters():,}")
    print(f"模型大小: {model.count_parameters() * 4 / 1024 / 1024:.2f} MB")
    
    # 测试前向传播
    input_ids = torch.randint(0, 1000, (1, 32))
    output = model(input_ids)
    print(f"输入形状: {input_ids.shape}")
    print(f"输出形状: {output.shape}")
    
    print("\n✅ 模型测试通过！")
