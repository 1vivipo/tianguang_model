# 黑洞 Blackhole LLM - 使用指南

## 📋 目录

1. [当前能力说明](#当前能力说明)
2. [部署方法](#部署方法)
3. [训练脚本使用](#训练脚本使用)
4. [小说生成](#小说生成)
5. [常见问题](#常见问题)

---

## 当前能力说明

### ✅ 现在就能做的

| 功能 | 状态 | 说明 |
|------|------|------|
| 知识爬取 | ✅ 可用 | 100只虫子爬知识 |
| 知识存储 | ✅ 可用 | 存到知识库 |
| 知识搜索 | ✅ 可用 | 搜索回答问题 |
| API服务 | ✅ 可用 | 可以调用 |
| 分类整理 | ✅ 可用 | 自动分类 |

### ⚠️ 需要训练后才能做的

| 功能 | 状态 | 说明 |
|------|------|------|
| 小说生成 | ⚠️ 需训练 | 需要GPU训练 |
| 创意写作 | ⚠️ 需训练 | 需要GPU训练 |
| 对话生成 | ⚠️ 需训练 | 需要GPU训练 |

### 当前版本 vs 训练后版本

```
当前版本（检索模式）：
用户: 写一个小说开头
AI: 我找到以下相关信息：
    1. 小说写作技巧...
    2. 经典小说开头...
    （搜索结果，不是创作）

训练后版本（生成模式）：
用户: 写一个小说开头
AI: 在一个风雨交加的夜晚，李明独自走在空旷的街道上...
    （真正的创作）
```

---

## 部署方法

### 方法一：Railway（免费）

1. 访问 https://railway.app
2. 用GitHub登录
3. 选择 `tianguang_model` 仓库
4. 设置 Root Directory: `blackhole_llm`
5. 设置环境变量: `BLACKHOLE_SCALE=mini`
6. 部署

### 方法二：自己的服务器

```bash
# 1. 克隆仓库
git clone https://github.com/1vivipo/tianguang_model.git

# 2. 进入目录
cd tianguang_model/blackhole_llm

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动
python run.py
```

---

## 训练脚本使用

### 第一步：积累知识

让黑洞跑1-3个月，积累知识

### 第二步：导出知识

```bash
# 知识在 blackhole_knowledge 目录
ls blackhole_knowledge/
```

### 第三步：训练模型

在火山引擎/阿里云/AutoDL租GPU：

```bash
# 安装依赖
pip install torch numpy

# 运行训练
python train_from_blackhole.py \
    --knowledge ./blackhole_knowledge \
    --epochs 20 \
    --batch_size 32 \
    --device cuda \
    --output ./trained_model
```

### 训练参数建议

| 知识量 | epochs | batch_size | 预计时间 |
|--------|--------|------------|----------|
| 1万条 | 5 | 16 | 1小时 |
| 10万条 | 10 | 32 | 5小时 |
| 50万条 | 15 | 64 | 1天 |
| 100万条 | 20 | 64 | 2-3天 |

---

## 小说生成

### 训练完成后

```bash
# 生成小说
python novel_generator.py \
    --model ./trained_model \
    --prompt "在一个风雨交加的夜晚" \
    --length 2000 \
    --output novel.txt

# 交互模式
python novel_generator.py --model ./trained_model --interactive
```

### 创造性调节

```bash
# 保守（更连贯）
--temperature 0.5

# 平衡
--temperature 0.8

# 创意（更随机）
--temperature 1.2
```

---

## 常见问题

### Q: 现在能写小说吗？

A: 当前版本是检索模式，会搜索相关知识返回，不是真正的创作。需要训练后才能生成小说。

### Q: 多少知识才能训练？

A: 建议10万条以上。越多越好。

### Q: 训练要多少钱？

A: 
- AutoDL: ~1元/小时
- 火山引擎: ~2元/小时
- 阿里云: ~3元/小时

10万条知识训练约需5-10小时，成本约10-30元。

### Q: 训练后模型多大？

A: 
- 小模型(256维): ~50MB
- 中模型(512维): ~200MB
- 大模型(768维): ~500MB

### Q: 能在手机上跑吗？

A: 小模型可以在手机上跑，但建议用服务器。

---

## 时间线

```
现在
  │
  ├── 部署黑洞 → 开始爬知识
  │
  ├─ 1个月后
  │     │
  │     └── 知识库 ~10万条
  │
  ├─ 3个月后
  │     │
  │     └── 知识库 ~50万条
  │           │
  │           └── 租GPU训练
  │                 │
  │                 └── 得到真模型
  │                       │
  │                       └── 可以写小说了！
  │
  └─ 6个月后
        │
        └── 知识库 ~100万条
              │
              └── 继续训练，越来越强
```

---

**记住：先养胖，再训练！**
