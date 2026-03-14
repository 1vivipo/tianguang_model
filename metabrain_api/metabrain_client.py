#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天光AI - MetaBrain 客户端SDK
标准AI调用接口，兼容OpenAI风格

使用方式：
    from metabrain_client import TianguangAI
    
    client = TianguangAI(
        api_key="sk-tianguang-2024-metabrain-v31",
        base_url="http://localhost:8088"
    )
    
    response = client.chat("你好")
    print(response)
"""

import requests
import json
import time
from typing import Optional, List, Dict, Any


class TianguangAI:
    """天光AI客户端 - 标准AI调用接口"""
    
    def __init__(
        self,
        api_key: str = "sk-tianguang-2024-metabrain-v31",
        api_secret: str = None,
        base_url: str = "http://localhost:8088",
        model: str = "metabrain-v3.1"
    ):
        """
        初始化客户端
        
        Args:
            api_key: API密钥
            api_secret: API密钥（可选）
            base_url: 服务地址
            model: 模型名称
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.model = model
        
        # 默认参数
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "style": "default",
            "enable_online_search": True
        }
    
    def chat(
        self,
        message: str,
        style: str = None,
        enable_online_search: bool = True,
        session_id: str = None,
        **kwargs
    ) -> str:
        """
        对话接口
        
        Args:
            message: 用户消息
            style: 回答风格 (default/professional/friendly/brief)
            enable_online_search: 是否联网搜索
            session_id: 会话ID
            
        Returns:
            AI回答
        """
        url = f"{self.base_url}/api/chat"
        
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key
        }
        
        data = {
            "query": message,
            "style": style or self.default_params["style"],
            "enable_online_search": enable_online_search,
            "session_id": session_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get("answer", "")
        except Exception as e:
            return f"错误: {str(e)}"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        OpenAI风格的对话接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "你好"}]
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            OpenAI风格的响应
        """
        # 提取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # 调用对话接口
        answer = self.chat(user_message)
        
        # 返回OpenAI风格响应
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model or self.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": answer
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message),
                "completion_tokens": len(answer),
                "total_tokens": len(user_message) + len(answer)
            }
        }
    
    def search(self, query: str) -> List[Dict]:
        """
        搜索接口
        
        Args:
            query: 搜索关键词
            
        Returns:
            搜索结果列表
        """
        url = f"{self.base_url}/api/search"
        
        headers = {
            "X-API-KEY": self.api_key
        }
        
        try:
            response = requests.get(url, headers=headers, params={"q": query}, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get("results", [])
        except Exception as e:
            return [{"error": str(e)}]
    
    def create_session(self, tenant_id: str = "default", user_id: str = "default") -> str:
        """
        创建会话
        
        Args:
            tenant_id: 租户ID
            user_id: 用户ID
            
        Returns:
            会话ID
        """
        url = f"{self.base_url}/api/sessions"
        
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key
        }
        
        data = {
            "tenant_id": tenant_id,
            "user_id": user_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result.get("session_id", "")
        except Exception as e:
            return ""
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            服务是否正常
        """
        url = f"{self.base_url}/health"
        
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


# ==================== 便捷函数 ====================

def chat(message: str, **kwargs) -> str:
    """快速对话函数"""
    client = TianguangAI()
    return client.chat(message, **kwargs)


def search(query: str) -> List[Dict]:
    """快速搜索函数"""
    client = TianguangAI()
    return client.search(query)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("  天光AI - MetaBrain 客户端测试")
    print("=" * 60)
    
    # 创建客户端
    client = TianguangAI(
        api_key="sk-tianguang-2024-metabrain-v31",
        base_url="http://localhost:8088"
    )
    
    # 健康检查
    print("\n1. 健康检查...")
    if client.health_check():
        print("   ✅ 服务正常")
    else:
        print("   ❌ 服务未启动")
        print("   请先运行: python metabrain_final.py")
        exit(1)
    
    # 测试对话
    print("\n2. 测试对话...")
    questions = [
        "你好，介绍一下自己",
        "今天天气怎么样",
        "什么是人工智能"
    ]
    
    for q in questions:
        print(f"\n   问: {q}")
        answer = client.chat(q)
        print(f"   答: {answer[:100]}...")
    
    # 测试OpenAI风格接口
    print("\n3. 测试OpenAI风格接口...")
    response = client.chat_completion([
        {"role": "user", "content": "你好"}
    ])
    print(f"   响应: {json.dumps(response, ensure_ascii=False, indent=2)[:200]}...")
    
    print("\n" + "=" * 60)
    print("  测试完成！")
    print("=" * 60)
