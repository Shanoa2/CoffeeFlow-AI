import json

def main(arg1):
    """
    简单的数据转换器，将LLM输出转换为API请求格式
    """
    try:
        # 解析输入的text字段
        input_data = json.loads(arg1)
        smiles_array_str = input_data.get("text", "")
        
        # 解析SMILES数组字符串
        smiles_list = json.loads(smiles_array_str)
        
        # 构造API请求数据
        api_request = {
            "smiles_list": smiles_list,
            "threshold": 0.3,
            "top_k": 5
        }
        
        return api_request
        
    except Exception as e:
        return {"error": f"转换失败: {str(e)}"}