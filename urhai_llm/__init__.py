"""
洱海 Urhai LLM - 真实AI架构版
混合架构：检索系统 + 神经网络 + 增量学习

特点：
1. 检索系统 - 精确知识获取
2. 神经网络 - 自然语言生成
3. 增量学习 - 边用边学，无限成长
4. 长期记忆 - 永久保存学到的知识

架构：
┌─────────────────────────────────────────────────┐
│                   洱海 Urhai                     │
├─────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 检索系统  │  │ 神经网络  │  │ 学习系统  │      │
│  │ (精确)   │  │ (生成)   │  │ (成长)   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │             │            │
│       └─────────────┼─────────────┘            │
│                     ▼                          │
│              ┌──────────┐                      │
│              │ 融合输出  │                      │
│              └──────────┘                      │
│                     │                          │
│                     ▼                          │
│              ┌──────────┐                      │
│              │ 长期记忆  │ ← 持久化存储         │
│              └──────────┘                      │
└─────────────────────────────────────────────────┘
"""

__version__ = "1.0.0"
__author__ = "Urhai Team"

# 核心组件
from .core.transformer import UrhaiTransformer
from .core.tokenizer import UrhaiTokenizer
from .core.retriever import KnowledgeRetriever
from .core.memory import LongTermMemory

# 学习系统
from .training.learner import IncrementalLearner
from .training.trainer import UrhaiTrainer

# API
from .api.server import create_app

# 配置
from .config import UrhaiConfig

__all__ = [
    "UrhaiTransformer",
    "UrhaiTokenizer", 
    "KnowledgeRetriever",
    "LongTermMemory",
    "IncrementalLearner",
    "UrhaiTrainer",
    "create_app",
    "UrhaiConfig"
]
