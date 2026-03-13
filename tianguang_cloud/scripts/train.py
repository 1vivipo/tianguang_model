"""
天光AI - 训练脚本
支持在GPU上训练语言模型
"""

import os
import sys
import time
import json
import math
import argparse
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR, LinearLR, SequentialLR

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config, SmallConfig, MediumConfig, LargeConfig
from model import TianguangModel
from tokenizer import TianguangTokenizer


class TextDataset(Dataset):
    """文本数据集"""
    
    def __init__(
        self,
        texts: list,
        tokenizer: TianguangTokenizer,
        max_length: int = 128
    ):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        
        # 编码
        ids = self.tokenizer.encode(
            text,
            add_bos=True,
            add_eos=True,
            max_length=self.max_length
        )
        
        # 填充
        if len(ids) < self.max_length:
            ids = ids + [0] * (self.max_length - len(ids))
        else:
            ids = ids[:self.max_length]
        
        return torch.tensor(ids, dtype=torch.long)


def load_data(data_path: str) -> list:
    """加载训练数据"""
    print(f"加载数据: {data_path}")
    
    texts = []
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                texts.append(line)
    
    print(f"加载了 {len(texts)} 条数据")
    return texts


def train(
    config,
    resume_from: str = None,
):
    """训练模型"""
    
    # 设置设备
    device = torch.device(config.device if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    # 加载数据
    texts = load_data(config.data_path)
    
    # 创建分词器
    print("训练分词器...")
    tokenizer = TianguangTokenizer(
        vocab_size=config.vocab_size,
        model_type="char"
    )
    tokenizer.train(texts, min_freq=1)
    
    # 创建数据集
    dataset = TextDataset(texts, tokenizer, config.max_length)
    dataloader = DataLoader(
        dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )
    
    # 创建模型
    print("创建模型...")
    model = TianguangModel(config)
    model = model.to(device)
    
    # 恢复训练
    start_step = 0
    if resume_from:
        print(f"从 {resume_from} 恢复训练")
        checkpoint = torch.load(resume_from, map_location=device)
        model.load_state_dict(checkpoint["model_state_dict"])
        start_step = checkpoint.get("step", 0)
    
    # 优化器
    optimizer = AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
        betas=(0.9, 0.95)
    )
    
    # 学习率调度器
    warmup_scheduler = LinearLR(
        optimizer,
        start_factor=0.1,
        end_factor=1.0,
        total_iters=config.warmup_steps
    )
    main_scheduler = CosineAnnealingLR(
        optimizer,
        T_max=config.max_steps - config.warmup_steps,
        eta_min=config.learning_rate * 0.1
    )
    scheduler = SequentialLR(
        optimizer,
        schedulers=[warmup_scheduler, main_scheduler],
        milestones=[config.warmup_steps]
    )
    
    # 混合精度
    scaler = torch.cuda.amp.GradScaler() if config.fp16 else None
    
    # 训练循环
    print("开始训练...")
    model.train()
    
    global_step = start_step
    total_loss = 0
    start_time = time.time()
    
    while global_step < config.max_steps:
        for batch in dataloader:
            if global_step >= config.max_steps:
                break
            
            # 移动到设备
            input_ids = batch.to(device)
            labels = input_ids.clone()
            
            # 前向传播
            if config.fp16:
                with torch.cuda.amp.autocast():
                    logits, loss = model(input_ids, labels=labels)
                    loss = loss / config.gradient_accumulation_steps
            else:
                logits, loss = model(input_ids, labels=labels)
                loss = loss / config.gradient_accumulation_steps
            
            # 反向传播
            if config.fp16:
                scaler.scale(loss).backward()
            else:
                loss.backward()
            
            total_loss += loss.item()
            
            # 梯度累积
            if (global_step + 1) % config.gradient_accumulation_steps == 0:
                # 梯度裁剪
                if config.fp16:
                    scaler.unscale_(optimizer)
                
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    config.max_grad_norm
                )
                
                # 更新参数
                if config.fp16:
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    optimizer.step()
                
                scheduler.step()
                optimizer.zero_grad()
                
                global_step += 1
                
                # 日志
                if global_step % config.log_steps == 0:
                    elapsed = time.time() - start_time
                    avg_loss = total_loss / config.log_steps
                    lr = scheduler.get_last_lr()[0]
                    
                    print(
                        f"Step {global_step}/{config.max_steps} | "
                        f"Loss: {avg_loss:.4f} | "
                        f"LR: {lr:.2e} | "
                        f"Time: {elapsed:.1f}s"
                    )
                    
                    total_loss = 0
                    start_time = time.time()
                
                # 保存检查点
                if global_step % config.save_steps == 0:
                    save_path = os.path.join(config.output_dir, f"checkpoint-{global_step}")
                    os.makedirs(save_path, exist_ok=True)
                    
                    torch.save({
                        "step": global_step,
                        "model_state_dict": model.state_dict(),
                        "optimizer_state_dict": optimizer.state_dict(),
                    }, os.path.join(save_path, "checkpoint.pt"))
                    
                    print(f"检查点已保存: {save_path}")
                
                # 评估
                if global_step % config.eval_steps == 0:
                    model.eval()
                    
                    # 生成示例
                    test_text = "人工智能"
                    test_ids = torch.tensor([tokenizer.encode(test_text, add_bos=True, add_eos=False)]).to(device)
                    generated = model.generate(
                        test_ids,
                        max_new_tokens=30,
                        temperature=0.8
                    )
                    generated_text = tokenizer.decode(generated[0].tolist())
                    
                    print(f"生成示例: {generated_text}")
                    
                    model.train()
    
    # 保存最终模型
    print("保存最终模型...")
    os.makedirs(config.output_dir, exist_ok=True)
    
    model.save_pretrained(config.output_dir)
    tokenizer.save(config.output_dir)
    
    print("训练完成！")
    print(f"模型保存在: {config.output_dir}")


def main():
    parser = argparse.ArgumentParser(description="天光AI训练脚本")
    parser.add_argument("--config", type=str, default="medium", choices=["small", "medium", "large"])
    parser.add_argument("--data", type=str, default="data/training_data.txt")
    parser.add_argument("--output", type=str, default="models/tianguang_model")
    parser.add_argument("--resume", type=str, default=None)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--batch_size", type=int, default=None)
    parser.add_argument("--lr", type=float, default=None)
    
    args = parser.parse_args()
    
    # 选择配置
    if args.config == "small":
        config = SmallConfig()
    elif args.config == "large":
        config = LargeConfig()
    else:
        config = MediumConfig()
    
    # 覆盖参数
    if args.data:
        config.data_path = args.data
    if args.output:
        config.output_dir = args.output
    if args.steps:
        config.max_steps = args.steps
    if args.batch_size:
        config.batch_size = args.batch_size
    if args.lr:
        config.learning_rate = args.lr
    
    print("=" * 50)
    print("天光AI训练配置")
    print("=" * 50)
    print(f"模型类型: {args.config}")
    print(f"词表大小: {config.vocab_size}")
    print(f"隐藏层大小: {config.hidden_size}")
    print(f"层数: {config.num_layers}")
    print(f"注意力头数: {config.num_heads}")
    print(f"最大步数: {config.max_steps}")
    print(f"批次大小: {config.batch_size}")
    print(f"学习率: {config.learning_rate}")
    print("=" * 50)
    
    train(config, args.resume)


if __name__ == "__main__":
    main()
