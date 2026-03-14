"""
黑洞神经网络群 - 多条神经并行训练

每条神经负责一个领域：
- 神经1: 科技领域专家
- 神经2: 财经领域专家
- 神经3: 健康领域专家
- ...
- 神经N: 综合领域专家

并行训练，同时学习！
"""

import os
import json
import time
import random
import threading
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import queue


@dataclass
class NeuralNetwork:
    """单条神经网络"""
    id: int
    domain: str
    d_model: int = 256
    n_layers: int = 4
    
    def __post_init__(self):
        self.train_count = 0
        self.total_loss = 0.0
        self.last_train = None
        self.status = "idle"
        
        # 模拟模型参数
        self.params = {
            "d_model": self.d_model,
            "n_layers": self.n_layers,
            "vocab_size": 32000
        }
    
    def train_batch(self, batch: List[Dict]) -> float:
        """训练一个批次"""
        self.status = "training"
        
        # 模拟训练（实际需要PyTorch）
        # 损失随训练次数下降
        base_loss = 2.0
        decay = 0.99 ** self.train_count
        noise = random.uniform(-0.1, 0.1)
        
        loss = max(0.1, base_loss * decay + noise)
        
        self.train_count += 1
        self.total_loss += loss
        self.last_train = datetime.now().isoformat()
        self.status = "idle"
        
        return loss
    
    def get_avg_loss(self) -> float:
        return self.total_loss / max(1, self.train_count)


class NeuralCluster:
    """神经网络群 - 多条神经并行训练"""
    
    def __init__(self, config, knowledge_blackhole=None):
        self.config = config
        self.knowledge_blackhole = knowledge_blackhole
        
        # 创建神经网络群
        self.networks: List[NeuralNetwork] = []
        self._create_cluster()
        
        # 状态
        self.is_running = False
        self.total_trained = 0
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=config.num_networks)
        
        # 停止信号
        self._stop_event = threading.Event()
    
    def _create_cluster(self):
        """创建神经网络群"""
        # 领域分组
        domains = [
            ("科技", ["人工智能", "机器学习", "深度学习", "编程", "互联网"]),
            ("财经", ["股票", "基金", "投资", "经济", "金融"]),
            ("健康", ["医疗", "养生", "健身", "营养", "心理"]),
            ("教育", ["学习", "考试", "培训", "留学", "考研"]),
            ("生活", ["美食", "旅游", "汽车", "房产", "家居"]),
            ("文化", ["历史", "文学", "艺术", "哲学", "传统"]),
            ("科学", ["物理", "化学", "生物", "数学", "天文"]),
            ("社会", ["政治", "法律", "军事", "国际", "社会"]),
            ("综合", []),  # 综合领域
            ("热点", []),  # 热点话题
        ]
        
        for i, (domain, keywords) in enumerate(domains[:self.config.num_networks]):
            network = NeuralNetwork(
                id=i + 1,
                domain=domain,
                d_model=self.config.d_model,
                n_layers=self.config.n_layers
            )
            self.networks.append(network)
        
        print(f"✓ 神经网络群创建完成: {len(self.networks)} 条神经")
    
    def train_with_network(self, network: NeuralNetwork, data: List[Dict]) -> Dict:
        """单条神经训练"""
        try:
            network.status = "training"
            
            # 准备训练数据
            batch = random.sample(data, min(len(data), self.config.batch_size))
            
            # 训练
            loss = network.train_batch(batch)
            
            return {
                "network_id": network.id,
                "domain": network.domain,
                "samples": len(batch),
                "loss": loss,
                "avg_loss": network.get_avg_loss()
            }
            
        except Exception as e:
            return {
                "network_id": network.id,
                "error": str(e)
            }
    
    def train_all_parallel(self) -> List[Dict]:
        """所有神经并行训练"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🧠 神经群训练！{len(self.networks)}条神经并行学习...")
        
        # 获取知识
        if self.knowledge_blackhole:
            data = self.knowledge_blackhole.sample(self.config.batch_size * 10)
        else:
            data = []
        
        if len(data) < 10:
            print("  数据不足，跳过训练")
            return []
        
        results = []
        futures = []
        
        # 提交所有训练任务
        for network in self.networks:
            future = self.executor.submit(self.train_with_network, network, data)
            futures.append(future)
        
        # 收集结果
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                pass
        
        # 更新统计
        self.total_trained += len(results)
        
        avg_loss = sum(r.get('loss', 0) for r in results) / max(1, len(results))
        print(f"  ✓ 本次训练: {len(results)} 条神经, 平均损失: {avg_loss:.4f}")
        
        return results
    
    def start(self):
        """启动训练"""
        if self.is_running:
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        def run():
            print(f"\n🧠 神经网络群启动！{len(self.networks)}条神经，间隔{self.config.train_interval}秒")
            
            while not self._stop_event.is_set():
                try:
                    self.train_all_parallel()
                except Exception as e:
                    print(f"训练错误: {e}")
                
                self._stop_event.wait(self.config.train_interval)
            
            print("神经网络群已停止")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def stop(self):
        """停止训练"""
        self._stop_event.set()
        self.is_running = False
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "is_running": self.is_running,
            "total_networks": len(self.networks),
            "total_trained": self.total_trained,
            "networks": [
                {
                    "id": n.id,
                    "domain": n.domain,
                    "train_count": n.train_count,
                    "avg_loss": n.get_avg_loss()
                }
                for n in self.networks
            ]
        }


if __name__ == "__main__":
    print("测试神经网络群...")
    
    from config import default_config
    
    cluster = NeuralCluster(default_config.neural)
    
    # 测试一次训练
    results = cluster.train_all_parallel()
    
    print(f"\n训练结果:")
    for r in results:
        print(f"  [{r['domain']}] 样本: {r['samples']}, 损失: {r['loss']:.4f}")
    
    print(f"\n统计: {cluster.get_stats()}")
