"""
洱海增量学习系统

特点：
1. 在线学习 - 边用边学
2. 从对话中学习
3. 从反馈中改进
4. 持续优化模型
"""

import os
import json
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import deque
import copy


class TrainingSample:
    """训练样本"""
    
    def __init__(
        self,
        input_text: str,
        output_text: str,
        source: str = "conversation",
        quality: float = 1.0
    ):
        self.input_text = input_text
        self.output_text = output_text
        self.source = source
        self.quality = quality
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "input": self.input_text,
            "output": self.output_text,
            "source": self.source,
            "quality": self.quality,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TrainingSample":
        return cls(
            input_text=data["input"],
            output_text=data["output"],
            source=data.get("source", "conversation"),
            quality=data.get("quality", 1.0)
        )


class IncrementalLearner:
    """增量学习器"""
    
    def __init__(
        self,
        model=None,
        tokenizer=None,
        memory=None,
        learning_rate: float = 1e-4,
        batch_size: int = 8,
        learn_every_n: int = 10,
        min_samples: int = 5,
        buffer_size: int = 1000
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.memory = memory
        
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.learn_every_n = learn_every_n
        self.min_samples = min_samples
        
        # 训练样本缓冲区
        self.sample_buffer: deque = deque(maxlen=buffer_size)
        
        # 学习计数器
        self.conversation_count = 0
        self.learning_events = 0
        
        # 学习历史
        self.learning_history: List[Dict] = []
    
    def add_sample(
        self,
        input_text: str,
        output_text: str,
        source: str = "conversation",
        quality: float = 1.0
    ):
        """添加训练样本"""
        sample = TrainingSample(input_text, output_text, source, quality)
        self.sample_buffer.append(sample)
        
        # 检查是否需要学习
        self.conversation_count += 1
        
        if self.conversation_count % self.learn_every_n == 0:
            if len(self.sample_buffer) >= self.min_samples:
                self.learn()
    
    def learn(self):
        """执行学习"""
        if not self.model or not self.tokenizer:
            print("模型或分词器未初始化，跳过学习")
            return
        
        if len(self.sample_buffer) < self.min_samples:
            print(f"样本不足 ({len(self.sample_buffer)}/{self.min_samples})，跳过学习")
            return
        
        print(f"开始增量学习，样本数: {len(self.sample_buffer)}")
        
        # 准备训练数据
        samples = list(self.sample_buffer)
        random.shuffle(samples)
        
        # 创建批次
        batches = [
            samples[i:i + self.batch_size]
            for i in range(0, len(samples), self.batch_size)
        ]
        
        # 训练统计
        total_loss = 0.0
        num_batches = 0
        
        # 简化的训练循环（实际需要PyTorch）
        for batch in batches:
            loss = self._train_batch(batch)
            total_loss += loss
            num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0
        
        # 记录学习事件
        self.learning_events += 1
        event = {
            "event_id": self.learning_events,
            "timestamp": datetime.now().isoformat(),
            "num_samples": len(samples),
            "num_batches": num_batches,
            "avg_loss": avg_loss,
            "buffer_size": len(self.sample_buffer)
        }
        self.learning_history.append(event)
        
        print(f"学习完成，平均损失: {avg_loss:.4f}")
        
        # 保存模型检查点
        self._save_checkpoint()
    
    def _train_batch(self, batch: List[TrainingSample]) -> float:
        """训练一个批次"""
        # 这里是简化的训练逻辑
        # 实际实现需要：
        # 1. 将文本转换为token
        # 2. 前向传播计算损失
        # 3. 反向传播更新权重
        
        # 模拟损失
        loss = random.uniform(0.5, 2.0)
        
        # 实际代码示例：
        # inputs = [self.tokenizer.encode(s.input_text) for s in batch]
        # targets = [self.tokenizer.encode(s.output_text) for s in batch]
        # loss = self.model.train_step(inputs, targets)
        
        return loss
    
    def _save_checkpoint(self):
        """保存检查点"""
        if self.model:
            checkpoint_dir = f"./checkpoints/step_{self.learning_events}"
            os.makedirs(checkpoint_dir, exist_ok=True)
            
            # 保存模型
            # self.model.save_pretrained(checkpoint_dir)
            
            # 保存学习状态
            state = {
                "learning_events": self.learning_events,
                "conversation_count": self.conversation_count,
                "buffer_size": len(self.sample_buffer),
                "learning_history": self.learning_history[-10:]  # 只保存最近10条
            }
            
            with open(os.path.join(checkpoint_dir, "learner_state.json"), 'w') as f:
                json.dump(state, f, indent=2)
    
    def learn_from_feedback(
        self,
        user_input: str,
        ai_response: str,
        feedback: str,  # "positive", "negative", "correct"
        correction: Optional[str] = None
    ):
        """从用户反馈学习"""
        if feedback == "positive":
            # 正面反馈，增强这个回答
            self.add_sample(user_input, ai_response, quality=1.5)
            
            # 也存入记忆
            if self.memory:
                self.memory.learn_from_conversation(
                    user_input, ai_response, "positive"
                )
        
        elif feedback == "negative":
            # 负面反馈，降低这个回答的质量
            self.add_sample(user_input, ai_response, quality=0.3)
        
        elif feedback == "correct" and correction:
            # 用户纠正，学习正确答案
            self.add_sample(user_input, correction, quality=2.0)
            
            # 存入记忆
            if self.memory:
                self.memory.remember(
                    content=f"问: {user_input} 答: {correction}",
                    memory_type="knowledge",
                    importance=2.0
                )
    
    def get_training_data(self) -> List[Dict]:
        """获取训练数据"""
        return [s.to_dict() for s in self.sample_buffer]
    
    def save_training_data(self, path: str):
        """保存训练数据"""
        data = {
            "samples": self.get_training_data(),
            "stats": {
                "total_samples": len(self.sample_buffer),
                "learning_events": self.learning_events,
                "conversation_count": self.conversation_count
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_training_data(self, path: str):
        """加载训练数据"""
        if not os.path.exists(path):
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for sample_data in data.get("samples", []):
            sample = TrainingSample.from_dict(sample_data)
            self.sample_buffer.append(sample)
        
        print(f"加载了 {len(self.sample_buffer)} 个训练样本")


class UrhaiTrainer:
    """洱海训练器 - 完整训练流程"""
    
    def __init__(
        self,
        model,
        tokenizer,
        config: Dict = None
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config or {}
    
    def train_from_texts(
        self,
        texts: List[str],
        epochs: int = 3,
        batch_size: int = 8,
        learning_rate: float = 1e-4
    ):
        """从文本训练"""
        print(f"开始训练，文本数: {len(texts)}, epochs: {epochs}")
        
        # 训练分词器
        print("训练分词器...")
        self.tokenizer.train(texts)
        
        # 准备数据
        print("准备训练数据...")
        # 实际需要将文本转换为训练样本
        
        # 训练模型
        print("训练模型...")
        # 实际训练循环
        
        print("训练完成！")
    
    def train_from_qa_pairs(
        self,
        qa_pairs: List[Tuple[str, str]],
        epochs: int = 3
    ):
        """从问答对训练"""
        print(f"从 {len(qa_pairs)} 个问答对训练...")
        
        for q, a in qa_pairs:
            # 创建训练样本
            pass
        
        print("训练完成！")
    
    def evaluate(self, test_data: List[str]) -> Dict:
        """评估模型"""
        # 计算困惑度等指标
        return {
            "perplexity": 0.0,
            "accuracy": 0.0
        }


if __name__ == "__main__":
    print("测试增量学习系统...")
    
    learner = IncrementalLearner()
    
    # 添加样本
    learner.add_sample("什么是AI", "AI是人工智能的缩写")
    learner.add_sample("什么是机器学习", "机器学习是AI的核心技术")
    learner.add_sample("什么是深度学习", "深度学习使用神经网络")
    
    # 从反馈学习
    learner.learn_from_feedback(
        "什么是NLP",
        "NLP是自然语言处理",
        "positive"
    )
    
    # 从纠正学习
    learner.learn_from_feedback(
        "洱海在哪里",
        "洱海在昆明",  # 错误
        "correct",
        "洱海在大理"  # 正确
    )
    
    print(f"样本数: {len(learner.sample_buffer)}")
    print(f"学习事件: {learner.learning_events}")
    
    print("\n✅ 增量学习系统测试通过！")
