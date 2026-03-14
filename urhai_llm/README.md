# 洱海 Urhai LLM - 真实AI架构版

🌊 **自己的AI，边用边学，无限成长**

## ✨ 特点

| 特性 | 说明 |
|------|------|
| **混合架构** | 检索系统 + 神经网络 |
| **增量学习** | 边用边学，越用越聪明 |
| **长期记忆** | 永久保存学到的知识 |
| **无限成长** | 没有知识上限 |
| **完全自主** | 不依赖任何第三方大模型 |

## 🏗️ 架构

```
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
```

## 📁 目录结构

```
urhai_llm/
├── core/                  # 核心组件
│   ├── transformer.py     # 神经网络模型
│   ├── tokenizer.py       # 分词器
│   ├── retriever.py       # 检索系统
│   └── memory.py          # 长期记忆
├── training/              # 训练系统
│   ├── learner.py         # 增量学习器
│   └── trainer.py         # 训练器
├── api/                   # API服务
│   └── server.py          # Flask服务
├── config.py              # 配置
├── requirements.txt       # 依赖
└── README.md              # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python -m api.server
```

### 3. 调用API

```bash
curl -X POST http://localhost:8080/api/chat \
     -H "Content-Type: application/json" \
     -H "X-API-KEY: sk-urhai-2024-llm-key" \
     -d '{"message": "你好"}'
```

## 🧠 训练模型

### 从文本训练

```python
from core.transformer import create_model
from core.tokenizer import UrhaiTokenizer

# 创建模型
model = create_model(vocab_size=32000, d_model=256)

# 训练分词器
tokenizer = UrhaiTokenizer(vocab_size=32000)
tokenizer.train(your_texts)

# 保存
model.save_pretrained("./model")
tokenizer.save("./model")
```

### 增量学习

```python
from training.learner import IncrementalLearner

learner = IncrementalLearner(model, tokenizer)

# 从对话学习
learner.add_sample("什么是AI", "AI是人工智能...")

# 从反馈学习
learner.learn_from_feedback(
    message="洱海在哪里",
    response="洱海在昆明",  # 错误
    feedback="correct",
    correction="洱海在大理"  # 正确
)
```

## 📡 API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/v1/chat/completions` | POST | OpenAI风格对话 |
| `/api/chat` | POST | 简化对话接口 |
| `/api/learn` | POST | 学习接口 |
| `/api/stats` | GET | 统计信息 |

## 🔧 配置

```python
from config import UrhaiConfig

config = UrhaiConfig()
config.model.d_model = 256      # 模型维度
config.model.n_layers = 4       # 层数
config.learning.learning_rate = 1e-4  # 学习率
```

## 💡 与假AI的区别

| 特性 | 假AI (MetaBrain) | 真AI (Urhai) |
|------|------------------|--------------|
| 架构 | 检索+模板 | 检索+神经网络 |
| 学习 | 不学习 | 边用边学 |
| 记忆 | 无 | 长期记忆 |
| 成长 | 固定知识 | 无限成长 |
| 生成 | 模板拼接 | 神经网络生成 |

## 📊 模型规格

| 配置 | 参数量 | 内存占用 |
|------|--------|----------|
| tiny | ~5M | ~20MB |
| small | ~15M | ~60MB |
| base | ~30M | ~120MB |

---

**洱海 Urhai - 自己的AI，无限成长！** 🌊
