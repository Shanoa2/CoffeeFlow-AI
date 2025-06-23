import json

def main(input_data):
    """
    Dify代码执行节点 - 转换结构化输出为API请求格式
    将节点7的输出转换为OpenPOM API需要的格式
    """
    try:
        # 处理输入数据
        if isinstance(input_data, str):
            data = json.loads(input_data)
        else:
            data = input_data
        
        # 调试：打印输入数据结构
        print(f"输入数据类型: {type(data)}")
        print(f"输入数据: {data}")
        
        # 提取SMILES列表 - 尝试多种可能的路径
        smiles_list = []
        
        # 情况1: structured_output.smiles_list
        if isinstance(data, dict):
            if "structured_output" in data and isinstance(data["structured_output"], dict):
                if "smiles_list" in data["structured_output"]:
                    smiles_list = data["structured_output"]["smiles_list"]
                    print(f"从structured_output提取: {smiles_list}")
            
            # 情况2: 直接的smiles_list
            elif "smiles_list" in data:
                smiles_list = data["smiles_list"]
                print(f"从根级别提取: {smiles_list}")
            
            # 情况3: text字段包含JSON
            elif "text" in data:
                try:
                    text_data = json.loads(data["text"])
                    if isinstance(text_data, dict) and "smiles_list" in text_data:
                        smiles_list = text_data["smiles_list"]
                        print(f"从text字段提取: {smiles_list}")
                except:
                    pass
        
        # 情况4: 输入直接是列表
        elif isinstance(data, list):
            smiles_list = data
            print(f"输入直接是列表: {smiles_list}")
        
        # 验证SMILES列表
        if not smiles_list or not isinstance(smiles_list, list):
            print(f"警告: 未找到有效的SMILES列表")
            smiles_list = []
        
        # 构建API请求
        api_request = {
            "smiles_list": smiles_list,
            "threshold": 0.3,
            "top_k": 5
        }
        
        print(f"最终API请求: {api_request}")
        return api_request
        
    except Exception as e:
        print(f"错误: {str(e)}")
        # 返回空请求以避免HTTP错误
        return {
            "smiles_list": [],
            "threshold": 0.3,
            "top_k": 5,
            "error": f"数据转换错误: {str(e)}"
        }