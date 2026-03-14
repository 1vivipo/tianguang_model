#!/usr/bin/env python3
"""
黑洞 Blackhole LLM - 一键训练脚本

用途：用积累的知识训练真正的模型
时机：知识库胖了之后（建议10万条以上）

使用方法：
    python train_from_blackhole.py --knowledge ./blackhole_knowledge --epochs 10 --output ./trained_model

参数说明：
    --knowledge   知识库目录（黑洞积累的知识）
    --epochs      训练轮数（默认10）
    --batch_size  批次大小（默认16）
    --lr          学习率（默认1e-4）
    --output      输出目录（默认./trained_model）
    --device      设备（cuda/cpu，默认自动检测）

示例：
    # 在火山引擎GPU上训练
    python train_from_blackhole.py --knowledge ./blackhole_knowledge --epochs 20 --device cuda

    # 在CPU上测试训练
    python train_from_blackhole.py --knowledge ./blackhole_knowledge --epochs 1 --device cpu
"""

import os
import sys
import json
import time
import random
import argparse
from datetime import datetime
from typing import List, Dict, Tuple
from collections import Counter

# 检查依赖
def check_dependencies():
    """检查必要的依赖"""
    missing = []
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
    except ImportError:
        missing.append("torch")
    
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError:
        missing.append("numpy")
    
    if missing:
        print(f"\n❌ 缺少依赖: {', '.join(missing)}")
        print("请安装: pip install " + " ".join(missing))
        sys.exit(1)
    
    return True


class SimpleTokenizer:
    """简单分词器"""
    
    def __init__(self, vocab_size: int = 32000):
        self.vocab_size = vocab_size
        self.word2id = {"<pad>": 0, "<unk>": 1, "<bos>": 2, "<eos>": 3}
        self.id2word = {0: "<pad>", 1: "<unk>", 2: "<bos>", 3: "<eos>"}
        self.is_trained = False
    
    def train(self, texts: List[str], min_freq: int = 2):
        """训练分词器"""
        print(f"训练分词器，文本数: {len(texts)}")
        
        # 统计词频
        word_freq = Counter()
        for text in texts:
            # 简单分词：中文字符 + 英文单词
            import re
            words = re.findall(r'[\u4e00-\u9fff]|[a-zA-Z]+|[0-9]+', text.lower())
            word_freq.update(words)
        
        # 选择高频词
        vocab_list = [word for word, freq in word_freq.most_common(self.vocab_size - 4)
                      if freq >= min_freq]
        
        # 构建词表
        for i, word in enumerate(vocab_list):
            self.word2id[word] = i + 4
            self.id2word[i + 4] = word
        
        self.is_trained = True
        print(f"词表大小: {len(self.word2id)}")
    
    def encode(self, text: str, max_len: int = 512) -> List[int]:
        """编码"""
        import re
        words = re.findall(r'[\u4e00-\u9fff]|[a-zA-Z]+|[0-9]+', text.lower())
        
        ids = [self.word2id["<bos>"]]
        for word in words[:max_len - 2]:
            ids.append(self.word2id.get(word, self.word2id["<unk>"]))
        ids.append(self.word2id["<eos>"])
        
        # 填充
        while len(ids) < max_len:
            ids.append(self.word2id["<pad>"])
        
        return ids[:max_len]
    
    def decode(self, ids: List[int]) -> str:
        """解码"""
        words = []
        for id in ids:
            if id in [0, 2, 3]:  # pad, bos, eos
                continue
            words.append(self.id2word.get(id, "<unk>"))
        return "".join(words)
    
    def save(self, path: str):
        """保存"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "vocab_size": self.vocab_size,
                "word2id": self.word2id,
                "id2word": {str(k): v for k, v in self.id2word.items()}
            }, f, ensure_ascii=False)
    
    def load(self, path: str):
        """加载"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.vocab_size = data["vocab_size"]
        self.word2id = data["word2id"]
        self.id2word = {int(k): v for k, v in data["id2word"].items()}
        self.is_trained = True


