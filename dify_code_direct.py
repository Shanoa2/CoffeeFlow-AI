import json
import requests

def main(molecules_data):
    """
    直接使用变量名的版本
    """
    try:
        # 如果传入的是字符串，解析JSON
        if isinstance(molecules_data, str):
            molecules_obj = json.loads(molecules_data)
        else:
            molecules_obj = molecules_data
        
        molecules = molecules_obj.get("molecules", [])
        
        # 提取SMILES列表
        smiles_list = [mol["smiles"] for mol in molecules]
        
        if not smiles_list:
            return {"error": "没有找到SMILES分子", "success": False}
        
        # 调用API
        response = requests.post(
            "https://capi.shanoa.net/predict_batch",
            json={
                "smiles_list": smiles_list,
                "threshold": 0.3,
                "top_k": 5
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return {"error": f"API错误: {response.status_code}", "success": False}
        
        api_result = response.json()
        predictions = api_result.get("predictions", [])
        
        # 合并结果
        result_molecules = []
        for i, mol in enumerate(molecules):
            if i < len(predictions):
                mol["odor_predictions"] = predictions[i].get("odors", [])
                result_molecules.append(mol)
        
        return {
            "molecules_with_odors": result_molecules,
            "success": True
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}