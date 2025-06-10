# 🚀 快速部署指南

## 📁 部署包：`odor-prediction-api-deploy_20250610_190647.tar.gz`

### ✅ 预检要求
- **Python**: 3.8+
- **内存**: 8GB+ RAM
- **CPU**: 4核心+
- **存储**: 2GB+ 空间

### 🛠 部署步骤

#### 1. 上传并解压
```bash
# 上传tar包到服务器
scp odor-prediction-api-deploy_20250610_190647.tar.gz user@server:/path/to/deploy/

# 在服务器上解压
tar -xzf odor-prediction-api-deploy_20250610_190647.tar.gz
cd deploy_package
```

#### 2. 准备模型文件
```bash
# 创建模型目录
mkdir -p ensemble_models

# 复制您的模型文件 (需要您手动操作)
# 确保文件结构如下:
# ensemble_models/
# ├── experiments_1/checkpoint2.pt
# ├── experiments_2/checkpoint2.pt
# ├── ...
# └── experiments_10/checkpoint2.pt
```

#### 3. 验证环境
```bash
# 运行验证脚本
./verify_deployment.sh
```

#### 4. 安装依赖
```bash
# 创建虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements_server.txt
```

#### 5. 启动服务

**开发/测试环境:**
```bash
./start_server.sh
```

**生产环境:**
```bash
# 安装Gunicorn
pip install gunicorn

# 启动生产服务
./start_production.sh
```

#### 6. 测试部署
```bash
# 健康检查
curl http://localhost:5000/

# 运行完整测试
python3 test_api_client.py

# 单分子测试
curl -X POST http://localhost:5000/predict \
     -H "Content-Type: application/json" \
     -d '{"smiles": "CCO", "top_k": 5}'
```

### 🐳 Docker部署 (可选)
```bash
# 构建镜像
docker build -t odor-prediction-api .

# 运行容器
docker run -p 5000:5000 \
    -v /path/to/models:/app/ensemble_models \
    odor-prediction-api
```

### ⚙️ 配置优化

**环境变量配置:**
```bash
export OMP_NUM_THREADS=8      # CPU线程数
export MKL_NUM_THREADS=8      # Intel MKL线程数
export WORKERS=4              # Gunicorn工作进程数
export PORT=5000              # 服务端口
```

**生产环境配置:**
```bash
# 编辑配置文件
cp config.env .env
# 修改 .env 文件中的参数

# 后台运行
nohup ./start_production.sh > server.log 2>&1 &
```

### 🔧 故障排除

| 问题 | 解决方案 |
|------|----------|
| 模型加载失败 | 检查模型文件路径和权限 |
| 内存不足 | 减少模型数量或worker数量 |
| 端口被占用 | `export PORT=8080` 使用其他端口 |
| 依赖安装失败 | 更新pip: `pip install --upgrade pip` |

### 📊 API接口
- **健康检查**: `GET /`
- **单分子预测**: `POST /predict`
- **批量预测**: `POST /predict_batch`
- **气味任务**: `GET /tasks`

### 📱 监控命令
```bash
# 查看进程
ps aux | grep python

# 查看端口
netstat -tuln | grep 5000

# 查看日志
tail -f server.log

# 查看资源使用
htop
```

---

**✨ 关键特性:**
- ✅ **CPU专用** - 无需GPU
- ✅ **138种气味** - 完整任务支持  
- ✅ **REST API** - 标准HTTP接口
- ✅ **生产就绪** - 包含Gunicorn配置
- ✅ **Docker支持** - 容器化部署

**📞 需要帮助？** 
查看详细文档: `README_server_deployment.md` 