#!/bin/bash

# 部署验证脚本
# 在服务器上运行此脚本来验证部署是否成功

echo "=== 分子气味预测API - 部署验证 ==="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# 检查基本环境
echo ""
echo "🔍 检查基本环境..."

# Python版本
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    success "Python: $PYTHON_VERSION"
else
    error "Python3 未找到"
    exit 1
fi

# 检查内存
MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
if [ "$MEMORY_GB" -ge 8 ]; then
    success "内存: ${MEMORY_GB}GB (充足)"
elif [ "$MEMORY_GB" -ge 4 ]; then
    warning "内存: ${MEMORY_GB}GB (可能不足，建议8GB+)"
else
    error "内存: ${MEMORY_GB}GB (不足，需要至少4GB)"
fi

# 检查CPU核心数
CPU_CORES=$(nproc)
success "CPU核心数: $CPU_CORES"

# 检查文件完整性
echo ""
echo "📂 检查文件完整性..."

required_files=(
    "predict_odor_cpu.py"
    "server_deploy.py"
    "test_api_client.py"
    "requirements_server.txt"
    "DEPLOY_README.md"
    "start_server.sh"
    "start_production.sh"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        success "$file"
    else
        error "$file 缺失"
        exit 1
    fi
done

if [ -d "openpom" ]; then
    success "openpom/ 目录存在"
else
    error "openpom/ 目录缺失"
    exit 1
fi

# 检查模型文件
echo ""
echo "🤖 检查模型文件..."

if [ -d "ensemble_models" ]; then
    model_count=$(find ensemble_models -name "checkpoint2.pt" 2>/dev/null | wc -l)
    if [ "$model_count" -gt 0 ]; then
        success "找到 $model_count 个模型文件"
    else
        warning "模型文件夹存在但没有找到 .pt 文件"
        echo "   请确保模型文件结构如下:"
        echo "   ensemble_models/experiments_1/checkpoint2.pt"
        echo "   ensemble_models/experiments_2/checkpoint2.pt"
        echo "   ..."
    fi
else
    warning "ensemble_models/ 目录不存在"
    echo "   需要创建此目录并放入训练好的模型文件"
fi

# 检查Python依赖
echo ""
echo "📦 检查Python依赖..."

if python3 -c "import torch" 2>/dev/null; then
    TORCH_VERSION=$(python3 -c "import torch; print(torch.__version__)")
    success "PyTorch: $TORCH_VERSION"
else
    error "PyTorch 未安装"
    echo "   运行: pip install torch --index-url https://download.pytorch.org/whl/cpu"
fi

if python3 -c "import deepchem" 2>/dev/null; then
    success "DeepChem 已安装"
else
    error "DeepChem 未安装"
    echo "   运行: pip install deepchem"
fi

if python3 -c "import flask" 2>/dev/null; then
    success "Flask 已安装"
else
    error "Flask 未安装"
    echo "   运行: pip install flask"
fi

# 检查端口
echo ""
echo "🌐 检查网络端口..."

PORT=${PORT:-5000}
if command -v netstat &> /dev/null; then
    if netstat -tuln | grep ":$PORT " > /dev/null; then
        warning "端口 $PORT 已被占用"
        echo "   可以设置其他端口: export PORT=8080"
    else
        success "端口 $PORT 可用"
    fi
else
    warning "无法检查端口状态 (netstat未找到)"
fi

# 快速功能测试
echo ""
echo "⚡ 快速功能测试..."

if [ -d "ensemble_models" ] && [ "$model_count" -gt 0 ]; then
    echo "   正在进行快速预测测试..."
    
    # 设置环境变量避免GPU
    export CUDA_VISIBLE_DEVICES=""
    
    # 运行快速测试
    timeout 60 python3 -c "
from predict_odor_cpu import OdorPredictorCPU
try:
    predictor = OdorPredictorCPU(n_models=1)  # 只加载1个模型进行快速测试
    result = predictor.get_top_odors('CCO', top_k=3)
    print('测试预测结果:')
    for _, row in result.iterrows():
        print(f'  {row[\"odor\"]}: {row[\"probability\"]:.3f}')
    print('✓ 预测功能正常')
except Exception as e:
    print(f'❌ 预测测试失败: {e}')
    exit(1)
" 2>&1
    
    if [ $? -eq 0 ]; then
        success "预测功能测试通过"
    else
        error "预测功能测试失败"
        echo "   请检查模型文件和依赖包"
    fi
else
    warning "跳过功能测试 (缺少模型文件)"
fi

# 总结
echo ""
echo "📋 验证总结:"
echo "   Python: $(python3 --version)"
echo "   内存: ${MEMORY_GB}GB"
echo "   CPU核心: $CPU_CORES"
echo "   模型文件: $model_count 个"

echo ""
echo "🚀 后续步骤:"
if [ ! -d "ensemble_models" ] || [ "$model_count" -eq 0 ]; then
    echo "1. 复制模型文件到 ensemble_models/ 目录"
fi

missing_deps=0
for dep in torch deepchem flask; do
    if ! python3 -c "import $dep" 2>/dev/null; then
        if [ $missing_deps -eq 0 ]; then
            echo "$((missing_deps + 2)). 安装缺失的依赖: pip install -r requirements_server.txt"
        fi
        missing_deps=$((missing_deps + 1))
    fi
done

next_step=$((2 + (missing_deps > 0 ? 1 : 0) + ([ ! -d "ensemble_models" ] || [ "$model_count" -eq 0 ] ? 1 : 0)))
echo "$next_step. 启动服务: ./start_server.sh"
echo "$((next_step + 1)). 测试API: python3 test_api_client.py"

echo ""
if [ -d "ensemble_models" ] && [ "$model_count" -gt 0 ] && python3 -c "import torch, deepchem, flask" 2>/dev/null; then
    success "🎉 部署环境验证通过！可以启动服务了。"
else
    warning "⚠️  部署环境需要完善，请按照上述步骤操作。"
fi 