# CoffeeFlow-AI

基于OpenPOM深度学习模型的智能咖啡风味预测系统

## 🎯 项目简介

CoffeeFlow-AI 结合了最先进的图神经网络气味预测技术（OpenPOM）和大语言模型，为咖啡爱好者提供科学、专业的风味分析。用户只需用自然语言描述咖啡制作过程，系统就能预测其风味特征。

### 核心特性

- 🗣️ **自然语言输入**：无需专业知识，用日常语言描述即可
- 🔬 **科学预测**：基于分子层面的138种气味特征预测
- 📚 **智能分析**：结合科研文献的深度分析
- 📊 **专业报告**：生成咖啡品鉴师级别的风味报告
- 🚀 **生产就绪**：包含完整的部署方案
- 💻 **CPU优化**：无需GPU，适合服务器部署

## 🏗️ 系统架构

```
┌─────────────────┐
│   用户输入界面   │
└────────┬────────┘
         ↓
┌─────────────────┐     ┌──────────────────┐
│  Dify Workflow  │────→│  科研文献知识库   │
└────────┬────────┘     └──────────────────┘
         ↓
┌─────────────────┐     ┌──────────────────┐
│  LLM 分析引擎   │────→│  OpenPOM API    │
└────────┬────────┘     │ (capi.shanoa.net)│
         ↓              └──────────────────┘
┌─────────────────┐
│   风味报告输出   │
└─────────────────┘
```

### 工作流程

1. **自然语言理解**：使用Dify参数提取器理解用户输入
2. **知识检索**：从科研文献中检索相关咖啡化学信息
3. **分子预测**：基于文献预测咖啡中的香味分子
4. **气味分析**：通过OpenPOM API预测分子气味
5. **风味报告**：生成专业的咖啡品鉴报告

## 📋 系统要求

- **操作系统**: Linux, macOS, Windows
- **Python**: 3.9
- **内存**: 8GB+ (推荐16GB)
- **CPU**: 4核心+ (推荐8核心)
- **存储**: 2GB+ (用于模型文件)

## 🚀 快速开始

### 1. 体验在线服务

```bash
# 检查API服务状态
curl https://capi.shanoa.net/
```

### 2. 在Dify中创建工作流

#### Step 1: 创建新工作流
- 登录Dify
- 创建新应用 → 选择"工作流"
- 命名：CoffeeFlow-AI

#### Step 2: 配置节点（按顺序）

**节点1 - 开始节点**
- 添加变量：`user_description`（文本）

**节点2 - 参数提取器** ⭐
- 连接：节点1
- 配置6个参数：
  - coffee_origin（字符串，必需）
  - roast_level（选项：浅烘/中烘/深烘）
  - roast_time（数字，5-25）
  - roast_temp（数字，160-250）
  - process_method（选项：水洗/日晒/蜜处理/湿刨法）
  - brewing_method（选项：手冲/意式/法压壶/虹吸壶）

**节点3&4 - 知识检索**
- 知识库：coffee_research_database
- 检索模式：混合检索
- Top K：8-10

**节点5&6 - LLM分析**
- 使用提示词模板（见配置文档）

**节点7 - SMILES提取**
- 启用结构化输出
- Schema：
```json
{
  "type": "object",
  "properties": {
    "smiles_list": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

**节点8 - HTTP请求**
- URL：`https://capi.shanoa.net/predict_batch`
- 方法：POST
- Body：
```json
{
  "smiles_list": {{#node-7.structured_output.smiles_list#}},
  "threshold": 0.3,
  "top_k": 5
}
```

**节点9 - 风味报告**
- 引用所有前面节点的输出
- 生成最终报告

### 3. 本地部署（可选）

```bash
# 克隆仓库
git clone https://github.com/yourusername/CoffeeFlow-AI.git
cd CoffeeFlow-AI/deploy_package

# 创建虚拟环境
python3.9 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖包
pip install -r requirements_server.txt
```

#### 准备模型文件

```bash
# 下载模型压缩包
wget https://github.com/Shanoa2/CoffeeFlow-AI/releases/download/Model/ensemble_models.zip

# 解压文件
unzip ensemble_models.zip

# 可选：删除下载的压缩包
rm ensemble_models.zip
```

#### 启动服务

**开发环境**：
```bash
./start_server.sh
```

