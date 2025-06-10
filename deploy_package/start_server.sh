#!/bin/bash

# 分子气味预测API服务器启动脚本

echo "=== 分子气味预测API服务器启动脚本 ==="

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3，请先安装Python 3.8+"
    exit 1
fi

echo "✓ Python版本: $(python3 --version)"

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  警告: 建议在虚拟环境中运行"
    echo "   可以运行: python3 -m venv venv && source venv/bin/activate"
fi

# 检查依赖
echo "📦 检查依赖包..."
if ! python3 -c "import torch, deepchem, flask" 2>/dev/null; then
    echo "❌ 缺少依赖包，正在安装..."
    pip install -r requirements_server.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败，请手动安装: pip install -r requirements_server.txt"
        exit 1
    fi
fi

# 检查模型文件
if [ ! -d "ensemble_models" ]; then
    echo "❌ 错误: 未找到模型文件夹 'ensemble_models'"
    echo "   请确保模型文件按以下结构放置:"
    echo "   ensemble_models/"
    echo "   ├── experiments_1/checkpoint2.pt"
    echo "   ├── experiments_2/checkpoint2.pt"
    echo "   └── ..."
    exit 1
fi

model_count=$(find ensemble_models -name "checkpoint2.pt" | wc -l)
echo "✓ 找到 $model_count 个模型文件"

# 设置环境变量
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"5000"}
export DEBUG=${DEBUG:-"False"}

# CPU优化设置
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-"4"}
export MKL_NUM_THREADS=${MKL_NUM_THREADS:-"4"}

echo "🚀 启动配置:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Debug: $DEBUG"
echo "   CPU线程数: $OMP_NUM_THREADS"

# 启动服务器
echo "✓ 启动服务器..."
python3 server_deploy.py 