class SimpleTransformer:
    """简单Transformer模型"""
    
    def __init__(self, vocab_size: int, d_model: int = 256, n_heads: int = 4, n_layers: int = 4):
        import torch
        import torch.nn as nn
        
        self.vocab_size = vocab_size
        self.d_model = d_model
        
        # 模型结构
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(512, d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        
        self.fc_out = nn.Linear(d_model, vocab_size)
        
        # 初始化
        self._init_weights()
    
    def _init_weights(self):
        import torch.nn as nn
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def forward(self, x):
        import torch
        
        seq_len = x.size(1)
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0)
        
        # 嵌入
        x = self.embedding(x) + self.pos_embedding(positions)
        
        # Transformer
        # 创建因果掩码
        mask = torch.triu(torch.ones(seq_len, seq_len, device=x.device), diagonal=1).bool()
        x = self.transformer(x, mask=mask)
        
        # 输出
        logits = self.fc_out(x)
        
        return logits
    
    def generate(self, input_ids, max_new_tokens=100, temperature=0.8):
        """生成文本"""
        import torch
        import torch.nn.functional as F
        
        self.eval()
        
        with torch.no_grad():
            for _ in range(max_new_tokens):
                # 前向传播
                logits = self.forward(input_ids)
                
                # 只取最后一个位置
                logits = logits[:, -1, :] / temperature
                
                # 采样
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # 拼接
                input_ids = torch.cat([input_ids, next_token], dim=1)
                
                # 检查结束
                if next_token.item() == 3:  # <eos>
                    break
        
        return input_ids
    
    def save(self, path: str):
        """保存模型"""
        import torch
        torch.save({
            "vocab_size": self.vocab_size,
            "d_model": self.d_model,
            "state_dict": self.state_dict()
        }, path)
    
    def load(self, path: str):
        """加载模型"""
        import torch
        checkpoint = torch.load(path, map_location='cpu')
        self.load_state_dict(checkpoint["state_dict"])


