#!/bin/bash

# 分子气味预测API部署包打包脚本

echo "=== 创建部署包 ==="

# 包名和版本
PACKAGE_NAME="odor-prediction-api-deploy"
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

# 创建打包清单
echo ""
echo "📝 创建打包清单..."
cat > PACKAGE_MANIFEST.txt << EOF
分子气味预测API部署包
=====================

打包时间: $(date)
版本: $VERSION

包含文件:
$(ls -la)

文件统计:
- Python文件: $(find . -name "*.py" | wc -l)
- 脚本文件: $(find . -name "*.sh" | wc -l)
- 配置文件: $(find . -name "*.txt" -o -name "*.env" -o -name "Dockerfile" | wc -l)
- 文档文件: $(find . -name "*.md" | wc -l)

安装说明:
1. 解压文件: tar -xzf $PACKAGE_FILE
2. 阅读文档: cat DEPLOY_README.md
3. 准备模型: 将模型文件放入 ensemble_models/ 目录
4. 安装依赖: pip install -r requirements_server.txt
5. 启动服务: ./start_server.sh

技术支持:
- 详细文档: README_server_deployment.md
- 快速指南: DEPLOY_README.md
EOF

echo "✓ 打包清单已创建"

# 清理临时文件
echo ""
echo "🧹 清理临时文件..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.log" -delete
find . -name "temp_predict*.csv" -delete

# 创建tar包
echo ""
echo "📦 创建压缩包..."
cd ..
tar -czf "$PACKAGE_FILE" \
    --exclude="*.git*" \
    --exclude="*.pytest_cache*" \
    --exclude="*/__pycache__/*" \
    --exclude="*.pyc" \
    --exclude="*.log" \
    deploy_package/

if [ $? -eq 0 ]; then
    echo "✅ 打包成功!"
    echo ""
    echo "📦 部署包信息:"
    echo "   文件名: $PACKAGE_FILE"
    echo "   大小: $(du -h "$PACKAGE_FILE" | cut -f1)"
    echo "   位置: $(pwd)/$PACKAGE_FILE"
    
    echo ""
    echo "🚀 部署步骤:"
    echo "1. 将 $PACKAGE_FILE 上传到服务器"
    echo "2. 解压: tar -xzf $PACKAGE_FILE"
    echo "3. 进入目录: cd deploy_package"
    echo "4. 阅读说明: cat DEPLOY_README.md"
    echo "5. 复制模型文件到 ensemble_models/ 目录"
    echo "6. 启动服务: ./start_server.sh"
else
    echo "❌ 打包失败!"
    exit 1
fi 