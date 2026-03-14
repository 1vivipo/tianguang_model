#!/usr/bin/env python3
"""
洱海 Urhai LLM 初始化脚本
快速初始化并启动服务
"""

import os
import sys

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║                    洱海 Urhai LLM                        ║
║                  真实AI架构版 v1.0                        ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 创建必要目录
    dirs = ["knowledge", "memory", "model", "checkpoints"]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"✓ 创建目录: {d}/")
    
    # 检查依赖
    print("\n检查依赖...")
    missing = []
    
    try:
        import torch
        print(f"✓ torch {torch.__version__}")
    except ImportError:
        missing.append("torch")
    
    try:
        import flask
        print(f"✓ flask {flask.__version__}")
    except ImportError:
        missing.append("flask")
    
    try:
        import jieba
        print(f"✓ jieba {jieba.__version__}")
    except ImportError:
        missing.append("jieba")
    
    if missing:
        print(f"\n缺少依赖: {', '.join(missing)}")
        print("请运行: pip install " + " ".join(missing))
        return
    
    # 检查模型
    print("\n检查模型...")
    if os.path.exists("model/model.bin"):
        print("✓ 模型已存在")
    else:
        print("⚠ 模型不存在，将使用模板模式")
        print("  要训练模型，请运行: python train.py")
    
    # 启动服务
    print("\n启动API服务...")
    print("API Key: sk-urhai-2024-llm-key")
    print("Port: 8080")
    print()
    
    from api.server import create_app
    from config import UrhaiConfig
    
    config = UrhaiConfig.from_env()
    app = create_app(config)
    app.run(host="0.0.0.0", port=config.api.port)


if __name__ == "__main__":
    main()
