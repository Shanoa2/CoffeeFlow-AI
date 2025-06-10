# 分子气味预测API - 服务器部署包

## 📦 部署包内容

这个部署包包含了在服务器上运行分子气味预测API所需的所有文件。

### 文件清单

**核心文件:**
- `predict_odor_cpu.py` - CPU专用预测器 (修复了138个任务的兼容性问题)
- `server_deploy.py` - Flask API服务器
- `test_api_client.py` - 客户端测试工具

**部署脚本:**
- `start_server.sh` - 开发/测试环境启动脚本
- `start_production.sh` - 生产环境启动脚本 (使用Gunicorn)
- `Dockerfile` - Docker容器化部署文件

**配置文件:**
- `requirements_server.txt` - Python依赖包列表
- `config.env` - 环境变量配置模板

**文档:**
- `README_server_deployment.md` - 详细部署指南
- `DEPLOY_README.md` - 本文件 (快速部署说明)

**模块代码:**
- `openpom/` - OpenPOM核心模块代码

## 🚀 快速部署步骤

### 1. 准备模型文件

将您训练好的模型文件放在以下目录结构中：

```
deploy_package/
├── ensemble_models/
│   ├── experiments_1/
│   │   └── checkpoint2.pt
│   ├── experiments_2/
│   │   └── checkpoint2.pt
│   ├── ...
│   └── experiments_10/
│       └── checkpoint2.pt
└── (其他文件...)
```

### 2. 环境准备

```bash
# 创建虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或者 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements_server.txt
```

### 3. 启动服务

**开发/测试环境:**
```bash
# 方法1: 使用启动脚本 (推荐)
chmod +x start_server.sh
./start_server.sh

# 方法2: 直接运行
python3 server_deploy.py
```

**生产环境:**
```bash
# 使用Gunicorn (推荐)
chmod +x start_production.sh
./start_production.sh

# 或者手动启动
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 server_deploy:app
```

### 4. 测试部署

```bash
# 健康检查
curl http://localhost:5000/

# 预测测试
python3 test_api_client.py

# 或者使用curl
curl -X POST http://localhost:5000/predict \
     -H "Content-Type: application/json" \
     -d '{"smiles": "CCO", "top_k": 5}'
```

## 🐳 Docker部署

```bash
# 构建镜像
docker build -t odor-prediction-api .

# 运行容器
docker run -p 5000:5000 \
    -v /path/to/your/models:/app/ensemble_models \
    odor-prediction-api
```

## ⚙️ 配置调优

### CPU性能优化

编辑 `config.env` 文件或设置环境变量：

```bash
# 根据CPU核心数调整
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8

# Gunicorn工作进程数 (建议CPU核心数的50%)
export WORKERS=4
```

### 内存优化

如果内存不足，可以：
1. 减少集成模型数量 (修改 `predict_odor_cpu.py` 中的 `n_models` 参数)
2. 减少 batch_size
3. 减少 Gunicorn worker 数量

## 🔧 故障排除

### 常见问题

1. **模型加载失败**
   ```
   检查: 模型文件路径和权限
   确保: ensemble_models/ 目录存在且包含正确的 .pt 文件
   ```

2. **内存不足**
   ```
   建议: 至少8GB RAM
   解决: 减少模型数量或worker数量
   ```

3. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :5000
   
   # 使用其他端口
   export PORT=8080
   ./start_server.sh
   ```

4. **依赖安装失败**
   ```bash
   # 更新pip
   pip install --upgrade pip
   
   # 手动安装核心依赖
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   pip install deepchem dgl dgllife flask
   ```

## 📊 API接口

### 主要端点

| 端点 | 方法 | 功能 | 示例 |
|------|------|------|------|
| `/` | GET | 健康检查 | `curl http://localhost:5000/` |
| `/predict` | POST | 单分子预测 | 见下方示例 |
| `/predict_batch` | POST | 批量预测 | 见下方示例 |
| `/tasks` | GET | 获取气味任务列表 | `curl http://localhost:5000/tasks` |

### 使用示例

**单分子预测:**
```bash
curl -X POST http://localhost:5000/predict \
     -H "Content-Type: application/json" \
     -d '{"smiles": "CCO", "top_k": 10}'
```

**批量预测:**
```bash
curl -X POST http://localhost:5000/predict_batch \
     -H "Content-Type: application/json" \
     -d '{"smiles_list": ["CCO", "CC(=O)OCC"], "threshold": 0.5}'
```

## 📝 系统要求

- **操作系统**: Linux, macOS, Windows
- **Python**: 3.8+
- **CPU**: 4核心+ (推荐8核心)
- **内存**: 8GB+ (推荐16GB)
- **存储**: 2GB+ (用于模型文件)

## 🔒 安全建议

1. **生产环境**:
   - 使用HTTPS
   - 配置防火墙
   - 限制API访问频率

2. **监控**:
   - 监控CPU和内存使用
   - 记录API访问日志
   - 设置健康检查

## 📞 技术支持

如遇问题，请检查：
1. 模型文件完整性
2. 依赖包版本兼容性
3. 系统资源充足性
4. 网络连通性

详细信息请参考: `README_server_deployment.md` 