def load_knowledge(knowledge_dir: str) -> List[Dict]:
    """加载知识库"""
    print(f"\n加载知识库: {knowledge_dir}")
    
    knowledge = []
    
    if os.path.isfile(knowledge_dir) and knowledge_dir.endswith('.json'):
        # 单个文件
        with open(knowledge_dir, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                knowledge.extend(data)
            elif isinstance(data, dict):
                knowledge.append(data)
    elif os.path.isdir(knowledge_dir):
        # 目录
        for filename in os.listdir(knowledge_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(knowledge_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        knowledge.extend(data)
                    elif isinstance(data, dict):
                        knowledge.append(data)
                except Exception as e:
                    print(f"  跳过 {filename}: {e}")
    
    print(f"✓ 加载了 {len(knowledge)} 条知识")
    return knowledge


def prepare_training_data(knowledge: List[Dict]) -> List[Tuple[str, str]]:
    """准备训练数据"""
    print("\n准备训练数据...")
    
    training_pairs = []
    
    for item in knowledge:
        title = item.get("title", "")
        content = item.get("content", "")
        domain = item.get("domain", "")
        
        if content:
            # 创建多种训练样本
            
            # 1. 标题 -> 内容
            if title:
                training_pairs.append((f"关于{title}", content))
            
            # 2. 领域 -> 内容
            if domain:
                training_pairs.append((f"{domain}知识", content))
            
            # 3. 内容续写
            if len(content) > 100:
                training_pairs.append((content[:50], content[50:200]))
    
    print(f"✓ 准备了 {len(training_pairs)} 个训练样本")
    return training_pairs


def train(
    knowledge_dir: str,
    output_dir: str = "./trained_model",
    epochs: int = 10,
    batch_size: int = 16,
    learning_rate: float = 1e-4,
    device: str = None
):
    """训练模型"""
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    
    # 检查设备
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n使用设备: {device}")
    
    # 加载知识
    knowledge = load_knowledge(knowledge_dir)
    
    if len(knowledge) < 100:
        print("❌ 知识太少，建议积累更多知识后再训练")
        return
    
    # 准备数据
    training_pairs = prepare_training_data(knowledge)
    
    # 训练分词器
    print("\n训练分词器...")
    tokenizer = SimpleTokenizer(vocab_size=32000)
    all_texts = [p[0] + " " + p[1] for p in training_pairs]
    tokenizer.train(all_texts)
    
    # 创建数据集
    class TextDataset(Dataset):
        def __init__(self, pairs, tokenizer, max_len=256):
            self.pairs = pairs
            self.tokenizer = tokenizer
            self.max_len = max_len
        
        def __len__(self):
            return len(self.pairs)
        
        def __getitem__(self, idx):
            input_text, output_text = self.pairs[idx]
            
            # 编码
            input_ids = self.tokenizer.encode(input_text, self.max_len)
            target_ids = self.tokenizer.encode(output_text, self.max_len)
            
            return torch.tensor(input_ids), torch.tensor(target_ids)
    
    dataset = TextDataset(training_pairs, tokenizer)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # 创建模型
    print("\n创建模型...")
    model = SimpleTransformer(
        vocab_size=len(tokenizer.word2id),
        d_model=256,
        n_heads=4,
        n_layers=4
    ).to(device)
    
    # 计算参数量
    total_params = sum(p.numel() for p in model.parameters())
    print(f"模型参数: {total_params:,}")
    print(f"模型大小: {total_params * 4 / 1024 / 1024:.2f} MB")
    
    # 优化器
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss(ignore_index=0)  # 忽略padding
    
    # 训练循环
    print(f"\n开始训练，epochs: {epochs}")
    print("=" * 50)
    
    start_time = time.time()
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        num_batches = 0
        
        for batch_idx, (inputs, targets) in enumerate(dataloader):
            inputs = inputs.to(device)
            targets = targets.to(device)
            
            # 前向传播
            logits = model(inputs)
            
            # 计算损失
            loss = criterion(
                logits.view(-1, logits.size(-1)),
                targets.view(-1)
            )
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            # 打印进度
            if (batch_idx + 1) % 10 == 0:
                print(f"  Epoch {epoch+1}/{epochs}, Batch {batch_idx+1}/{len(dataloader)}, Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / num_batches
        elapsed = time.time() - start_time
        
        print(f"Epoch {epoch+1} 完成: 平均损失 {avg_loss:.4f}, 用时 {elapsed:.1f}秒")
        print("-" * 50)
    
    # 保存模型
    print(f"\n保存模型到 {output_dir}...")
    os.makedirs(output_dir, exist_ok=True)
    
    model.save(os.path.join(output_dir, "model.pt"))
    tokenizer.save(os.path.join(output_dir, "tokenizer.json"))
    
    # 保存训练信息
    info = {
        "trained_at": datetime.now().isoformat(),
        "knowledge_count": len(knowledge),
        "training_samples": len(training_pairs),
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "final_loss": avg_loss,
        "model_params": total_params,
        "device": device
    }
    
    with open(os.path.join(output_dir, "training_info.json"), 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 训练完成！")
    print(f"   模型保存在: {output_dir}")
    print(f"   参数量: {total_params:,}")
    print(f"   最终损失: {avg_loss:.4f}")
    
    # 测试生成
    print("\n测试生成...")
    test_generation(model, tokenizer, device)
    
    return model, tokenizer


def test_generation(model, tokenizer, device, prompt="人工智能"):
    """测试生成"""
    import torch
    
    print(f"提示: {prompt}")
    
    input_ids = torch.tensor([tokenizer.encode(prompt)]).to(device)
    output_ids = model.generate(input_ids, max_new_tokens=50, temperature=0.8)
    
    output_text = tokenizer.decode(output_ids[0].tolist())
    print(f"生成: {output_text}")


def main():
    parser = argparse.ArgumentParser(description="黑洞模型训练脚本")
    parser.add_argument("--knowledge", type=str, required=True, help="知识库目录")
    parser.add_argument("--output", type=str, default="./trained_model", help="输出目录")
    parser.add_argument("--epochs", type=int, default=10, help="训练轮数")
    parser.add_argument("--batch_size", type=int, default=16, help="批次大小")
    parser.add_argument("--lr", type=float, default=1e-4, help="学习率")
    parser.add_argument("--device", type=str, default=None, help="设备(cuda/cpu)")
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║            黑洞 Blackhole LLM 训练脚本                  ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 检查依赖
    check_dependencies()
    
    # 开始训练
    train(
        knowledge_dir=args.knowledge,
        output_dir=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        device=args.device
    )


if __name__ == "__main__":
    main()
