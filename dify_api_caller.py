import json
import requests

def main(arg1):
    """
    接收结构化输出并调用OpenPOM API
    """
    try:
        # 解析输入数据
        if isinstance(arg1, str):
            input_data = json.loads(arg1)
        else:
            input_data = arg1
        
        # 提取SMILES列表
        # 尝试从structured_output中获取
        if "structured_output" in input_data:
            smiles_list = input_data["structured_output"].get("smiles_list", [])
        # 如果直接就是smiles_list
        elif "smiles_list" in input_data:
            smiles_list = input_data["smiles_list"]
        # 如果是数组格式
        elif isinstance(input_data, list):
            smiles_list = input_data
        else:
            return {"error": "无法找到SMILES列表", "success": False}
        
        if not smiles_list:
            return {"error": "SMILES列表为空", "success": False}
        
        # 调用API
        url = "https://capi.shanoa.net/predict_batch"
        payload = {
            "smiles_list": smiles_list,
            "threshold": 0.3,
            "top_k": 5
        }
        
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            return {
                "predictions": response.json(),
                "success": True
            }
        else:
            return {
                "error": f"API错误: {response.status_code}",
                "details": response.text,
                "success": False
            }
            
    except Exception as e:
        return {
            "error": f"执行错误: {str(e)}",
            "success": False
        }