"""
突突 Tutu 配置文件
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class CrawlerConfig:
    """爬虫配置"""
    # 爬取间隔（秒）
    crawl_interval: int = 300  # 5分钟爬一次
    
    # 每次爬取数量
    crawl_count: int = 10
    
    # 爬取源
    sources: List[str] = field(default_factory=lambda: [
        "https://news.baidu.com",           # 百度新闻
        "https://www.zhihu.com/hot",        # 知乎热榜
        "https://www.36kr.com",             # 36氪
        "https://www.sohu.com",             # 搜狐
        "https://www.jiqizhixin.com",       # 机器之心
        "https://www.pingwest.com",         # 品玩
    ])
    
    # 关键词（爬取重点）
    keywords: List[str] = field(default_factory=lambda: [
        "人工智能", "AI", "机器学习", "深度学习",
        "科技", "互联网", "创业", "投资",
        "Python", "编程", "开发", "技术",
    ])
    
    # 是否启用
    enabled: bool = True
    
    # User-Agent
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

@dataclass
class LearnerConfig:
    """学习器配置"""
    # 学习间隔（秒）
    learn_interval: int = 600  # 10分钟学一次
    
    # 每次学习样本数
    batch_size: int = 32
    
    # 学习率
    learning_rate: float = 1e-4
    
    # 是否启用
    enabled: bool = True
    
    # 最小知识数才开始学习
    min_knowledge: int = 100

@dataclass
class ClassifierConfig:
    """分类器配置"""
    # 分类类别
    categories: List[str] = field(default_factory=lambda: [
        "科技", "财经", "教育", "娱乐", "体育",
        "健康", "生活", "文化", "政治", "其他"
    ])
    
    # 自动分类阈值
    threshold: float = 0.5

@dataclass
class MemoryConfig:
    """记忆配置"""
    # 知识库路径
    knowledge_dir: str = "./knowledge"
    
    # 最大知识条数
    max_knowledge: int = 100000
    
    # 是否启用压缩
    enable_compression: bool = True

@dataclass
class APIConfig:
    """API配置"""
    port: int = 8080
    api_key: str = "sk-tutu-2024-auto-learn"
    model_name: str = "tutu-1.0"

@dataclass
class TutuConfig:
    """突突总配置"""
    crawler: CrawlerConfig = field(default_factory=CrawlerConfig)
    learner: LearnerConfig = field(default_factory=LearnerConfig)
    classifier: ClassifierConfig = field(default_factory=ClassifierConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    api: APIConfig = field(default_factory=APIConfig)
    
    @classmethod
    def from_env(cls) -> "TutuConfig":
        config = cls()
        config.api.port = int(os.environ.get("PORT", 8080))
        config.api.api_key = os.environ.get("API_KEY", config.api.api_key)
        return config

# 默认配置
default_config = TutuConfig()
