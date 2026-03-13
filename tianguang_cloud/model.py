"""
天光AI - 模型定义
基于Transformer的语言模型
"""

import math
import os
import json
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiHeadAttention(nn.Module):
    """多头自注意力"""
    
    def __init__(self, hidden_size: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        
        assert hidden_size % num_heads == 0, "hidden_size必须能被num_heads整除"
        
        self.q_proj = nn.Linear(hidden_size, hidden_size)
        self.k_proj = nn.Linear(hidden_size, hidden_size)
        self.v_proj = nn.Linear(hidden_size, hidden_size)
        self.o_proj = nn.Linear(hidden_size, hidden_size)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = math.sqrt(self.head_dim)
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        batch_size, seq_len, _ = hidden_states.shape
        
        # 计算Q, K, V
        q = self.q_proj(hidden_states)
        k = self.k_proj(hidden_states)
        v = self.v_proj(hidden_states)
        
        # 重塑为多头
        q = q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # 计算注意力分数
        scores = torch.matmul(q, k.transpose(-2, -1)) / self.scale
        
        # 应用注意力掩码
        if attention_mask is not None:
            scores = scores + attention_mask
        
        # Softmax
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        # 加权求和
        output = torch.matmul(attn_weights, v)
        
        # 重塑
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.hidden_size)
        
        # 输出投影
        output = self.o_proj(output)
        
        return output


