"""
突突 Tutu LLM - 自主学习AI

特点：
1. 🚀 自动爬取 - 自己上网找知识
2. 🧠 自动学习 - 自己训练自己
3. 📚 自动分类 - 自己整理知识库
4. 🔄 持续进化 - 24小时不停学习
5. 💪 越来越强 - 用得越多越聪明

工作流程：
┌─────────────────────────────────────────────────────────┐
│                    突突 Tutu LLM                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐ │
│  │ 自动爬虫 │ → │ 自动分类 │ → │ 自动训练 │ → │ 知识库  │ │
│  │ 24/7    │   │ 整理    │   │ 学习    │   │ 更新    │ │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘ │
│       ↑                                          │      │
│       └──────────────────────────────────────────┘      │
│                     循环学习                            │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐                                           │
│  │ API服务 │ ← 用户随时调用                            │
│  └─────────┘                                           │
└─────────────────────────────────────────────────────────┘

部署后：
- 自动爬取新闻、百科、技术文章
- 自动分类存入知识库
- 自动训练优化模型
- 24小时不间断学习
- 没人用也在成长！
"""

__version__ = "1.0.0"
__author__ = "Tutu Team"

from .config import TutuConfig
from .crawler.auto_crawler import AutoCrawler
from .brain.auto_learner import AutoLearner
from .brain.classifier import KnowledgeClassifier
from .memory.knowledge_base import KnowledgeBase
from .api.server import create_app

__all__ = [
    "TutuConfig",
    "AutoCrawler",
    "AutoLearner", 
    "KnowledgeClassifier",
    "KnowledgeBase",
    "create_app"
]
