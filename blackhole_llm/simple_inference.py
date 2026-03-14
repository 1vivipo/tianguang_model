#!/usr/bin/env python3
"""
简单推理脚本 - 使用训练好的模型生成文本

使用方法：
    python simple_inference.py --prompt "人工智能"
    python simple_inference.py --prompt "Python" --max_len 50
"""

import os
import sys
import pickle
import argparse

MODEL_DIR = "/home/z/tianguang_model/trained_model"


def load_models():
    """加载模型"""
    # 加载分词器
    with open(os.path.join(MODEL_DIR, "tokenizer.pkl"), 'rb') as f:
        tokenizer_data = pickle.load(f)
    
    # 加载N-gram模型
    with open(os.path.join(MODEL_DIR, "ngram_model.pkl"), 'rb') as f:
        ngram_data = pickle.load(f)
    
    return tokenizer_data, ngram_data


def generate(tokenizer_data, ngram_data, prompt: str, max_len: int = 30):
    """生成文本"""
    word2id = tokenizer_data['word2id']
    id2word = tokenizer_data['id2word']
    ngram_counts = ngram_data['ngram_counts']
    context_counts = ngram_data['context_counts']
    n = ngram_data['n']
    
    # 编码提示
    import re
    words = re.findall(r'[\u4e00-\u9fff]|[a-zA-Z]+|[0-9]+', prompt.lower())
    context = [word2id.get(w, 1) for w in words]
    
    if not context:
        context = [2]  # <bos>
    
    # 生成
    import random
    for _ in range(max_len):
        ctx = tuple(context[-(n-1):])
        
        if ctx not in ngram_counts:
            break
        
        candidates = ngram_counts[ctx]
        total = context_counts[ctx]
        
        if total == 0:
            break
        
        # 采样
        r = random.random() * total
        cumsum = 0
        next_word = None
        for word, count in candidates.items():
            cumsum += count
            if cumsum >= r:
                next_word = word
                break
        
        if next_word is None or next_word == 3:  # <eos>
            break
        
        context.append(next_word)
    
    # 解码
    result = "".join(id2word.get(i, "<unk>") for i in context)
    return result


def main():
    parser = argparse.ArgumentParser(description="简单推理")
    parser.add_argument("--prompt", type=str, default="人工智能", help="提示词")
    parser.add_argument("--max_len", type=int, default=30, help="最大生成长度")
    parser.add_argument("--num", type=int, default=3, help="生成数量")
    
    args = parser.parse_args()
    
    print("加载模型...")
    tokenizer_data, ngram_data = load_models()
    
    print(f"\n提示: {args.prompt}")
    print("-" * 50)
    
    for i in range(args.num):
        result = generate(tokenizer_data, ngram_data, args.prompt, args.max_len)
        print(f"{i+1}. {result}")


if __name__ == "__main__":
    main()
