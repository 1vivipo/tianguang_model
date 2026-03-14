#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天光AI - MetaBrain V3.1 API服务
标准AI调用接口，兼容OpenAI风格

启动方式：
    python api_server.py

调用方式：
    # OpenAI风格
    curl -X POST http://localhost:8088/v1/chat/completions \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer sk-tianguang-2024-metabrain-v31" \
         -d '{"model": "metabrain-v3.1", "messages": [{"role": "user", "content": "你好"}]}'
    
    # 简化风格
    curl -X POST http://localhost:8088/api/chat \
         -H "Content-Type: application/json" \
         -H "X-API-KEY: sk-tianguang-2024-metabrain-v31" \
         -d '{"query": "你好"}'
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入元脑核心
from metabrain_final import (
    MetaBrainV31, GLOBAL_CONFIG, DEFAULT_STYLE_LIBRARY,
    datetime, logging, json
)

from flask import Flask, request, jsonify
from flask_cors import CORS
import time

# ==================== API配置 ====================

API_KEY = "sk-tianguang-2024-metabrain-v31"
API_SECRET = "tianguang-secret-key-2024"
MODEL_NAME = "metabrain-v3.1"

# ==================== 创建Flask应用 ====================

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    CORS(app)
    
    # 初始化元脑
    print("正在初始化元脑...")
    brain = MetaBrainV31()
    print("元脑初始化完成！")
    
    # ==================== 标准接口 ====================
    
    @app.route('/')
    def index():
        """服务信息"""
        return jsonify({
            "name": "天光AI - MetaBrain",
            "version": "3.1.0",
            "model": MODEL_NAME,
            "status": "running",
            "api_key": API_KEY,
            "endpoints": {
                "openai_style": "POST /v1/chat/completions",
                "simple_style": "POST /api/chat",
                "search": "GET /api/search",
                "health": "GET /health"
            }
        })
    
    @app.route('/health')
    def health():
        """健康检查"""
        return jsonify({
            "status": "healthy",
            "model": MODEL_NAME,
            "timestamp": datetime.now().isoformat()
        })
    
    # ==================== OpenAI风格接口 ====================
    
    @app.route('/v1/chat/completions', methods=['POST'])
    def chat_completions():
        """OpenAI风格的对话接口"""
        try:
            # 鉴权
            auth = request.headers.get('Authorization', '')
            if auth.startswith('Bearer '):
                api_key = auth[7:]
            else:
                api_key = request.headers.get('X-API-KEY', '')
            
            if api_key != API_KEY:
                return jsonify({
                    "error": {
                        "message": "Invalid API key",
                        "type": "invalid_request_error"
                    }
                }), 401
            
            # 解析请求
            data = request.get_json()
            messages = data.get('messages', [])
            model = data.get('model', MODEL_NAME)
            temperature = data.get('temperature', 0.7)
            max_tokens = data.get('max_tokens', 1000)
            
            # 提取用户消息
            user_message = ""
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    user_message = msg.get('content', '')
                    break
            
            if not user_message:
                return jsonify({
                    "error": {
                        "message": "No user message found",
                        "type": "invalid_request_error"
                    }
                }), 400
            
            # 调用元脑
            result = brain.chat(user_message, enable_online_search=True)
            
            # 构建OpenAI风格响应
            response = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": result.get("answer", "")
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(user_message),
                    "completion_tokens": len(result.get("answer", "")),
                    "total_tokens": len(user_message) + len(result.get("answer", ""))
                }
            }
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({
                "error": {
                    "message": str(e),
                    "type": "server_error"
                }
            }), 500
    
    @app.route('/v1/models', methods=['GET'])
    def list_models():
        """模型列表"""
        return jsonify({
            "object": "list",
            "data": [
                {
                    "id": MODEL_NAME,
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": "tianguang"
                }
            ]
        })
    
    # ==================== 简化接口 ====================
    
    @app.route('/api/chat', methods=['POST'])
    def simple_chat():
        """简化对话接口"""
        try:
            # 鉴权
            api_key = request.headers.get('X-API-KEY', '')
            if api_key != API_KEY:
                return jsonify({"error": "无效的API密钥"}), 401
            
            data = request.get_json()
            query = data.get('query', '')
            style = data.get('style')
            session_id = data.get('session_id')
            enable_online_search = data.get('enable_online_search', True)
            
            if not query:
                return jsonify({"error": "请提供query参数"}), 400
            
            result = brain.chat(query, session_id, style, enable_online_search)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/search', methods=['GET'])
    def search():
        """搜索接口"""
        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "请提供搜索参数q"}), 400
        
        results = brain.online_search_engine.search(query)
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
    
    @app.route('/api/sessions', methods=['POST'])
    def create_session():
        """创建会话"""
        data = request.get_json() or {}
        tenant_id = data.get('tenant_id', 'default')
        user_id = data.get('user_id', 'default_user')
        
        session = brain.session_manager.create_session(tenant_id, user_id)
        return jsonify({
            "session_id": session.session_id,
            "tenant_id": session.tenant_id,
            "user_id": session.user_id
        })
    
    return app


# ==================== 主入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("  天光AI - MetaBrain V3.1 API服务")
    print("  标准AI调用接口 | 兼容OpenAI风格")
    print("=" * 60)
    print()
    print("  API配置:")
    print(f"    URL: http://localhost:8088")
    print(f"    API Key: {API_KEY}")
    print(f"    Model: {MODEL_NAME}")
    print()
    print("  调用方式:")
    print()
    print("  # OpenAI风格:")
    print('  curl -X POST http://localhost:8088/v1/chat/completions \\')
    print('       -H "Content-Type: application/json" \\')
    print(f'       -H "Authorization: Bearer {API_KEY}" \\')
    print('       -d \'{"model": "metabrain-v3.1", "messages": [{"role": "user", "content": "你好"}]}\'')
    print()
    print("  # 简化风格:")
    print('  curl -X POST http://localhost:8088/api/chat \\')
    print('       -H "Content-Type: application/json" \\')
    print(f'       -H "X-API-KEY: {API_KEY}" \\')
    print('       -d \'{"query": "你好"}\'')
    print()
    print("=" * 60)
    
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=8088,
        debug=False
    )
