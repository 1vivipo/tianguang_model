# 天光AI - 云端训练版

一个可以在阿里云/腾讯云免费GPU上训练的语言模型。

## 快速开始

### 1. 创建云端实例

**阿里云PAI-DSW（推荐，有免费额度）：**
1. 访问 https://pai.console.aliyun.com/
2. 创建DSW实例，选择GPU类型
3. 选择 PyTorch 镜像

**腾讯云TI-ONE：**
1. 访问 https://console.cloud.tencent.com/tione
2. 创建 Notebook 实例
3. 选择 GPU 类型

### 2. 上传代码

将本项目上传到云端实例

### 3. 运行训练

```bash
cd tianguang_cloud
python scripts/train.py
```

### 4. 下载模型

训练完成后，模型保存在 `models/` 目录

## 项目结构

```
tianguang_cloud/
├── data/
│   └── training_data.txt    # 训练数据
├── models/
│   └── tianguang_model/     # 训练后的模型
├── scripts/
│   ├── train.py             # 训练脚本
│   ├── inference.py         # 推理脚本
│   └── export.py            # 导出脚本
├── config.py                # 配置文件
├── model.py                 # 模型定义
├── tokenizer.py             # 分词器
└── README.md                # 说明文档
```

## 模型规格

- 参数量：约 10M - 100M（可配置）
- 架构：Transformer / GPT-2 风格
- 词表大小：约 5000-10000
- 训练数据：约 3MB+

## 使用训练好的模型

```python
from model import TianguangModel
from tokenizer import TianguangTokenizer

# 加载模型
model = TianguangModel.from_pretrained('models/tianguang_model')
tokenizer = TianguangTokenizer.from_pretrained('models/tianguang_model')

# 生成文本
input_text = "人工智能"
output = model.generate(input_text, max_length=50)
print(output)
```

## 导出为ONNX格式

```bash
python scripts/export.py --format onnx
```

## 部署为API服务

```bash
pip install fastapi uvicorn
python scripts/serve.py
```

## 许可证

MIT License
