import json
import requests

def main(arg1):
    """
    Dify代码执行节点最终修复版本
    参数名必须是arg1
    """
    try:
        # 解析输入数据
        if isinstance(arg1, str):
            molecules_data = json.loads(arg1)
        else:
            molecules_data = arg1
        
        molecules = molecules_data.get("molecules", [])
        
        # 提取SMILES列表
        smiles_list = []
        for mol in molecules:
            if "smiles" in mol:
                smiles_list.append(mol["smiles"])
        
        if not smiles_list:
            return {
                "error": "没有找到有效的SMILES分子",
                "success": False
            }
        
        # 调用OpenPOM API
        api_url = "https://capi.shanoa.net/predict_batch"
        payload = {
            "smiles_list": smiles_list,
            "threshold": 0.3,
            "top_k": 5
        }
        
        response = requests.post(api_url, json=payload, timeout=60)
        
        if response.status_code != 200:
            return {
                "error": f"API请求失败: {response.status_code}",
                "success": False
            }
        
        api_result = response.json()
        predictions = api_result.get("predictions", [])
        
        if not predictions:
            return {
                "error": "API返回空预测结果",
                "success": False
            }
        
        # 合并结果
        result_molecules = []
        for i, mol in enumerate(molecules):
            if i < len(predictions):
                new_mol = mol.copy()
                new_mol["odor_predictions"] = predictions[i].get("odors", [])
                result_molecules.append(new_mol)
        
        return {
            "molecules_with_odors": result_molecules,
            "total_predictions": len(result_molecules),
            "success": True
        }
        
    except json.JSONDecodeError:
        return {"error": "JSON解析失败", "success": False}
    except requests.RequestException as e:
        return {"error": f"网络请求错误: {str(e)}", "success": False}
    except Exception as e:
        return {"error": f"未知错误: {str(e)}", "success": False}