# 分子气味预测模型 - 服务器部署指南

## 概述

本指南帮助您将训练好的分子气味预测模型部署到**仅CPU**的服务器环境中，提供HTTP API服务。

## 特性

✅ **CPU专用**: 强制使用CPU推理，无需GPU  
✅ **内存优化**: 针对CPU环境优化内存使用  
✅ **REST API**: 提供标准HTTP接口  
✅ **批量预测**: 支持单个和批量分子预测  
✅ **健康检查**: 提供服务器状态监控接口  
✅ **错误处理**: 完善的错误处理和日志记录  

## 系统要求

### 硬件要求
- **CPU**: 至少4核心（推荐8核心以上）
- **内存**: 最少8GB RAM（推荐16GB以上）
- **存储**: 至少2GB可用空间用于模型文件

### 软件要求
- **操作系统**: Linux, macOS, 或 Windows
- **Python**: 3.8 或以上版本
- **网络**: 可访问的网络端口（默认5000）

## 安装步骤

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv_server
source venv_server/bin/activate  # Linux/macOS
# 或者 venv_server\Scripts\activate  # Windows

# 升级pip
pip install --upgrade pip
```

### 2. 安装依赖

```bash
# 安装服务器版本依赖
pip install -r examples/requirements_server.txt

# 或者手动安装核心依赖
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install deepchem dgl dgllife flask requests psutil pandas numpy scikit-learn
```

### 3. 模型文件准备

确保您的模型文件按以下结构组织：

```
your_project/
├── ensemble_models/
│   ├── experiments_1/
│   │   └── checkpoint2.pt
│   ├── experiments_2/
│   │   └── checkpoint2.pt
│   ├── ...
│   └── experiments_10/
│       └── checkpoint2.pt
├── examples/
│   ├── predict_odor_cpu.py
│   ├── server_deploy.py
│   └── test_api_client.py
└── openpom/  # 您的OpenPOM模块
```

## 部署方式

### 方式1: 开发测试环境

```bash
# 启动开发服务器
cd examples
python server_deploy.py

# 服务器将在 http://localhost:5000 启动
```

### 方式2: 生产环境 (推荐)

```bash
# 安装生产级WSGI服务器
pip install gunicorn

# 启动生产服务器
cd examples
gunicorn -w 4 -b 0.0.0.0:5000 server_deploy:app

# 参数说明:
# -w 4: 4个工作进程
# -b 0.0.0.0:5000: 绑定到所有网络接口的5000端口
```

### 方式3: Docker部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements_server.txt .
RUN pip install -r requirements_server.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "server_deploy.py"]
```

构建和运行Docker容器：

```bash
# 构建镜像
docker build -t odor-prediction-api .

# 运行容器
docker run -p 5000:5000 -v /path/to/models:/app/ensemble_models odor-prediction-api
```

## API接口文档

### 1. 健康检查
```http
GET /
```

**响应示例**:
```json
{
    "status": "healthy",
    "service": "Odor Prediction API",
    "version": "1.0.0",
    "cpu_only": true,
    "platform": "Linux",
    "cpu_count": 8,
    "memory_total_gb": 16.0,
    "models_loaded": 10
}
```

### 2. 单分子预测
```http
POST /predict
Content-Type: application/json

{
    "smiles": "CCO",
    "top_k": 5
}
```

**响应示例**:
```json
{
    "smiles": "CCO",
    "top_odors": [
        {"odor": "alcoholic", "probability": 0.892},
        {"odor": "sweet", "probability": 0.756},
        {"odor": "ethereal", "probability": 0.643},
        {"odor": "fruity", "probability": 0.521},
        {"odor": "fresh", "probability": 0.489}
    ],
    "prediction_time_seconds": 1.234
}
```

### 3. 批量预测
```http
POST /predict_batch
Content-Type: application/json

{
    "smiles_list": ["CCO", "CC(=O)OCC", "c1ccc(cc1)O"],
    "threshold": 0.5
}
```