class FeedForward(nn.Module):
    """前馈网络"""
    
    def __init__(
        self,
        hidden_size: int,
        intermediate_size: int,
        dropout: float = 0.1
    ):
        super().__init__()
        
        self.fc1 = nn.Linear(hidden_size, intermediate_size)
        self.fc2 = nn.Linear(intermediate_size, hidden_size)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = F.gelu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class TransformerBlock(nn.Module):
    """Transformer块"""
    
    def __init__(
        self,
        hidden_size: int,
        num_heads: int,
        intermediate_size: int,
        dropout: float = 0.1
    ):
        super().__init__()
        
        self.attention = MultiHeadAttention(hidden_size, num_heads, dropout)
        self.ffn = FeedForward(hidden_size, intermediate_size, dropout)
        
        self.ln1 = nn.LayerNorm(hidden_size)
        self.ln2 = nn.LayerNorm(hidden_size)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        # 自注意力 + 残差
        residual = hidden_states
        hidden_states = self.ln1(hidden_states)
        hidden_states = self.attention(hidden_states, attention_mask)
        hidden_states = self.dropout(hidden_states)
        hidden_states = residual + hidden_states
        
        # 前馈网络 + 残差
        residual = hidden_states
        hidden_states = self.ln2(hidden_states)
        hidden_states = self.ffn(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = residual + hidden_states
        
        return hidden_states


class TianguangModel(nn.Module):
    """天光AI语言模型"""
    
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        
        # 词嵌入
        self.token_embedding = nn.Embedding(config.vocab_size, config.hidden_size)
        self.position_embedding = nn.Embedding(config.max_length, config.hidden_size)
        
        self.embedding_dropout = nn.Dropout(config.hidden_dropout)
        
        # Transformer块
        self.blocks = nn.ModuleList([
            TransformerBlock(
                config.hidden_size,
                config.num_heads,
                config.intermediate_size,
                config.hidden_dropout
            )
            for _ in range(config.num_layers)
        ])
        
        # 最终LayerNorm
        self.ln_f = nn.LayerNorm(config.hidden_size)
        
        # 输出头
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # 权重共享
        self.lm_head.weight = self.token_embedding.weight
        
        # 初始化权重
        self.apply(self._init_weights)
        
        # 统计参数量
        self.num_params = sum(p.numel() for p in self.parameters())
        print(f"模型参数量: {self.num_params:,}")
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.ones_(module.weight)
            torch.nn.init.zeros_(module.bias)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        batch_size, seq_len = input_ids.shape
        
        # 创建位置ID
        position_ids = torch.arange(seq_len, device=input_ids.device)
        position_ids = position_ids.unsqueeze(0).expand(batch_size, -1)
        
        # 嵌入
        hidden_states = self.token_embedding(input_ids)
        hidden_states = hidden_states + self.position_embedding(position_ids)
        hidden_states = self.embedding_dropout(hidden_states)
        
        # 创建因果注意力掩码
        if attention_mask is None:
            attention_mask = torch.triu(
                torch.ones(seq_len, seq_len, device=input_ids.device) * float('-inf'),
                diagonal=1
            )
            attention_mask = attention_mask.unsqueeze(0).unsqueeze(0)
        
        # Transformer块
        for block in self.blocks:
            hidden_states = block(hidden_states, attention_mask)
        
        # 最终LayerNorm
        hidden_states = self.ln_f(hidden_states)
        
        # 输出logits
        logits = self.lm_head(hidden_states)
        
        # 计算损失
        loss = None
        if labels is not None:
            # 移位：预测下一个token
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = labels[:, 1:].contiguous()
            
            loss = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=0  # PAD token
            )
        
        return logits, loss
    
    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 50,
        temperature: float = 0.8,
        top_k: int = 50,
        top_p: float = 0.9,
        do_sample: bool = True,
    ) -> torch.Tensor:
        """生成文本"""
        self.eval()
        
        for _ in range(max_new_tokens):
            # 截断到最大长度
            idx_cond = input_ids[:, -self.config.max_length:]
            
            # 前向传播
            logits, _ = self(idx_cond)
            
            # 取最后一个位置的logits
            logits = logits[:, -1, :] / temperature
            
            # Top-K采样
            if top_k > 0:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float('-inf')
            
            # Top-P采样
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
            
            if do_sample:
                next_token = torch.multinomial(probs, num_samples=1)
            else:
                next_token = torch.argmax(probs, dim=-1, keepdim=True)
            
            # 拼接
            input_ids = torch.cat([input_ids, next_token], dim=1)
            
            # 遇到EOS停止
            if next_token.item() == 3:  # EOS token
                break
        
        return input_ids
    
    def save_pretrained(self, path: str):
        """保存模型"""
        os.makedirs(path, exist_ok=True)
        
        # 保存模型权重
        torch.save(self.state_dict(), os.path.join(path, "pytorch_model.bin"))
        
        # 保存配置
        config_dict = {
            "vocab_size": self.config.vocab_size,
            "hidden_size": self.config.hidden_size,
            "num_layers": self.config.num_layers,
            "num_heads": self.config.num_heads,
            "intermediate_size": self.config.intermediate_size,
            "max_length": self.config.max_length,
            "hidden_dropout": self.config.hidden_dropout,
        }
        
        with open(os.path.join(path, "config.json"), "w") as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"模型已保存到: {path}")
    
    @classmethod
    def from_pretrained(cls, path: str, config=None) -> "TianguangModel":
        """加载模型"""
        # 加载配置
        with open(os.path.join(path, "config.json"), "r") as f:
            config_dict = json.load(f)
        
        # 创建配置对象
        if config is None:
            from config import Config
            config = Config()
        
        for key, value in config_dict.items():
            setattr(config, key, value)
        
        # 创建模型
        model = cls(config)
        
        # 加载权重
        state_dict = torch.load(os.path.join(path, "pytorch_model.bin"), map_location="cpu")
        model.load_state_dict(state_dict)
        
        print(f"模型已从 {path} 加载")
        
        return model


if __name__ == "__main__":
    # 测试模型
    from config import SmallConfig
    
    config = SmallConfig()
    model = TianguangModel(config)
    
    # 测试前向传播
    input_ids = torch.randint(0, config.vocab_size, (2, 32))
    labels = input_ids.clone()
    
    logits, loss = model(input_ids, labels=labels)
    
    print(f"输入形状: {input_ids.shape}")
    print(f"输出形状: {logits.shape}")
    print(f"损失: {loss.item():.4f}")
    
    # 测试生成
    generated = model.generate(input_ids[:1, :5], max_new_tokens=20)
    print(f"生成长度: {generated.shape}")
