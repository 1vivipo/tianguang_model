"""
天光AI - 配置文件
"""

class Config:
    """模型配置"""
    
    # 模型架构
    model_type = "gpt"  # gpt, transformer, lstm
    
    # 词表
    vocab_size = 8000    # 词表大小
    max_length = 128     # 最大序列长度
    
    # 模型维度
    hidden_size = 256    # 隐藏层大小
    num_layers = 4       # 层数
    num_heads = 4        # 注意力头数
    intermediate_size = 512  # FFN中间层大小
    
    # 正则化
    hidden_dropout = 0.1
    attention_dropout = 0.1
    
    # 训练参数
    batch_size = 16
    learning_rate = 5e-4
    weight_decay = 0.01
    warmup_steps = 1000
    max_steps = 50000
    
    # 学习率调度
    lr_scheduler = "cosine"  # linear, cosine, constant
    
    # 梯度
    max_grad_norm = 1.0
    gradient_accumulation_steps = 4
    
    # 保存
    save_steps = 2000
    eval_steps = 1000
    log_steps = 100
    
    # 路径
    data_path = "data/training_data.txt"
    output_dir = "models/tianguang_model"
    
    # 设备
    device = "cuda"  # cuda, cpu, mps
    
    # 精度
    fp16 = True  # 使用混合精度训练
    
    # 生成参数
    max_new_tokens = 50
    temperature = 0.8
    top_k = 50
    top_p = 0.9
    do_sample = True


class SmallConfig(Config):
    """小模型配置 - 适合快速测试"""
    hidden_size = 128
    num_layers = 2
    num_heads = 2
    intermediate_size = 256
    vocab_size = 4000


class MediumConfig(Config):
    """中等模型配置 - 推荐使用"""
    hidden_size = 256
    num_layers = 4
    num_heads = 4
    intermediate_size = 512
    vocab_size = 8000


class LargeConfig(Config):
    """大模型配置 - 需要更多GPU内存"""
    hidden_size = 512
    num_layers = 6
    num_heads = 8
    intermediate_size = 1024
    vocab_size = 10000


# 默认配置
config = Config()
