# 分子气味预测API - Docker镜像

FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装Python包
COPY requirements_server.txt .
RUN pip install --no-cache-dir -r requirements_server.txt

# 复制应用代码
COPY . .

# 设置权限
RUN chmod +x start_server.sh start_production.sh

# 环境变量
ENV HOST=0.0.0.0
ENV PORT=5000
ENV OMP_NUM_THREADS=4
ENV MKL_NUM_THREADS=4

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 启动命令
CMD ["python3", "server_deploy.py"] 