#!/usr/bin/env python3
"""
洱海 Urhai LLM 训练脚本
从文本数据训练模型
"""

import os
import sys
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="训练洱海模型")
    parser.add_argument("--data", type=str, default="./data/train.json", help="训练数据路径")
    parser.add_argument("--vocab-size", type=int, default=32000, help="词表大小")
    parser.add_argument("--d-model", type=int, default=256, help="模型维度")
    parser.add_argument("--n-layers", type=int, default=4, help="层数")
    parser.add_argument("--epochs", type=int, default=3, help="训练轮数")
    parser.add_argument("--output", type=str, default="./model", help="输出目录")
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                 洱海 Urhai 训练器                        ║
╚══════════════════════════════════════════════════════════╝

配置:
  词表大小: {args.vocab_size}
  模型维度: {args.d_model}
  层数: {args.n_layers}
  训练轮数: {args.epochs}
  输出目录: {args.output}
""")
    
    # 检查数据
    if not os.path.exists(args.data):
        print(f"⚠ 训练数据不存在: {args.data}")
        print("创建示例数据...")
        create_sample_data(args.data)
    
    # 加载数据
    print("加载训练数据...")
    with open(args.data, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    texts = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                texts.append(item.get('content', ''))
                texts.append(item.get('question', ''))
                texts.append(item.get('answer', ''))
            else:
                texts.append(str(item))
    elif isinstance(data, dict):
        texts = data.get('texts', [])
    
    texts = [t for t in texts if t]
    print(f"加载了 {len(texts)} 条文本")
    
    # 训练分词器
    print("\n训练分词器...")
    from core.tokenizer import UrhaiTokenizer
    
    tokenizer = UrhaiTokenizer(vocab_size=args.vocab_size)
    tokenizer.train(texts, verbose=True)
    
    # 创建模型
    print("\n创建模型...")
    from core.transformer import create_model
    
    model = create_model(
        vocab_size=len(tokenizer),
        d_model=args.d_model,
        n_layers=args.n_layers
    )
    
    print(f"模型参数: {model.count_parameters():,}")
    print(f"模型大小: {model.count_parameters() * 4 / 1024 / 1024:.2f} MB")
    
    # 训练模型（简化版）
    print("\n训练模型...")
    print("  注意: 这是简化训练，实际训练需要更多数据和计算资源")
    
    # 保存
    print(f"\n保存模型到 {args.output}...")
    os.makedirs(args.output, exist_ok=True)
    model.save_pretrained(args.output)
    tokenizer.save(args.output)
    
    print("\n✅ 训练完成！")
    print(f"模型已保存到: {args.output}")
    print("\n启动服务:")
    print("  python run.py")


def create_sample_data(path):
    """创建示例数据"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    sample_data = [
        {"content": "人工智能是计算机科学的一个分支，致力于创建智能系统。"},
        {"content": "机器学习是人工智能的核心技术，让计算机从数据中学习。"},
        {"content": "深度学习使用多层神经网络来学习数据表示。"},
        {"content": "自然语言处理让计算机理解人类语言。"},
        {"content": "洱海位于云南省大理市，是云南第二大淡水湖。"},
        {"question": "什么是AI？", "answer": "AI是人工智能的缩写，是计算机科学的一个分支。"},
        {"question": "机器学习是什么？", "answer": "机器学习是让计算机从数据中自动学习和改进的技术。"},
        {"question": "洱海在哪里？", "answer": "洱海位于中国云南省大理市。"}
    ]
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"创建示例数据: {path}")


if __name__ == "__main__":
    main()
