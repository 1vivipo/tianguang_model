#!/usr/bin/env python3
"""
黑洞 Blackhole LLM - 小说生成脚本

用途：用训练好的模型生成小说
时机：模型训练完成后

使用方法：
    python novel_generator.py --model ./trained_model --prompt "在一个风雨交加的夜晚" --length 1000

参数说明：
    --model    训练好的模型目录
    --prompt   开头提示
    --length   生成长度（字数）
    --output   输出文件
    --temperature  创造性程度（0.5-1.5，越高越随机）
"""

import os
import sys
import json
import argparse
from datetime import datetime


def generate_novel(
    model_dir: str,
    prompt: str,
    length: int = 1000,
    temperature: float = 0.8,
    output_file: str = None
):
    """生成小说"""
    import torch
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║            黑洞 Blackhole LLM 小说生成器                ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 检查模型
    model_path = os.path.join(model_dir, "model.pt")
    tokenizer_path = os.path.join(model_dir, "tokenizer.json")
    
    if not os.path.exists(model_path):
        print(f"❌ 模型不存在: {model_path}")
        print("请先运行 train_from_blackhole.py 训练模型")
        return
    
    # 加载模型
    print("加载模型...")
    from train_from_blackhole import SimpleTransformer, SimpleTokenizer
    
    tokenizer = SimpleTokenizer()
    tokenizer.load(tokenizer_path)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SimpleTransformer(vocab_size=len(tokenizer.word2id))
    model.load(model_path)
    model.to(device)
    model.eval()
    
    print(f"✓ 模型加载完成，设备: {device}")
    
    # 生成
    print(f"\n开始生成...")
    print(f"提示: {prompt}")
    print(f"目标长度: {length}字")
    print("-" * 50)
    
    # 编码
    input_ids = torch.tensor([tokenizer.encode(prompt)]).to(device)
    
    # 分段生成
    generated_text = prompt
    target_length = length
    
    while len(generated_text) < target_length:
        # 生成一段
        output_ids = model.generate(
            input_ids,
            max_new_tokens=min(100, target_length - len(generated_text)),
            temperature=temperature
        )
        
        # 解码
        new_text = tokenizer.decode(output_ids[0].tolist())
        
        # 更新
        generated_text = new_text
        input_ids = output_ids
        
        # 打印进度
        print(f"已生成: {len(generated_text)}字")
    
    # 打印结果
    print("\n" + "=" * 50)
    print("生成的小说:")
    print("=" * 50)
    print(generated_text)
    print("=" * 50)
    
    # 保存
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(generated_text)
        print(f"\n✓ 已保存到: {output_file}")
    
    return generated_text


def interactive_mode(model_dir: str):
    """交互模式"""
    import torch
    from train_from_blackhole import SimpleTransformer, SimpleTokenizer
    
    # 加载模型
    print("加载模型...")
    tokenizer = SimpleTokenizer()
    tokenizer.load(os.path.join(model_dir, "tokenizer.json"))
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SimpleTransformer(vocab_size=len(tokenizer.word2id))
    model.load(os.path.join(model_dir, "model.pt"))
    model.to(device)
    model.eval()
    
    print(f"\n✓ 模型加载完成")
    print("输入提示开始生成，输入 'quit' 退出")
    print("-" * 50)
    
    while True:
        prompt = input("\n请输入开头: ").strip()
        
        if prompt.lower() == 'quit':
            break
        
        if not prompt:
            continue
        
        # 生成
        input_ids = torch.tensor([tokenizer.encode(prompt)]).to(device)
        output_ids = model.generate(input_ids, max_new_tokens=200, temperature=0.8)
        
        generated = tokenizer.decode(output_ids[0].tolist())
        
        print(f"\n生成结果:")
        print(generated)


def main():
    parser = argparse.ArgumentParser(description="黑洞小说生成器")
    parser.add_argument("--model", type=str, default="./trained_model", help="模型目录")
    parser.add_argument("--prompt", type=str, default="", help="开头提示")
    parser.add_argument("--length", type=int, default=1000, help="生成长度")
    parser.add_argument("--temperature", type=float, default=0.8, help="创造性程度")
    parser.add_argument("--output", type=str, default=None, help="输出文件")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode(args.model)
    elif args.prompt:
        generate_novel(
            model_dir=args.model,
            prompt=args.prompt,
            length=args.length,
            temperature=args.temperature,
            output_file=args.output
        )
    else:
        print("请提供 --prompt 或使用 --interactive 模式")


if __name__ == "__main__":
    main()