**响应示例**:
```json
{
    "molecule_count": 3,
    "threshold": 0.5,
    "predictions": [...],  // 详细概率预测
    "binary_predictions": [...],  // 二进制预测结果
    "prediction_time_seconds": 2.876
}
```

### 4. 获取气味任务
```http
GET /tasks
```

**响应示例**:
```json
{
    "tasks": ["alcoholic", "aldehydic", "alliaceous", ...],
    "task_count": 138
}
```

## 测试部署

### 使用提供的测试脚本

```bash
# 基本功能测试
python test_api_client.py

# 性能测试
python test_api_client.py --perf-test --num-requests 20

# 测试远程服务器
python test_api_client.py --url http://your-server:5000
```

### 使用curl命令测试

```bash
# 健康检查
curl http://localhost:5000/

# 单分子预测
curl -X POST http://localhost:5000/predict \
     -H "Content-Type: application/json" \
     -d '{"smiles": "CCO", "top_k": 5}'

# 批量预测
curl -X POST http://localhost:5000/predict_batch \
     -H "Content-Type: application/json" \
     -d '{"smiles_list": ["CCO", "CC(=O)OCC"], "threshold": 0.5}'
```

## 性能优化建议

### 1. CPU优化
```bash
# 设置OpenMP线程数（根据CPU核心数调整）
export OMP_NUM_THREADS=4

# 设置MKL线程数
export MKL_NUM_THREADS=4
```

### 2. 内存优化
- 减少集成模型数量（修改`n_models`参数）
- 使用较小的batch_size
- 定期重启服务以释放内存

### 3. 并发设置
```bash
# Gunicorn配置示例
gunicorn -w 2 -k sync --timeout 300 -b 0.0.0.0:5000 server_deploy:app

# 参数说明:
# -w 2: 2个工作进程（建议CPU核心数的50%）
# -k sync: 同步工作模式
# --timeout 300: 超时时间5分钟
```

## 监控和日志

### 查看日志
```bash
# 启动时启用详细日志
python server_deploy.py 2>&1 | tee server.log

# Gunicorn日志
gunicorn --access-logfile access.log --error-logfile error.log server_deploy:app
```

### 监控指标
- 响应时间
- 内存使用率
- CPU使用率
- 错误率

## 故障排除

### 常见问题

1. **模型加载失败**
   ```
   解决方案: 检查模型文件路径和权限
   ```

2. **内存不足**
   ```
   解决方案: 
   - 增加服务器内存
   - 减少集成模型数量
   - 使用更小的batch_size
   ```

3. **预测速度慢**
   ```
   解决方案:
   - 检查CPU核心数设置
   - 优化OpenMP线程数
   - 考虑使用更强的CPU
   ```

4. **端口被占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :5000
   
   # 或者使用其他端口
   export PORT=8080
   python server_deploy.py
   ```

### 调试模式

启动调试模式以获取更多信息：

```bash
export DEBUG=true
python server_deploy.py
```

## 安全建议

1. **网络安全**
   - 使用防火墙限制访问
   - 考虑使用HTTPS（配置SSL证书）
   - 设置API访问限制

2. **输入验证**
   - API已包含基本的输入验证
   - 考虑添加更严格的SMILES格式检查

3. **资源限制**
   - 限制单次请求的分子数量（默认100个）
   - 设置请求超时时间

## 扩展部署

### 负载均衡

如需处理大量请求，可以部署多个实例并使用负载均衡器：

```bash
# 启动多个实例
python server_deploy.py &  # 端口5000
PORT=5001 python server_deploy.py &  # 端口5001
PORT=5002 python server_deploy.py &  # 端口5002

# 使用nginx作为负载均衡器
```

### 缓存策略

考虑添加Redis缓存以提升重复查询的响应速度。

## 技术支持

如遇到问题，请检查：

1. Python版本兼容性
2. 依赖包版本
3. 模型文件完整性
4. 系统资源充足性
5. 网络连通性

---

**注意**: 该模型专为CPU推理优化，在CPU环境下可以稳定运行，无需GPU支持。 