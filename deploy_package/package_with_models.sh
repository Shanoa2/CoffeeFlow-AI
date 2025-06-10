#!/bin/bash

# 分子气味预测API部署包打包脚本 (包含模型文件)

echo "=== 创建完整部署包 (包含模型) ==="

# 包名和版本
PACKAGE_NAME="odor-prediction-api-full-deploy"
VERSION=$(date +%Y%m%d_%H%M%S)
PACKAGE_FILE="${PACKAGE_NAME}_${VERSION}.tar.gz"

echo "📦 打包信息:"
echo "   包名: $PACKAGE_NAME"
echo "   版本: $VERSION"
echo "   文件: $PACKAGE_FILE"

# 检查必要文件
required_files=(
    "predict_odor_cpu.py"
    "server_deploy.py"
    "test_api_client.py"
    "requirements_server.txt"
    "DEPLOY_README.md"
    "start_server.sh"
    "start_production.sh"
    "Dockerfile"
    "config.env"
    "verify_deployment.sh"
    "QUICK_DEPLOY.md"
)

echo ""
echo "🔍 检查文件:"
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ❌ $file (缺失)"
        exit 1
    fi
done

if [ -d "openpom" ]; then
    echo "   ✓ openpom/ (目录)"
else
    echo "   ❌ openpom/ (缺失)"
    exit 1
fi

# 检查模型文件
echo ""
echo "🤖 检查模型文件..."

# 检查当前目录的模型文件
if [ -d "ensemble_models" ]; then
    model_count=$(find ensemble_models -name "checkpoint2.pt" 2>/dev/null | wc -l)
    if [ "$model_count" -gt 0 ]; then
        echo "   ✓ 在当前目录找到 $model_count 个模型文件"
        MODELS_DIR="ensemble_models"
        INCLUDE_MODELS=true
    else
        echo "   ❌ 模型目录存在但没有找到 checkpoint2.pt 文件"
        INCLUDE_MODELS=false
    fi
# 检查上级目录的模型文件
elif [ -d "../ensemble_models" ]; then
    model_count=$(find ../ensemble_models -name "checkpoint2.pt" 2>/dev/null | wc -l)
    if [ "$model_count" -gt 0 ]; then
        echo "   ✓ 在上级目录找到 $model_count 个模型文件"
        MODELS_DIR="../ensemble_models"
        INCLUDE_MODELS=true
    else
        echo "   ❌ 模型目录存在但没有找到 checkpoint2.pt 文件"
        echo "   请确保有训练好的模型文件"
        INCLUDE_MODELS=false
    fi
else
    echo "   ❌ 没有找到 ensemble_models 目录"
    echo "   需要提供训练好的模型文件"
    INCLUDE_MODELS=false
fi

if [ "$INCLUDE_MODELS" = false ]; then
    echo ""
    echo "⚠️  警告: 没有找到模型文件"
    echo "   这将创建一个轻量版部署包（不包含模型）"
    echo "   如果要包含模型，请确保以下之一:"
    echo "   1. 当前目录有 ensemble_models/ 文件夹"
    echo "   2. 上级目录有 ensemble_models/ 文件夹"
    echo ""
    read -p "是否继续创建轻量版包？(y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "取消打包"
        exit 1
    fi
fi

# 复制模型文件到当前目录
if [ "$INCLUDE_MODELS" = true ] && [ "$MODELS_DIR" = "../ensemble_models" ]; then
    echo ""
    echo "📁 复制模型文件..."
    cp -r ../ensemble_models ./ensemble_models_temp
    MODELS_DIR="ensemble_models_temp"
    CLEANUP_MODELS=true
else
    CLEANUP_MODELS=false
fi

# 创建打包清单
echo ""
echo "📝 创建打包清单..."

if [ "$INCLUDE_MODELS" = true ]; then
    model_size=$(du -sh $MODELS_DIR 2>/dev/null | cut -f1)
    total_model_files=$(find $MODELS_DIR -name "checkpoint2.pt" 2>/dev/null | wc -l)
