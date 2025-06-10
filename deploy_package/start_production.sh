#!/bin/bash

# 生产环境启动脚本 (使用Gunicorn)

echo "=== 分子气味预测API - 生产环境启动 ==="

# 检查Gunicorn
if ! command -v gunicorn &> /dev/null; then
    echo "📦 安装Gunicorn..."
    pip install gunicorn
fi

# 检查模型文件
if [ ! -d "ensemble_models" ]; then
    echo "❌ 错误: 未找到模型文件夹 'ensemble_models'"
    exit 1
fi

# 配置参数
WORKERS=${WORKERS:-2}  # 工作进程数 (建议CPU核心数的50%)
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-"5000"}
TIMEOUT=${TIMEOUT:-300}  # 超时时间(秒)

# CPU优化
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-"4"}
export MKL_NUM_THREADS=${MKL_NUM_THREADS:-"4"}

echo "🚀 生产环境配置:"
echo "   工作进程数: $WORKERS"
echo "   绑定地址: $HOST:$PORT"
echo "   超时时间: $TIMEOUT 秒"
echo "   CPU线程数: $OMP_NUM_THREADS"

# 启动Gunicorn
exec gunicorn \
    --workers $WORKERS \
    --bind $HOST:$PORT \
    --timeout $TIMEOUT \
    --worker-class sync \
    --access-logfile access.log \
    --error-logfile error.log \
    --log-level info \
    --preload \
    server_deploy:app 