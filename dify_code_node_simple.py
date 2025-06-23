import json
import requests

# Dify代码执行节点的全局变量方式
def main(**kwargs):
    """
    Dify代码执行节点专用版本
    调用远程OpenPOM API批量预测分子气味
    """
    try:
        # 从kwargs中获取输入数据
        molecules_json = None
        for key, value in kwargs.items():
            if isinstance(value, str) and value.strip().startswith('{'):
                molecules_json = value
                break
        
        if not molecules_json:
            # 如果没有找到JSON字符串，尝试第一个参数
            first_arg = list(kwargs.values())[0] if kwargs else None
            if first_arg:
                molecules_json = str(first_arg)
        
        if not molecules_json:
            return {
                "error": "未找到分子数据输入",
                "status": "failed",
                "success": False
            }
        
        # 解析分子数据
        molecules_data = json.loads(molecules_json)
        molecules = molecules_data.get("molecules", [])
        
        # 提取SMILES列表
        smiles_list = [mol["smiles"] for mol in molecules]
        
        if not smiles_list:
            return {
                "error": "没有找到有效的SMILES分子",
                "status": "failed",
                "success": False
            }
        
        # 调用远程OpenPOM API
        api_url = "https://capi.shanoa.net/predict_batch"
        payload = {
            "smiles_list": smiles_list,
            "threshold": 0.3,
            "top_k": 5
        }
        
        # 设置请求
        response = requests.post(
            api_url, 
            json=payload, 
            timeout=60,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        # 处理响应
        api_response = response.json()
        predictions = api_response.get("predictions", [])
        
        if not predictions:
            return {
                "error": "API返回空的预测结果",
                "status": "failed",
                "success": False
            }
        
        # 合并原始数据和预测结果
        molecules_with_odors = []
        for i, mol in enumerate(molecules):
            if i < len(predictions):
                mol_result = mol.copy()
                mol_result["odor_predictions"] = predictions[i].get("odors", [])
                mol_result["prediction_confidence"] = predictions[i].get("confidence", 0.0)
                molecules_with_odors.append(mol_result)
        
        return {
            "molecules_with_odors": molecules_with_odors,
            "total_predictions": len(molecules_with_odors),
            "status": "success",
            "success": True
        }
        
    except Exception as e:
        return {
            "error": f"执行错误: {str(e)}",
            "status": "error",
            "success": False
        }