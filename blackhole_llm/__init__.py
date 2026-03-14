"""
黑洞 Blackhole LLM - 分布式智能体集群

核心概念：
- 100只虫子并行爬取不同领域
- 100条神经并行训练学习
- 知识黑洞吞噬所有知识
- 几天内变得超级强大

架构：
┌─────────────────────────────────────────────────────────┐
│                   黑洞 Blackhole LLM                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     ┌─────┐          │
│  │虫子1│ │虫子2│ │虫子3│ │虫子4│ ... │虫子N│  100只虫  │
│  │科技 │ │财经 │ │健康 │ │教育 │     │娱乐 │          │
│  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘     └──┬──┘          │
│     └───────┴───────┴───────┴───────────┘              │
│                     ↓                                   │
│              ┌──────────┐                               │
│              │ 知识黑洞  │  吞噬所有知识                │
│              └────┬─────┘                               │
│                   │                                     │
│     ┌─────────────┼─────────────┐                      │
│     ↓             ↓             ↓                      │
│  ┌─────┐     ┌─────┐     ┌─────┐                      │
│  │神经1│     │神经2│     │神经N│   100条神经          │
│  │训练 │     │训练 │     │训练 │                      │
│  └──┬──┘     └──┬──┘     └──┬──┘                      │
│     └───────────┴───────────┘                          │
│                 ↓                                       │
│          ┌──────────┐                                   │
│          │ 超级大脑  │                                   │
│          └──────────┘                                   │
└─────────────────────────────────────────────────────────┘

部署后效果：
- 每5分钟：100只虫子同时爬取 → 100个领域知识
- 每10分钟：100条神经同时训练 → 100倍学习速度
- 每天：爬取28800条知识，训练1440次
- 几天后：知识量爆炸，模型超强
"""

__version__ = "1.0.0"
__author__ = "Blackhole Team"

from .config import BlackholeConfig
from .swarm.crawler_swarm import CrawlerSwarm
from .neural.neural_cluster import NeuralCluster
from .core.knowledge_blackhole import KnowledgeBlackhole
from .core.coordinator import Coordinator
from .api.server import create_app

__all__ = [
    "BlackholeConfig",
    "CrawlerSwarm",
    "NeuralCluster",
    "KnowledgeBlackhole",
    "Coordinator",
    "create_app"
]
