# OpenPOM 分子气味预测 API

基于深度学习的分子气味预测系统，提供RESTful API服务，专为生产环境优化。

## 🌟 项目简介

OpenPOM (Open Prediction of Odor from Molecules) 是一个基于图神经网络的分子气味预测模型。本仓库提供了将训练好的OpenPOM模型部署为HTTP API服务的完整解决方案，支持对分子的138种气味特征进行预测。

### 主要特性

- 🚀 **生产就绪**：包含开发和生产环境配置
- 🔬 **138种气味预测**：支持完整的气味特征预测
- 💻 **CPU优化**：专为服务器CPU环境优化，无需GPU
- 📦 **批量处理**：支持单分子和批量分子预测
- 🛡️ **稳定可靠**：包含错误处理和健康检查机制
- 🐳 **容器化支持**：提供Docker部署方案

## 📋 系统要求

- **操作系统**: Linux, macOS, Windows
- **Python**: 3.8+ (推荐3.10)
- **内存**: 8GB+ (推荐16GB)
- **CPU**: 4核心+ (推荐8核心)
- **存储**: 2GB+ (用于模型文件)

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/openpom-api.git
cd openpom-api
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖包
pip install -r requirements_server.txt
```

### 3. 准备模型文件

将训练好的模型文件放置在以下目录结构中：

```
ensemble_models/
├── experiments_1/
│   └── checkpoint2.pt
├── experiments_2/
│   └── checkpoint2.pt
├── ...
└── experiments_10/
    └── checkpoint2.pt
```

### 4. 启动服务

**开发环境**：
```bash
./start_server.sh
```

**生产环境**：
```bash
./start_production.sh
```

服务将在 `http://localhost:5000` 启动。

## 📡 API 接口

### 健康检查

```bash
GET /
```

**响应示例**：
```json
{
    "status": "healthy",
    "service": "Odor Prediction API",
    "version": "1.0.0",
    "models_loaded": 10,
    "cpu_count": 8,
    "memory_total_gb": 16.0
}
```

### 单分子预测

```bash
POST /predict
Content-Type: application/json

{
    "smiles": "CCO",
    "top_k": 5
}
```

**响应示例**：
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

### 批量预测

```bash
POST /predict_batch
Content-Type: application/json

{
    "smiles_list": ["CCO", "CC(=O)OCC", "c1ccc(cc1)O"],
    "threshold": 0.5
}
```

### 获取支持的气味任务

```bash
GET /tasks
```

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t openpom-api .
```

### 运行容器

```bash
docker run -p 5000:5000 \
    -v /path/to/models:/app/ensemble_models \
    openpom-api
```

## 🧪 测试

使用提供的测试脚本：

```bash
# 基础功能测试
python test_api_client.py

# 性能测试
python test_api_client.py --perf-test --num-requests 20

# 测试远程服务器
python test_api_client.py --url http://your-server:5000
```

## ⚙️ 配置优化

### CPU性能优化

```bash
# 设置环境变量
export OMP_NUM_THREADS=8      # 根据CPU核心数调整
export MKL_NUM_THREADS=8      # Intel MKL线程数
```

### 生产环境配置

编辑 `config.env` 文件或设置环境变量：

```bash
export WORKERS=4              # Gunicorn工作进程数
export PORT=5000              # 服务端口
export HOST=0.0.0.0          # 绑定地址
```

## 📂 项目结构

```
.
├── deploy_package/              # 部署包目录
│   ├── predict_odor_cpu.py     # CPU预测器核心代码
│   ├── server_deploy.py         # Flask API服务器
│   ├── test_api_client.py       # API测试客户端
│   ├── requirements_server.txt  # Python依赖
│   ├── start_server.sh         # 开发环境启动脚本
│   ├── start_production.sh     # 生产环境启动脚本
│   ├── Dockerfile              # Docker配置
│   ├── config.env              # 环境配置模板
│   └── openpom/                # OpenPOM核心模块
│       ├── feat/               # 特征提取模块
│       ├── models/             # 模型定义
│       ├── layers/             # 神经网络层
│       └── utils/              # 工具函数
└── README.md                   # 本文件
```

## 🔧 故障排除

### 常见问题

1. **模型加载失败**
   - 检查模型文件路径是否正确
   - 确认 `ensemble_models/` 目录存在
   - 验证 `.pt` 文件完整性

2. **内存不足**
   - 建议至少8GB RAM
   - 可通过减少模型数量降低内存需求
   - 调整批处理大小

3. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :5000
   
   # 使用其他端口
   export PORT=8080
   ./start_server.sh
   ```

## 🛠️ 开发指南

### 添加新功能

1. 在 `server_deploy.py` 中添加新的API端点
2. 在 `predict_odor_cpu.py` 中实现相应的预测逻辑
3. 更新测试脚本 `test_api_client.py`
4. 更新文档

### 性能优化建议

- 使用模型缓存减少加载时间
- 实现请求批处理
- 添加结果缓存（如Redis）
- 使用异步处理提高并发能力

## 📚 相关资源

- [OpenPOM原始论文](https://www.biorxiv.org/content/10.1101/2022.09.01.504602v4)
- [DeepChem文档](https://deepchem.io/)
- [DGL文档](https://www.dgl.ai/)

## 🤝 贡献指南

欢迎提交Issue和Pull Request。请确保：

1. 代码符合项目风格
2. 添加必要的测试
3. 更新相关文档
4. 提交前运行测试

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 👥 团队

CoffeeFlowAI团队 - 人工智能课程项目

## 📮 联系方式

- Issue: [GitHub Issues](https://github.com/yourusername/openpom-api/issues)
- Email: your-email@example.com

---

**注意**：本项目是CoffeeFlowAI系统的一部分，专注于将OpenPOM模型部署为API服务。完整的咖啡风味预测系统还包括RAG知识检索和Dify工作流等组件。
