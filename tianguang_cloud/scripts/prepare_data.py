"""
天光AI - 数据准备脚本
帮助准备训练数据
"""

import os
import sys
import json
import random


def create_sample_data(output_path: str, num_samples: int = 1000):
    """创建示例数据"""
    
    sample_texts = [
        "人工智能是计算机科学的一个分支，研究如何使计算机具有智能。",
        "机器学习是人工智能的核心技术，让计算机从数据中学习。",
        "深度学习使用多层神经网络进行学习和预测。",
        "自然语言处理让计算机能够理解和生成人类语言。",
        "计算机视觉让计算机能够理解和处理图像。",
        "神经网络是模拟人脑神经元连接的计算模型。",
        "卷积神经网络特别适合处理图像数据。",
        "循环神经网络适合处理序列数据。",
        "Transformer是目前最流行的神经网络架构。",
        "注意力机制让模型能够关注重要的信息。",
        "预训练模型是在大规模数据上训练的模型。",
        "微调是在特定任务上调整预训练模型。",
        "迁移学习是将一个领域的知识迁移到另一个领域。",
        "数据增强是增加数据多样性的技术。",
        "正则化是防止过拟合的技术。",
        "梯度下降是优化模型参数的算法。",
        "学习率控制参数更新的步长。",
        "批次大小是一次训练的样本数量。",
        "训练轮次是遍历整个数据集的次数。",
        "验证集用于调整模型超参数。",
        "测试集用于评估模型性能。",
        "损失函数衡量模型预测与真实值的差距。",
        "准确率是预测正确的比例。",
        "精确率是预测为正例中真正例的比例。",
        "召回率是真正例中被预测为正例的比例。",
        "F1分数是精确率和召回率的调和平均。",
        "过拟合是模型在训练数据上表现太好。",
        "欠拟合是模型在训练数据上表现不好。",
        "偏差是模型预测与真实值的系统性差异。",
        "方差是模型预测的波动程度。",
        "偏差-方差权衡是模型复杂度的平衡。",
        "特征工程是创建和选择特征的过程。",
        "特征选择是选择最相关特征的过程。",
        "降维是减少特征数量的技术。",
        "主成分分析是一种降维技术。",
        "聚类是将相似样本分组的技术。",
        "分类是将样本分到预定义类别。",
        "回归是预测连续值的技术。",
        "监督学习使用标注数据训练。",
        "无监督学习使用未标注数据训练。",
        "半监督学习使用少量标注数据。",
        "强化学习通过奖励信号学习。",
        "生成模型学习数据分布并生成新样本。",
        "判别模型学习区分不同类别。",
        "生成对抗网络由生成器和判判器组成。",
        "变分自编码器是一种生成模型。",
        "扩散模型是新兴的生成模型。",
        "自监督学习从数据本身构造监督信号。",
        "对比学习通过对比样本学习表示。",
    ]
    
    # 扩展数据
    texts = []
    for _ in range(num_samples):
        text = random.choice(sample_texts)
        texts.append(text)
    
    # 保存
    with open(output_path, "w", encoding="utf-8") as f:
        for text in texts:
            f.write(text + "\n")
    
    print(f"创建了 {len(texts)} 条示例数据")
    print(f"保存到: {output_path}")


def merge_data_files(input_dir: str, output_path: str):
    """合并多个数据文件"""
    
    texts = []
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        texts.append(line)
    
    # 保存
    with open(output_path, "w", encoding="utf-8") as f:
        for text in texts:
            f.write(text + "\n")
    
    print(f"合并了 {len(texts)} 条数据")
    print(f"保存到: {output_path}")


def filter_data(input_path: str, output_path: str, min_length: int = 10, max_length: int = 200):
    """过滤数据"""
    
    texts = []
    
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if min_length <= len(line) <= max_length:
                texts.append(line)
    
    # 保存
    with open(output_path, "w", encoding="utf-8") as f:
        for text in texts:
            f.write(text + "\n")
    
    print(f"过滤后剩余 {len(texts)} 条数据")
    print(f"保存到: {output_path}")


def split_data(input_path: str, train_path: str, val_path: str, val_ratio: float = 0.1):
    """分割训练集和验证集"""
    
    with open(input_path, "r", encoding="utf-8") as f:
        texts = [line.strip() for line in f if line.strip()]
    
    # 随机打乱
    random.shuffle(texts)
    
    # 分割
    val_size = int(len(texts) * val_ratio)
    val_texts = texts[:val_size]
    train_texts = texts[val_size:]
    
    # 保存
    with open(train_path, "w", encoding="utf-8") as f:
        for text in train_texts:
            f.write(text + "\n")
    
    with open(val_path, "w", encoding="utf-8") as f:
        for text in val_texts:
            f.write(text + "\n")
    
    print(f"训练集: {len(train_texts)} 条")
    print(f"验证集: {len(val_texts)} 条")


def data_stats(data_path: str):
    """数据统计"""
    
    with open(data_path, "r", encoding="utf-8") as f:
        texts = [line.strip() for line in f if line.strip()]
    
    lengths = [len(text) for text in texts]
    
    print("=" * 50)
    print("数据统计")
    print("=" * 50)
    print(f"总条数: {len(texts)}")
    print(f"最短长度: {min(lengths)}")
    print(f"最长长度: {max(lengths)}")
    print(f"平均长度: {sum(lengths) / len(lengths):.1f}")
    print(f"总字符数: {sum(lengths)}")
    print("=" * 50)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="天光AI数据准备工具")
    parser.add_argument("command", choices=["create", "merge", "filter", "split", "stats"])
    parser.add_argument("--input", type=str)
    parser.add_argument("--output", type=str, default="data/training_data.txt")
    parser.add_argument("--num", type=int, default=1000)
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_sample_data(args.output, args.num)
    elif args.command == "merge":
        merge_data_files(args.input, args.output)
    elif args.command == "filter":
        filter_data(args.input, args.output)
    elif args.command == "split":
        split_data(args.input, "data/train.txt", "data/val.txt")
    elif args.command == "stats":
        data_stats(args.input)
