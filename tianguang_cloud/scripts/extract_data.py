#!/usr/bin/env python3
"""
从JS文件提取训练数据，生成纯文本文件
"""

import re
import os

def extract_data_from_js(js_file, output_file):
    """从JS文件提取数据"""

    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取所有引号中的文本
    pattern = r'"([^"]+)"'
    matches = re.findall(pattern, content)

    # 过滤有效的句子
    texts = []
    for match in matches:
        # 跳过太短或包含特殊字符的
        if len(match) > 10 and not match.startswith('BUILTIN') and not match.startswith('console'):
            # 跳过纯英文变量名
            if any('\u4e00' <= c <= '\u9fff' for c in match):
                texts.append(match)

    # 去重
    texts = list(set(texts))

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        for text in texts:
            f.write(text + '\n')

    print(f"提取了 {len(texts)} 条数据")
    print(f"保存到: {output_file}")

    return texts

if __name__ == '__main__':
    js_file = 'training_data.js'
    output_file = 'training_data.txt'

    texts = extract_data_from_js(js_file, output_file)

    # 统计
    total_chars = sum(len(t) for t in texts)
    print(f"总字符数: {total_chars}")
    print(f"文件大小约: {total_chars / 1024:.1f} KB")
