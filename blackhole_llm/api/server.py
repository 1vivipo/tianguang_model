"""
黑洞 Blackhole LLM API服务

功能：
1. 对话接口
2. 状态监控
3. 手动触发
4. 知识查询
"""

import os
import time
from datetime import datetime
from typing import Dict

from flask import Flask, request, jsonify
from flask_cors import CORS

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config, default_config


def create_app(config: Config = None) -> Flask:
    """创建Flask应用"""
    config = config or default_config
    
    app = Flask(__name__)
    CORS(app)
    
    # 初始化组件
    print("\n" + "="*60)
    print("  🕳️ 黑洞 Blackhole LLM 初始化")
    print("="*60)
    
    # 1. 知识黑洞
    print("\n[1/4] 创建知识黑洞...")
    from core.knowledge_blackhole import KnowledgeBlackhole
    blackhole = KnowledgeBlackhole(config.blackhole)
    
    # 2. 虫群
    print("[2/4] 创建虫群...")
    from swarm.crawler_swarm import CrawlerSwarm
    swarm = CrawlerSwarm(config.swarm, blackhole)
    
    # 3. 神经网络群
    print("[3/4] 创建神经网络群...")
    from neural.neural_cluster import NeuralCluster
    neural = NeuralCluster(config.neural, blackhole)
    
    # 4. 协调器
    print("[4/4] 创建协调器...")
    from core.coordinator import Coordinator
    coordinator = Coordinator(swarm, neural, blackhole)
    
    # 启动
    if config.swarm.enabled:
        coordinator.start()
    
    print("\n" + "="*60)
    print("  ✓ 黑洞初始化完成！")
    print(f"  ✓ 虫群: {len(swarm.agents)} 只虫子并行爬取")
    print(f"  ✓ 神经: {len(neural.networks)} 条神经并行训练")
    print(f"  ✓ 知识: {len(blackhole.knowledge)} 条")
    print("="*60 + "\n")
    
    @app.route('/')
    def index():
        return jsonify({
            "name": "黑洞 Blackhole LLM",
            "version": "1.0.0",
            "model": config.api.model_name,
            "status": "running",
            "features": [
                "🕷️ 100只虫子并行爬取",
                "🧠 10条神经并行训练",
                "🕳️ 知识黑洞吞噬一切",
                "⚡ 几天内变得超强"
            ],
            "scale": {
                "crawlers": len(swarm.agents),
                "networks": len(neural.networks),
                "knowledge": len(blackhole.knowledge)
            },
            "api_key": config.api.api_key
        })
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        key = request.headers.get('X-API-KEY', '')
        if key != config.api.api_key:
            return jsonify({"error": "Invalid API key"}), 401
        
        data = request.get_json() or {}
        message = data.get('message', '') or data.get('query', '')
        
        if not message:
            return jsonify({"error": "No message"}), 400
        
        # 搜索知识黑洞
        results = blackhole.search(message, top_k=5)
        
        if results:
            answer_parts = [f"黑洞知识库找到 {len(results)} 条相关信息：\n"]
            for i, r in enumerate(results, 1):
                domain = r.get('domain', '未知')
                title = r.get('title', '')
                content = r.get('content', '')[:200]
                answer_parts.append(f"{i}. 【{domain}】{title}\n   {content}...")
            answer = "\n".join(answer_parts)
        else:
            answer = f"黑洞正在学习「{message}」相关知识，请稍后再问！"
        
        return jsonify({
            "answer": answer,
            "sources": len(results),
            "knowledge_total": len(blackhole.knowledge)
        })
    
    @app.route('/api/status', methods=['GET'])
    def status():
        """获取状态"""
        return jsonify(coordinator.get_stats())
    
    @app.route('/api/crawl', methods=['POST'])
    def trigger_crawl():
        """手动触发爬取"""
        key = request.headers.get('X-API-KEY', '')
        if key != config.api.api_key:
            return jsonify({"error": "Invalid API key"}), 401
        
        results = swarm.crawl_all_parallel()
        absorbed = blackhole.absorb(results)
        
        return jsonify({
            "crawled": len(results),
            "absorbed": absorbed
        })
    
    @app.route('/api/train', methods=['POST'])
    def trigger_train():
        """手动触发训练"""
        key = request.headers.get('X-API-KEY', '')
        if key != config.api.api_key:
            return jsonify({"error": "Invalid API key"}), 401
        
        results = neural.train_all_parallel()
        
        return jsonify({
            "trained": len(results),
            "avg_loss": sum(r.get('loss', 0) for r in results) / max(1, len(results))
        })
    
    @app.route('/api/knowledge', methods=['GET'])
    def get_knowledge():
        """获取知识"""
        domain = request.args.get('domain', '')
        limit = int(request.args.get('limit', 20))
        
        if domain:
            items = blackhole.get_by_domain(domain)[:limit]
        else:
            items = blackhole.sample(limit)
        
        return jsonify({
            "total": len(blackhole.knowledge),
            "items": items
        })
    
    @app.route('/api/domains', methods=['GET'])
    def get_domains():
        """获取领域统计"""
        stats = blackhole.get_stats()
        return jsonify({
            "domains": stats["domains"],
            "total": stats["total_knowledge"]
        })
    
    return app


if __name__ == "__main__":
    config = Config.from_env()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                 黑洞 Blackhole LLM                      ║
║               分布式智能体集群 v1.0                      ║
╠══════════════════════════════════════════════════════════╣
║  🕷️ 100只虫子并行爬取 - 每5分钟出击一次                 ║
║  🧠 10条神经并行训练 - 每10分钟学习一次                 ║
║  🕳️ 知识黑洞吞噬一切 - 几天内变得超强                   ║
╠══════════════════════════════════════════════════════════╣
║  API Key: {config.api.api_key:<42} ║
║  Port:    {config.api.port:<42} ║
╚══════════════════════════════════════════════════════════╝
""")
    
    app = create_app(config)
    app.run(host="0.0.0.0", port=config.api.port)
