# CoffeeFlow-AI 快速开始指南

## 🚀 5分钟快速部署

### 1. 检查API服务
```bash
curl https://capi.shanoa.net/
# 应返回：{"status": "healthy", "service": "Odor Prediction API", "models_loaded": 10}
```

### 2. 在Dify中导入工作流

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
- 使用提示词模板（见dify_prompts.md）

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

### 3. 测试工作流

输入示例：
```
我用埃塞俄比亚豆子，浅烘10分钟，180度，水洗的，手冲
```

预期输出：
- 花香果香突出
- 明亮酸度
- 茶感清晰

## 💡 关键要点

1. **参数提取器是核心** - 不要使用LLM节点提取参数
2. **结构化输出很重要** - 确保SMILES数组格式正确
3. **正确引用变量路径** - `{{#node-7.structured_output.smiles_list#}}`

## ❓ 常见问题

**Q: HTTP请求返回400错误？**
A: 检查结构化输出的变量引用路径

**Q: 参数提取不准确？**
A: 调整参数提取器的指令和默认值

**Q: API调用超时？**
A: 增加HTTP请求的超时时间到60秒

---

需要帮助？查看完整文档：COFFEEFLOW_FINAL_DOCUMENTATION.md