**生产环境**：
```bash
./start_production.sh
```

服务将在 `http://localhost:5000` 启动。

## 📊 使用示例

### 输入示例
```
我用埃塞俄比亚豆子，浅烘10分钟，180度，水洗的，手冲
```

### 输出示例
```
风味概览：
这杯咖啡呈现典型的埃塞俄比亚浅烘特征，以明亮的花果香调为主导。

主要风味：
- 前段：茉莉花香、柑橘酸度
- 中段：蜜桃、杏子的果香
- 尾韵：绿茶般的清新感

建议冲煮参数：
- 水温：90-92°C
- 粉水比：1:15
- 研磨度：中细
```

## 📡 OpenPOM API 接口

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

## 🔧 Dify工作流详细配置

### 参数提取器优势
- ✅ **更稳定**：输出格式固定，避免JSON解析错误
- ✅ **更快速**：专门优化的提取算法
- ✅ **更经济**：比LLM节点消耗更少资源
- ✅ **类型安全**：自动类型验证和范围检查

### 知识库配置

#### 内容类型
- 咖啡化学研究论文
- 烘焙化学反应研究
- 挥发性有机化合物分析报告
- 不同产地咖啡成分对比研究
- 处理方法对化学成分影响的研究

#### 检索配置
- **分段方式**：智能分段
- **嵌入模型**：text-embedding-3-large
- **检索模式**：混合检索
- **Top-K**：8-10
- **Score阈值**：0.6

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

## ⚙️ 配置优化

### CPU性能优化

```bash
# 设置环境变量
export OMP_NUM_THREADS=8      # 根据CPU核心数调整
export MKL_NUM_THREADS=8      # Intel MKL线程数
```

### 生产环境配置

```bash
export WORKERS=4              # Gunicorn工作进程数
export PORT=5000              # 服务端口
export HOST=0.0.0.0          # 绑定地址
```

## 📂 项目结构

```
CoffeeFlow-AI/
├── deploy_package/              # OpenPOM API部署包
│   ├── predict_odor_cpu.py     # CPU预测器核心代码
│   ├── server_deploy.py         # Flask API服务器
│   ├── requirements_server.txt  # Python依赖
│   ├── start_server.sh         # 启动脚本
│   └── openpom/                # OpenPOM核心模块
├── coffee_molecule_database.csv # 咖啡分子数据库
├── dify_prompts.md             # LLM提示词模板
├── test_dify_integration.py    # 集成测试脚本
└── README.md                   # 本文件
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

4. **HTTP请求返回400错误**
   - 检查结构化输出的变量引用路径
   - 确认引用格式：`{{#node-7.structured_output.smiles_list#}}`

5. **参数提取不准确**
   - 调整参数提取器的指令和默认值
   - 确保参数类型和范围设置正确

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

## 🔬 技术栈

- **深度学习**：OpenPOM (DeepChem + DGL + PyTorch)
- **工作流平台**：Dify
- **API服务**：Flask + Gunicorn
- **知识管理**：RAG + 向量数据库
- **自然语言处理**：GPT-4 / Claude

## 📚 相关资源

- [OpenPOM原始论文](https://www.biorxiv.org/content/10.1101/2022.09.01.504602v4)
- [DeepChem文档](https://deepchem.io/)
- [DGL文档](https://www.dgl.ai/)
- [Dify文档](https://docs.dify.ai/)

## 🤝 贡献指南

欢迎提交Issue和Pull Request。请确保：

1. 代码符合项目风格
2. 添加必要的测试
3. 更新相关文档
4. 提交前运行测试

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🏆 项目亮点

1. **创新性应用**：首次将图神经网络气味预测技术应用于咖啡风味分析
2. **科学依据充分**：基于大量科研文献和化学数据
3. **用户友好**：自然语言输入，专业风味报告输出
4. **技术领先**：结合最新的AI技术栈
5. **开源贡献**：完整的代码和文档供社区使用

## 👥 团队

CoffeeFlow-AI Team

---

**项目状态**：✅ 生产就绪  
**最新版本**：v2.0  
**更新日期**：2024-06-23

## 📞 联系方式

- 项目仓库: https://github.com/Shanoa2/CoffeeFlow-AI
- 问题反馈: 提交GitHub Issue

---

*让每一杯咖啡的风味可以被科学预测* ☕🔬