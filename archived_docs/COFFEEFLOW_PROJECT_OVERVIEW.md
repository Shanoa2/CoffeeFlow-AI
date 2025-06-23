# CoffeeFlow-AI 项目文件总览

## 📁 项目结构

```
CoffeeFlow-AI/
├── deploy_package/           # OpenPOM API部署包
│   ├── server_deploy.py      # Flask API服务器
│   ├── predict_odor_cpu.py   # CPU预测器
│   ├── requirements_server.txt # Python依赖
│   ├── ensemble_models/      # 训练好的模型文件
│   └── openpom/             # OpenPOM核心模块
│
├── DIFY_WORKFLOW_README.md   # Dify工作流开发指南 ⭐
├── coffee_molecule_database.csv # 咖啡分子数据库
├── dify_prompts.md          # Dify提示词模板
├── test_dify_integration.py # 集成测试脚本
└── README.md                # 项目说明

```

## 🚀 快速开始

### 1. 启动OpenPOM API服务
```bash
cd deploy_package
source venv/bin/activate
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
python server_deploy.py
```

服务将在 http://localhost:5000 启动

### 2. 配置Dify工作流
1. 打开 `DIFY_WORKFLOW_README.md` 查看详细配置指南
2. 导入 `coffee_molecule_database.csv` 到Dify知识库
3. 使用 `dify_prompts.md` 中的提示词模板

### 3. 测试集成
```bash
python test_dify_integration.py
```

## 📋 核心文件说明

### DIFY_WORKFLOW_README.md
完整的Dify工作流开发指南，包含：
- 系统架构设计
- 工作流节点配置
- 知识库准备指南
- 测试用例示例
- 故障排除方案

### coffee_molecule_database.csv
咖啡分子数据库，包含40+条记录：
- 不同产地的特征分子
- 烘焙程度影响
- SMILES分子表示
- 生成机理说明

### dify_prompts.md
优化的提示词模板：
- 分子预测提示词
- 风味分析提示词
- 错误处理模板
- 多语言版本

### test_dify_integration.py
集成测试工具：
- API连接测试
- 分子预测测试
- 完整工作流测试
- 性能基准测试

## 🔄 工作流程

1. **用户输入** → 咖啡制作参数
2. **知识检索** → 查询分子数据库
3. **LLM分析** → 预测分子组成
4. **API调用** → OpenPOM气味预测
5. **报告生成** → 风味分析报告

## 🛠️ 技术栈

- **后端**: Python 3.9, Flask, PyTorch
- **模型**: OpenPOM (Graph Neural Network)
- **工作流**: Dify平台
- **数据库**: CSV知识库（可扩展到向量数据库）

## 📈 下一步计划

1. 扩充咖啡分子数据库
2. 优化模型预测准确度
3. 添加可视化风味轮
4. 支持更多语言
5. 开发移动端界面

## 🤝 贡献指南

欢迎提交Issue和PR！请确保：
- 遵循现有代码风格
- 添加必要的测试
- 更新相关文档

## 📞 联系方式

- 项目仓库: https://github.com/Shanoa2/CoffeeFlow-AI
- 问题反馈: 提交GitHub Issue

---

**CoffeeFlow-AI** - 让每一杯咖啡的风味可以被科学预测 ☕🔬