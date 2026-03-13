/**
 * 天光AI - 快速训练配置
 * 针对浏览器端优化的训练参数
 */

// 快速训练配置
const QUICK_TRAIN_CONFIG = {
    // 只用少量数据
    maxDataSize: 500,      // 最多500条数据
    
    // 减少训练轮次
    epochs: 20,            // 只训练20轮
    
    // 增大学习率
    learningRate: 0.02,    // 更快收敛
    
    // 减小批次
    batchSize: 8,          // 批次大小
    
    // 更小的模型
    embedDim: 32,          // 嵌入维度
    hiddenDim: 64,         // 隐藏层维度
    
    // 更短的序列
    seqLength: 16,         // 序列长度
};

// 中等配置（平衡速度和效果）
const BALANCED_CONFIG = {
    maxDataSize: 1000,
    epochs: 30,
    learningRate: 0.015,
    batchSize: 8,
    embedDim: 48,
    hiddenDim: 96,
    seqLength: 24,
};

// 完整配置（效果最好，最慢）
const FULL_CONFIG = {
    maxDataSize: 2000,
    epochs: 50,
    learningRate: 0.01,
    batchSize: 4,
    embedDim: 64,
    hiddenDim: 128,
    seqLength: 32,
};

// 导出
window.QUICK_TRAIN_CONFIG = QUICK_TRAIN_CONFIG;
window.BALANCED_CONFIG = BALANCED_CONFIG;
window.FULL_CONFIG = FULL_CONFIG;
