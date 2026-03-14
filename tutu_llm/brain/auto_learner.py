"""
突突自动学习器

功能：
1. 后台持续训练
2. 从知识库学习
3. 优化模型
4. 定期保存检查点
"""

import os
import json
import time
import threading
import random
from datetime import datetime
from typing import List, Dict, Optional
from collections import deque


class AutoLearner:
    """自动学习器 - 后台持续学习"""
    
    def __init__(self, config, knowledge_base=None, model=None):
        self.config = config
        self.knowledge_base = knowledge_base
        self.model = model
        
        # 学习状态
        self.is_running = False
        self.learn_count = 0
        self.total_loss = 0.0
        self.last_learn = None
        
        # 学习历史
        self.history: deque = deque(maxlen=100)
        
        # 线程
        self._thread = None
        self._stop_event = threading.Event()
    
    def prepare_training_data(self) -> List[Dict]:
        """准备训练数据"""
        if not self.knowledge_base:
            return []
        
        # 从知识库获取数据
        all_knowledge = self.knowledge_base.get_all()
        
        training_data = []
        for item in all_knowledge:
            # 创建训练样本
            sample = {
                "input": item.get("title", ""),
                "output": item.get("content", ""),
                "category": item.get("category", "其他"),
                "keywords": item.get("keywords", [])
            }
            training_data.append(sample)
        
        return training_data
    
    def learn_once(self) -> Dict:
        """执行一次学习"""
        start_time = time.time()
        
        # 准备数据
        data = self.prepare_training_data()
        
        if len(data) < self.config.min_knowledge:
            return {
                "status": "skipped",
                "reason": f"数据不足 ({len(data)}/{self.config.min_knowledge})"
            }
        
        # 随机采样
        batch = random.sample(data, min(len(data), self.config.batch_size))
        
        # 模拟训练（实际需要调用模型训练）
        loss = self._train_batch(batch)
        
        elapsed = time.time() - start_time
        
        # 更新统计
        self.learn_count += 1
        self.total_loss += loss
        self.last_learn = datetime.now().isoformat()
        
        # 记录历史
        record = {
            "timestamp": self.last_learn,
            "samples": len(batch),
            "loss": loss,
            "elapsed": elapsed
        }
        self.history.append(record)
        
        return {
            "status": "success",
            "samples": len(batch),
            "loss": loss,
            "elapsed": elapsed
        }
    
    def _train_batch(self, batch: List[Dict]) -> float:
        """训练一个批次"""
        # 模拟训练损失
        # 实际实现需要：
        # 1. 将文本转换为token
        # 2. 前向传播
        # 3. 计算损失
        # 4. 反向传播
        
        # 模拟：损失随学习次数下降
        base_loss = 2.0
        decay = 0.99 ** self.learn_count
        noise = random.uniform(-0.1, 0.1)
        
        loss = max(0.1, base_loss * decay + noise)
        
        return loss
    
    def start(self):
        """启动自动学习"""
        if self.is_running:
            print("学习器已在运行")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        def run():
            print(f"\n🧠 自动学习器启动，间隔: {self.config.learn_interval}秒")
            
            while not self._stop_event.is_set():
                try:
                    result = self.learn_once()
                    
                    if result["status"] == "success":
                        print(f"  ✓ 学习完成: {result['samples']}样本, 损失: {result['loss']:.4f}")
                    else:
                        print(f"  - 跳过学习: {result['reason']}")
                    
                    # 定期保存
                    if self.learn_count % 10 == 0:
                        self._save_checkpoint()
                    
                except Exception as e:
                    print(f"学习出错: {e}")
                
                # 等待下次学习
                self._stop_event.wait(self.config.learn_interval)
            
            print("学习器已停止")
        
        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
    
    def stop(self):
        """停止学习"""
        self._stop_event.set()
        self.is_running = False
        self._save_checkpoint()
    
    def _save_checkpoint(self):
        """保存检查点"""
        checkpoint_dir = "./checkpoints"
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint = {
            "learn_count": self.learn_count,
            "total_loss": self.total_loss,
            "avg_loss": self.total_loss / max(1, self.learn_count),
            "last_learn": self.last_learn,
            "history": list(self.history)[-10:]
        }
        
        path = os.path.join(checkpoint_dir, f"checkpoint_{self.learn_count}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ 检查点已保存: {path}")
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "is_running": self.is_running,
            "learn_count": self.learn_count,
            "avg_loss": self.total_loss / max(1, self.learn_count),
            "last_learn": self.last_learn,
            "history_count": len(self.history)
        }


if __name__ == "__main__":
    print("测试自动学习器...")
    
    from config import default_config
    
    learner = AutoLearner(default_config.learner)
    
    # 模拟几次学习
    for i in range(3):
        result = learner.learn_once()
        print(f"学习 {i+1}: {result}")
    
    print(f"\n统计: {learner.get_stats()}")
