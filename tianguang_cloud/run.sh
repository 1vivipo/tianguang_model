#!/bin/bash
# 天光AI - 快速启动脚本

echo "================================"
echo "天光AI - 云端训练版"
echo "================================"

# 检查Python
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python"
    exit 1
fi

# 检查PyTorch
python -c "import torch; print(f'PyTorch版本: {torch.__version__}')" 2>/dev/null || {
    echo "安装PyTorch..."
    pip install torch numpy
}

# 检查数据
if [ ! -f "data/training_data.txt" ]; then
    echo "错误: 未找到训练数据 data/training_data.txt"
    echo "请先准备训练数据"
    exit 1
fi

# 显示配置
echo ""
echo "训练配置:"
echo "  - 模型: 中等规模 (约10M参数)"
echo "  - 数据: data/training_data.txt"
echo "  - 输出: models/tianguang_model"
echo ""

# 开始训练
echo "开始训练..."
python scripts/train.py --config medium

echo ""
echo "================================"
echo "训练完成！"
echo "模型保存在: models/tianguang_model"
echo ""
echo "测试模型:"
echo "  python scripts/inference.py --interactive"
echo ""
echo "启动API服务:"
echo "  python scripts/serve.py"
echo "================================"
