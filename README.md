# 天光AI - 完整项目

一个可以在浏览器端和云端训练的语言模型项目。

## 项目包含

### 1. 浏览器端版本 (`/`)

在浏览器中直接训练和使用模型。

**使用方法：**
1. 打开网站：https://1vivipo.github.io/tianguang_model/
2. 加载数据 → 开始训练
3. 训练完成后可以对话测试

**特点：**
- 无需服务器，浏览器端训练
- 支持GPU加速
- 可导出模型

### 2. 云端训练版本 (`/tianguang_cloud`)

在阿里云/腾讯云/Colab上训练更强大的模型。

**使用方法：**
1. 上传代码到云端
2. 运行 `python scripts/train.py`
3. 下载训练好的模型

**特点：**
- 支持GPU训练
- 可训练更大模型
- 可导出ONNX格式
- 可部署为API服务

## 快速开始

### 方案一：浏览器端（最简单）

直接访问网站使用，无需任何配置。

### 方案二：Google Colab（免费GPU）

1. 打开 `tianguang_colab.ipynb`
2. 上传到 Google Colab
3. 启用GPU运行

### 方案三：阿里云PAI（推荐）

1. 创建PAI-DSW实例
2. 上传代码
3. 运行训练

## 训练数据

项目包含约 **440KB** 的训练数据，涵盖：

- AI与机器学习知识
- 编程与技术知识
- 科学知识百科
- 历史文化知识
- 生活常识百科
- 商业经济知识
- 汉语词典解释
- 英汉词典翻译
- 诗词名句
- 成语词典
- 名言警句
- 更多...

## 模型规格

| 配置 | 参数量 | 训练时间 | 推荐用途 |
|------|--------|----------|----------|
| Small | ~2M | 30分钟 | 快速测试 |
| Medium | ~10M | 2小时 | 日常使用 |
| Large | ~50M | 4小时 | 更好效果 |

## 部署方式

训练完成后，可以：

1. **本地运行**：使用Python脚本
2. **API服务**：启动FastAPI服务
3. **ONNX部署**：导出为ONNX格式
4. **移动端**：转换为移动端格式

## 文件结构

```
tianguang_model/
├── index.html              # 浏览器端主页
├── js/                     # 浏览器端代码
│   ├── training_data.js    # 训练数据
│   ├── trainer.js          # 训练器
│   └── app.js              # 应用逻辑
├── css/                    # 样式文件
├── python/                 # Python工具
├── tianguang_cloud/        # 云端训练版本
│   ├── model.py            # 模型定义
│   ├── tokenizer.py        # 分词器
│   ├── config.py           # 配置
│   ├── scripts/            # 脚本
│   │   ├── train.py        # 训练脚本
│   │   ├── inference.py    # 推理脚本
│   │   ├── export.py       # 导出脚本
│   │   └── serve.py        # API服务
│   └── data/               # 训练数据
└── docs/                   # 文档
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
