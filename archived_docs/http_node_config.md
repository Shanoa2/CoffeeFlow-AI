# 使用HTTP请求节点替代代码执行节点

## 🔧 节点配置

**节点类型**: HTTP请求节点  
**请求方法**: POST  
**请求URL**: `https://capi.shanoa.net/predict_batch`  

## 📋 请求配置

### Headers（请求头）
```
Content-Type: application/json
```

### Body（请求体）
选择"JSON"格式，输入：
```json
{
  "smiles_list": {{smiles_array}},
  "threshold": 0.3,
  "top_k": 5
}
```

## 🔄 前置处理

在HTTP请求节点之前，添加一个LLM节点来提取SMILES数组：

### LLM节点配置
**系统提示词**:
```
你需要从分子数据中提取SMILES列表，只输出JSON数组格式。

输入格式：
{
  "molecules": [
    {"smiles": "CCO", "name": "乙醇"},
    {"smiles": "CC(=O)OCC", "name": "乙酸乙酯"}
  ]
}

输出格式：
["CCO", "CC(=O)OCC"]

只输出SMILES数组，不要其他内容。
```

**用户提示词**:
```
{{#node-6.output#}}
```

**输出变量名**: `smiles_array`

## 📊 完整流程

```
节点6(分子预测) → 节点7(SMILES提取LLM) → 节点8(HTTP请求OpenPOM) → 节点9(结果处理)
```

## ✅ 优势

1. **避免代码执行问题** - 使用原生HTTP节点
2. **更稳定** - 不依赖Python环境
3. **更直观** - 配置简单明了
4. **更易调试** - 可以直接看到API请求和响应

## 🔄 后续处理

HTTP请求节点返回的结果可以直接传给下一个LLM节点进行风味分析。