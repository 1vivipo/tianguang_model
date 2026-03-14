"""
黑洞 Blackhole 配置文件
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict

# 100个领域定义
DOMAINS_100 = [
    # 科技类 (20个)
    "人工智能", "机器学习", "深度学习", "自然语言处理", "计算机视觉",
    "机器人", "区块链", "云计算", "大数据", "物联网",
    "网络安全", "移动开发", "前端开发", "后端开发", "数据库",
    "操作系统", "编程语言", "软件工程", "硬件", "芯片",
    
    # 财经类 (15个)
    "股票", "基金", "债券", "期货", "外汇",
    "银行", "保险", "投资", "理财", "经济",
    "金融", "创业", "融资", "上市", "税务",
    
    # 健康类 (15个)
    "医疗", "养生", "健身", "营养", "中医",
    "西医", "心理健康", "疾病预防", "药品", "医疗器械",
    "美容", "减肥", "睡眠", "老年健康", "儿童健康",
    
    # 教育类 (10个)
    "学前教育", "基础教育", "高等教育", "职业教育", "在线教育",
    "语言学习", "考试", "留学", "考研", "技能培训",
    
    # 生活类 (15个)
    "美食", "旅游", "汽车", "房产", "家居",
    "时尚", "购物", "宠物", "婚恋", "育儿",
    "社交", "娱乐", "游戏", "音乐", "电影",
    
    # 文化类 (10个)
    "历史", "文学", "艺术", "哲学", "宗教",
    "传统文化", "世界文化", "考古", "博物馆", "非物质文化遗产",
    
    # 科学类 (10个)
    "物理", "化学", "生物", "数学", "天文",
    "地理", "环境", "能源", "材料", "航空航天",
    
    # 社会类 (5个)
    "政治", "法律", "军事", "国际关系", "社会热点"
]

@dataclass
class SwarmConfig:
    """虫群配置"""
    # 虫子数量
    num_crawlers: int = 100
    
    # 每只虫子的爬取间隔（秒）
    crawl_interval: int = 300  # 5分钟
    
    # 每只虫子每次爬取数量
    crawl_per_agent: int = 5
    
    # 领域分配
    domains: List[str] = field(default_factory=lambda: DOMAINS_100)
    
    # 是否启用
    enabled: bool = True
    
    # 并发数
    max_concurrent: int = 20  # 最多20只虫子同时工作

@dataclass
class NeuralConfig:
    """神经网络群配置"""
    # 神经网络数量
    num_networks: int = 10  # 10条神经并行训练
    
    # 每条神经的训练间隔
    train_interval: int = 600  # 10分钟
    
    # 批次大小
    batch_size: int = 64
    
    # 学习率
    learning_rate: float = 1e-4
    
    # 是否启用
    enabled: bool = True
    
    # 模型维度
    d_model: int = 256
    n_layers: int = 4

@dataclass
class BlackholeConfig:
    """黑洞核心配置"""
    # 知识黑洞容量
    max_knowledge: int = 1000000  # 100万条知识
    
    # 知识存储路径
    knowledge_dir: str = "./blackhole_knowledge"
    
    # 是否启用压缩
    enable_compression: bool = True
    
    # 知识融合间隔
    merge_interval: int = 1800  # 30分钟融合一次

@dataclass
class APIConfig:
    """API配置"""
    port: int = 8080
    api_key: str = "sk-blackhole-2024-swarm"
    model_name: str = "blackhole-1.0"

@dataclass
class Config:
    """黑洞总配置"""
    swarm: SwarmConfig = field(default_factory=SwarmConfig)
    neural: NeuralConfig = field(default_factory=NeuralConfig)
    blackhole: BlackholeConfig = field(default_factory=BlackholeConfig)
    api: APIConfig = field(default_factory=APIConfig)
    
    @classmethod
    def from_env(cls) -> "Config":
        config = cls()
        config.api.port = int(os.environ.get("PORT", 8080))
        config.api.api_key = os.environ.get("API_KEY", config.api.api_key)
        
        # 根据环境调整规模
        if os.environ.get("BLACKHOLE_SCALE") == "mini":
            config.swarm.num_crawlers = 10
            config.neural.num_networks = 2
        elif os.environ.get("BLACKHOLE_SCALE") == "full":
            config.swarm.num_crawlers = 100
            config.neural.num_networks = 10
        
        return config

# 默认配置
default_config = Config()
