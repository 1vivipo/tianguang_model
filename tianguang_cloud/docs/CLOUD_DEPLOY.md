# 天光AI - 云端部署指南

## 方案一：阿里云PAI-DSW（推荐）

### 步骤1：创建实例

1. 登录阿里云控制台：https://pai.console.aliyun.com/
2. 进入"模型开发" -> "交互式建模(DSW)"
3. 点击"创建实例"
4. 选择配置：
   - 实例名称：tianguang-ai
   - 资源规格：GPU类型（推荐 T4 或 V100）
   - 镜像：PyTorch 2.0
   - 数据盘：勾选（数据会保留）

**免费额度：** 新用户有免费试用额度

### 步骤2：上传代码

方式一：使用Git
```bash
cd /mnt/workspace
git clone https://github.com/你的用户名/tianguang_cloud.git
cd tianguang_cloud
```

方式二：直接上传
- 使用DSW的Jupyter界面
- 上传整个项目文件夹

### 步骤3：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤4：准备数据

将训练数据放到 `data/training_data.txt`

### 步骤5：开始训练

```bash
# 小模型快速测试（约30分钟）
python scripts/train.py --config small --steps 5000

# 中等模型（推荐，约2小时）
python scripts/train.py --config medium --steps 20000

# 大模型（需要更多时间）
python scripts/train.py --config large --steps 50000
```

### 步骤6：下载模型

训练完成后，下载 `models/tianguang_model` 文件夹

---

## 方案二：Google Colab（完全免费）

### 步骤1：打开Colab

访问：https://colab.research.google.com/

### 步骤2：启用GPU

运行时 -> 更改运行时类型 -> GPU

### 步骤3：运行代码

新建Notebook，运行以下代码：

```python
# 1. 克隆代码
!git clone https://github.com/你的用户名/tianguang_cloud.git
%cd tianguang_cloud

# 2. 安装依赖
!pip install torch numpy tqdm

# 3. 开始训练
!python scripts/train.py --config small --steps 5000

# 4. 测试模型
!python scripts/inference.py --prompt "人工智能"

# 5. 下载模型
from google.colab import files
!zip -r model.zip models/tianguang_model
files.download('model.zip')
```

---

## 方案三：AutoDL（最便宜）

### 步骤1：租用GPU

访问：https://www.autodl.com/
- 选择GPU类型（RTX 3090 约1.7元/小时）
- 选择PyTorch镜像

### 步骤2：连接实例

使用SSH或Jupyter连接

### 步骤3：运行训练

```bash
cd /root
git clone https://github.com/你的用户名/tianguang_cloud.git
cd tianguang_cloud
pip install -r requirements.txt
python scripts/train.py --config medium
```

---

## 训练时间估计

| 配置 | 参数量 | GPU | 时间 |
|------|--------|-----|------|
| Small | ~2M | T4 | 30分钟 |
| Medium | ~10M | T4 | 2小时 |
| Large | ~50M | V100 | 4小时 |

---

## 成本估算

| 平台 | GPU | 价格 | 训练时间 | 总成本 |
|------|-----|------|----------|--------|
| 阿里云PAI | T4 | ~2元/小时 | 2小时 | ~4元 |
| Google Colab | T4 | 免费 | 2小时 | 0元 |
| AutoDL | 3090 | ~1.7元/小时 | 1.5小时 | ~2.5元 |

**推荐：** 用Google Colab完全免费！

---

## 训练完成后

### 1. 测试模型

```bash
python scripts/inference.py --interactive
```

### 2. 启动API服务

```bash
python scripts/serve.py --port 8000
```

### 3. 导出ONNX

```bash
python scripts/export.py --format onnx
```
