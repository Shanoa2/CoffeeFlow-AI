import json

def main(input_data):
    """
    修复JSON格式问题 - Dify代码执行节点
    """
    try:
        # 处理输入
        if isinstance(input_data, str):
            data = json.loads(input_data)
        else:
            data = input_data
        
        # 提取SMILES列表
        smiles_list = []
        
        # 从structured_output中提取
        if isinstance(data, dict) and "structured_output" in data:
            struct_output = data["structured_output"]
            if isinstance(struct_output, dict) and "smiles_list" in struct_output:
                smiles_list = struct_output["smiles_list"]
        
        # 确保是列表格式
        if not isinstance(smiles_list, list):
            smiles_list = []
        
        # 构建正确格式的请求
        return {
            "smiles_list": smiles_list,
            "threshold": 0.3,
            "top_k": 5
        }
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return {
            "smiles_list": [],
            "threshold": 0.3,
            "top_k": 5
        }