else
    model_size="0"
    total_model_files="0"
fi

cat > PACKAGE_MANIFEST.txt << EOF
分子气味预测API完整部署包
============================

打包时间: $(date)
版本: $VERSION
包类型: $([ "$INCLUDE_MODELS" = true ] && echo "完整包 (含模型)" || echo "轻量包 (不含模型)")

包含文件:
$(ls -la)

模型文件:
- 模型数量: $total_model_files 个
- 模型大小: $model_size
- 模型位置: $([ "$INCLUDE_MODELS" = true ] && echo "ensemble_models/" || echo "需要手动添加")

文件统计:
- Python文件: $(find . -name "*.py" | wc -l)
- 脚本文件: $(find . -name "*.sh" | wc -l)
- 配置文件: $(find . -name "*.txt" -o -name "*.env" -o -name "Dockerfile" | wc -l)
- 文档文件: $(find . -name "*.md" | wc -l)

安装说明:
1. 解压文件: tar -xzf $PACKAGE_FILE
2. 进入目录: cd deploy_package
3. 验证环境: ./verify_deployment.sh
4. 安装依赖: pip install -r requirements_server.txt
$([ "$INCLUDE_MODELS" = true ] || echo "5. 复制模型文件到 ensemble_models/ 目录")
$(([ "$INCLUDE_MODELS" = true ] && echo "5") || echo "6"). 启动服务: ./start_server.sh

技术支持:
- 详细文档: README_server_deployment.md
- 快速指南: QUICK_DEPLOY.md
- 部署验证: verify_deployment.sh
EOF

echo "✓ 打包清单已创建"

# 清理临时文件
echo ""
echo "🧹 清理临时文件..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.log" -delete
find . -name "temp_predict*.csv" -delete

# 创建tar包
echo ""
echo "📦 创建压缩包..."
cd ..

if [ "$INCLUDE_MODELS" = true ]; then
    echo "   包含模型文件，打包可能需要较长时间..."
    tar -czf "$PACKAGE_FILE" \
        --exclude="*.git*" \
        --exclude="*.pytest_cache*" \
        --exclude="*/__pycache__/*" \
        --exclude="*.pyc" \
        --exclude="*.log" \
        deploy_package/
else
    tar -czf "$PACKAGE_FILE" \
        --exclude="*.git*" \
        --exclude="*.pytest_cache*" \
        --exclude="*/__pycache__/*" \
        --exclude="*.pyc" \
        --exclude="*.log" \
        --exclude="deploy_package/ensemble_models*" \
        deploy_package/
fi

# 清理临时模型文件
if [ "$CLEANUP_MODELS" = true ]; then
    echo "🧹 清理临时模型文件..."
    rm -rf deploy_package/ensemble_models_temp
fi

if [ $? -eq 0 ]; then
    echo "✅ 打包成功!"
    echo ""
    echo "📦 部署包信息:"
    echo "   文件名: $PACKAGE_FILE"
    echo "   大小: $(du -h "$PACKAGE_FILE" | cut -f1)"
    echo "   位置: $(pwd)/$PACKAGE_FILE"
    echo "   类型: $([ "$INCLUDE_MODELS" = true ] && echo "完整包 (包含 $total_model_files 个模型)" || echo "轻量包 (需要手动添加模型)")"
    
    echo ""
    echo "🚀 部署步骤:"
    echo "1. 将 $PACKAGE_FILE 上传到服务器"
    echo "2. 解压: tar -xzf $PACKAGE_FILE"
    echo "3. 进入目录: cd deploy_package"
    echo "4. 验证环境: ./verify_deployment.sh"
    if [ "$INCLUDE_MODELS" = false ]; then
        echo "5. 复制模型文件到 ensemble_models/ 目录"
        echo "6. 启动服务: ./start_server.sh"
    else
        echo "5. 启动服务: ./start_server.sh"
    fi
else
    echo "❌ 打包失败!"
    exit 1
fi 