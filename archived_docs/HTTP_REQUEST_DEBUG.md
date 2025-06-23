# HTTP请求节点调试指南

## 🔍 问题诊断

错误信息：`smiles_list必须是非空列表`

这表明HTTP请求节点没有正确传递数组数据到API。

## 🛠️ 解决方案

### 方案1：添加代码执行节点（推荐）

在节点7（SMILES提取）和节点8（HTTP请求）之间添加一个代码执行节点：

#### 代码执行节点配置

**输入变量**：
- 变量名：`input_data`
- 变量值：`{{#node-7#}}`

**代码内容**：
```python
import json

def main(input_data):
    """
    转换结构化输出为API请求格式
    """
    try:
        # 处理输入数据
        if isinstance(input_data, str):
            data = json.loads(input_data)
        else:
            data = input_data
        
        # 提取SMILES列表
        smiles_list = []
        
        # 尝试不同的数据结构
        if "structured_output" in data and "smiles_list" in data["structured_output"]:
            smiles_list = data["structured_output"]["smiles_list"]
        elif "smiles_list" in data:
            smiles_list = data["smiles_list"]
        elif isinstance(data, list):
            smiles_list = data
        
        # 构建API请求
        api_request = {
            "smiles_list": smiles_list,
            "threshold": 0.3,
            "top_k": 5
        }
        
        return api_request
        
    except Exception as e:
        return {
            "smiles_list": [],
            "threshold": 0.3,
            "top_k": 5,
            "error": str(e)
        }
```

然后HTTP请求节点的Body设置为：
```
{{#node-7.5#}}
```

### 方案2：使用LLM节点构建请求

在HTTP请求前添加LLM节点：

**系统提示词**：
```
将输入数据转换为OpenPOM API请求格式。

输出格式（只输出JSON，无其他内容）：
{
  "smiles_list": ["分子1", "分子2", ...],
  "threshold": 0.3,
  "top_k": 5
}

确保smiles_list是一个数组，即使只有一个元素。
```

**用户提示词**：
```
{{#node-7#}}
```

### 方案3：调试变量引用

#### 检查步骤：

1. **查看节点7的完整输出**
   - 在节点7后添加一个结束节点
   - 输出变量设为`{{#node-7#}}`
   - 运行查看完整结构

2. **测试不同的引用路径**
   ```
   {{#node-7.structured_output.smiles_list#}}
   {{#node-7.smiles_list#}}
   {{#node-7.output.smiles_list#}}
   {{#node-7.text#}}
   ```

3. **使用JSON字符串方式**
   如果数组引用有问题，尝试：
   ```json
   {
     "smiles_list": {{#node-7.text#}},
     "threshold": 0.3,
     "top_k": 5
   }
   ```

## 🧪 测试验证

### 手动测试API
```python
import requests
import json

# 测试数据
test_data = {
    "smiles_list": ["CCO", "CC(=O)OCC"],
    "threshold": 0.3,
    "top_k": 5
}

# 发送请求
response = requests.post(
    "https://capi.shanoa.net/predict_batch",
    json=test_data,
    headers={"Content-Type": "application/json"}
)

print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")
```

### 期望的请求体格式
```json
{
  "smiles_list": [
    "CCO",
    "CC(=O)OCC",
    "c1ccccc1"
  ],
  "threshold": 0.3,
  "top_k": 5
}
```

## 💡 最佳实践

1. **使用代码执行节点** - 最可靠的方式处理复杂数据转换
2. **添加错误处理** - 确保即使出错也返回有效格式
3. **逐步调试** - 先确认每个节点的输出格式
4. **保持简单** - 如果HTTP请求节点有限制，用代码节点替代

## 🎯 推荐解决流程

1. 采用**方案1**添加代码执行节点
2. 代码节点处理所有数据转换逻辑
3. HTTP请求节点只负责发送已格式化的数据
4. 这样可以完全控制数据格式，避免Dify的限制

---

如果问题仍然存在，请分享：
1. 节点7的完整输出
2. HTTP请求节点的具体配置截图
3. 任何错误消息的详细信息