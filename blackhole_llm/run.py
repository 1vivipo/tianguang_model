#!/usr/bin/env python3
"""
黑洞 Blackhole LLM 启动脚本
"""

import os
import sys

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║                 黑洞 Blackhole LLM                      ║
║               分布式智能体集群 v1.0                      ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 创建目录
    dirs = ["blackhole_knowledge", "checkpoints"]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"✓ 创建目录: {d}/")
    
    # 检查依赖
    print("\n检查依赖...")
    
    try:
        import flask
        print(f"✓ flask {flask.__version__}")
    except ImportError:
        print("✗ 缺少 flask")
        return
    
    try:
        import requests
        print(f"✓ requests {requests.__version__}")
    except ImportError:
        print("✗ 缺少 requests")
        return
    
    # 启动
    print("\n启动黑洞...")
    print("  - 虫群: 100只虫子并行爬取")
    print("  - 神经: 10条神经并行训练")
    print("  - 间隔: 爬取5分钟/训练10分钟")
    print()
    
    from api.server import create_app
    from config import Config
    
    config = Config.from_env()
    app = create_app(config)
    app.run(host="0.0.0.0", port=config.api.port)


if __name__ == "__main__":
    main()
