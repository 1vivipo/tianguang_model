# 元脑MetaBrain V3.1 API

🧠 **自己的AI，无限知识，完全免费**

## ✨ 特点

- ✅ **100%自研** - 不依赖任何第三方大模型
- ✅ **联网搜索** - 自动搜索获取实时知识
- ✅ **标准API** - 兼容OpenAI接口格式
- ✅ **完全免费** - 无任何费用
- ✅ **一键部署** - 支持Railway/Render/Fly.io

## 🚀 快速部署

### Railway（推荐）

1. 访问 https://railway.app
2. 用GitHub登录
3. 选择此仓库
4. 设置 Root Directory 为 `metabrain_api`
5. 部署完成！

### Render

1. 访问 https://render.com
2. 创建 Web Service
3. 连接此仓库
4. 设置 Build Command: `pip install -r requirements.txt`
5. 设置 Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

## 📡 API调用

### OpenAI风格

```bash
curl -X POST https://你的域名/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer sk-tianguang-2024-metabrain-v31" \
     -d '{"model": "metabrain-v3.1", "messages": [{"role": "user", "content": "你好"}]}'
```

### 简化风格

```bash
curl -X POST https://你的域名/api/chat \
     -H "Content-Type: application/json" \
     -H "X-API-KEY: sk-tianguang-2024-metabrain-v31" \
     -d '{"query": "你好"}'
```

### Python

```python
import requests

response = requests.post(
    "https://你的域名/api/chat",
    headers={"X-API-KEY": "sk-tianguang-2024-metabrain-v31"},
    json={"query": "你好"}
)
print(response.json()["answer"])
```

## 📋 API配置

| 配置项 | 值 |
|--------|-----|
| API Key | `sk-tianguang-2024-metabrain-v31` |
| API Secret | `tianguang-secret-key-2024` |
| Model | `metabrain-v3.1` |

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `app.py` | 云端版主程序（精简版，推荐） |
| `api_server.py` | 完整版API服务 |
| `metabrain_final.py` | 元脑核心代码 |
| `metabrain_client.py` | Python客户端SDK |
| `requirements.txt` | Python依赖 |
| `Procfile` | 启动命令 |
| `Dockerfile` | Docker配置 |

## 🔧 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python app.py
```

## 📝 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| API_KEY | sk-tianguang-2024-metabrain-v31 | API密钥 |
| API_SECRET | tianguang-secret-key-2024 | API密钥 |
| MODEL_NAME | metabrain-v3.1 | 模型名称 |
| PORT | 8080 | 端口 |

---

**天光AI - 自己的AI，无限知识！**
