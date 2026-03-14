"""
洱海 Urhai 配置文件
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ModelConfig:
    """模型配置"""
    # 词表大小
    vocab_size: int = 32000
    
    # 模型维度
    d_model: int = 256
    d_ff: int = 512
    
    # 层数（轻量级）
    n_layers: int = 4
    n_heads: int = 4
    
    # 序列长度
    max_seq_len: int = 512
    
    # Dropout
    dropout: float = 0.1
    
    # 设备
    device: str = "cpu"

@dataclass
class RetrieverConfig:
    """检索系统配置"""
    # 知识库路径
    knowledge_dir: str = "./knowledge"
    
    # 检索数量
    top_k: int = 5
    
    # 相似度阈值
    threshold: float = 0.3
    
    # 是否启用网络搜索
    enable_web_search: bool = True

@dataclass
class MemoryConfig:
    """记忆系统配置"""
    # 记忆文件路径
    memory_file: str = "./memory/long_term.json"
    
    # 最大记忆条数
    max_memories: int = 10000
    
    # 记忆衰减（越久远的记忆权重越低）
    memory_decay: float = 0.99

@dataclass
class LearningConfig:
    """学习系统配置"""
    # 学习率
    learning_rate: float = 1e-4
    
    # 批次大小
    batch_size: int = 8
    
    # 是否启用在线学习
    enable_online_learning: bool = True
    
    # 学习频率（每N次对话学习一次）
    learn_every_n: int = 10
    
    # 最小学习样本数
    min_samples: int = 5

@dataclass
class APIConfig:
    """API配置"""
    # 服务端口
    port: int = 8080
    
    # API密钥
    api_key: str = "sk-urhai-2024-llm-key"
    
    # 模型名称
    model_name: str = "urhai-1.0"
    
    # 是否启用CORS
    enable_cors: bool = True

@dataclass
class UrhaiConfig:
    """洱海总配置"""
    model: ModelConfig = field(default_factory=ModelConfig)
    retriever: RetrieverConfig = field(default_factory=RetrieverConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    learning: LearningConfig = field(default_factory=LearningConfig)
    api: APIConfig = field(default_factory=APIConfig)
    
    @classmethod
    def from_env(cls) -> "UrhaiConfig":
        """从环境变量加载配置"""
        config = cls()
        
        # API配置
        config.api.port = int(os.environ.get("PORT", 8080))
        config.api.api_key = os.environ.get("API_KEY", config.api.api_key)
        config.api.model_name = os.environ.get("MODEL_NAME", config.api.model_name)
        
        # 模型配置
        if os.environ.get("URHAI_D_MODEL"):
            config.model.d_model = int(os.environ.get("URHAI_D_MODEL"))
        
        return config
    
    def save(self, path: str):
        """保存配置"""
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "model": self.model.__dict__,
                "retriever": self.retriever.__dict__,
                "memory": self.memory.__dict__,
                "learning": self.learning.__dict__,
                "api": self.api.__dict__
            }, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: str) -> "UrhaiConfig":
        """加载配置"""
        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        config = cls()
        config.model = ModelConfig(**data.get("model", {}))
        config.retriever = RetrieverConfig(**data.get("retriever", {}))
        config.memory = MemoryConfig(**data.get("memory", {}))
        config.learning = LearningConfig(**data.get("learning", {}))
        config.api = APIConfig(**data.get("api", {}))
        
        return config

# 默认配置实例
default_config = UrhaiConfig()
