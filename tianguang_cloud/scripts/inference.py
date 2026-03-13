"""
天光AI - 推理脚本
使用训练好的模型生成文本
"""

import os
import sys
import argparse

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from model import TianguangModel
from tokenizer import TianguangTokenizer


def generate(
    model_path: str,
    prompt: str,
    max_new_tokens: int = 100,
    temperature: float = 0.8,
    top_k: int = 50,
    top_p: float = 0.9,
    device: str = "cuda"
):
    """使用模型生成文本"""
    
    # 设置设备
    device = torch.device(device if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    # 加载模型
    print(f"加载模型: {model_path}")
    model = TianguangModel.from_pretrained(model_path)
    model = model.to(device)
    model.eval()
    
    # 加载分词器
    tokenizer = TianguangTokenizer.from_pretrained(model_path)
    
    # 编码输入
    input_ids = torch.tensor([tokenizer.encode(prompt, add_bos=True, add_eos=False)]).to(device)
    
    print(f"\n输入: {prompt}")
    print("-" * 50)
    
    # 生成
    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            do_sample=True
        )
    
    # 解码
    output_text = tokenizer.decode(output_ids[0].tolist(), skip_special_tokens=True)
    
    print(f"输出: {output_text}")
    print("-" * 50)
    
    return output_text


def interactive(model_path: str, device: str = "cuda"):
    """交互式对话"""
    
    # 设置设备
    device = torch.device(device if torch.cuda.is_available() else "cpu")
    
    # 加载模型
    print(f"加载模型: {model_path}")
    model = TianguangModel.from_pretrained(model_path)
    model = model.to(device)
    model.eval()
    
    # 加载分词器
    tokenizer = TianguangTokenizer.from_pretrained(model_path)
    
    print("\n" + "=" * 50)
    print("天光AI - 交互式对话")
    print("输入 'quit' 退出")
    print("=" * 50 + "\n")
    
    while True:
        try:
            prompt = input("你: ").strip()
            
            if prompt.lower() == "quit":
                print("再见！")
                break
            
            if not prompt:
                continue
            
            # 编码
            input_ids = torch.tensor([tokenizer.encode(prompt, add_bos=True, add_eos=False)]).to(device)
            
            # 生成
            with torch.no_grad():
                output_ids = model.generate(
                    input_ids,
                    max_new_tokens=100,
                    temperature=0.8,
                    top_k=50,
                    top_p=0.9,
                    do_sample=True
                )
            
            # 解码
            output_text = tokenizer.decode(output_ids[0].tolist(), skip_special_tokens=True)
            
            print(f"AI: {output_text}\n")
            
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    parser = argparse.ArgumentParser(description="天光AI推理脚本")
    parser.add_argument("--model", type=str, default="models/tianguang_model", help="模型路径")
    parser.add_argument("--prompt", type=str, default="人工智能", help="输入提示")
    parser.add_argument("--max_tokens", type=int, default=100, help="最大生成长度")
    parser.add_argument("--temperature", type=float, default=0.8, help="温度参数")
    parser.add_argument("--top_k", type=int, default=50, help="Top-K采样")
    parser.add_argument("--top_p", type=float, default=0.9, help="Top-P采样")
    parser.add_argument("--device", type=str, default="cuda", help="设备")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive(args.model, args.device)
    else:
        generate(
            args.model,
            args.prompt,
            args.max_tokens,
            args.temperature,
            args.top_k,
            args.top_p,
            args.device
        )


if __name__ == "__main__":
    main()
