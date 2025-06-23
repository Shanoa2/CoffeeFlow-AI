import json
import requests

def main(arg1: str) -> dict:
    """
    Dify代码执行节点专用版本
    调用远程OpenPOM API批量预测分子气味
    API地址: https://capi.shanoa.net
    
    Args:
        arg1: 分子数据的JSON字符串
    """
    try:
        # 解析分子数据
        molecules_data = json.loads(arg1)
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
        
        # 设置请求超时和重试
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
                "success": False,
                "api_response": api_response
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
            "api_response_time": api_response.get("total_time_seconds", 0),
            "status": "success",
            "success": True
        }
        
    except requests.exceptions.Timeout:
        return {
            "error": "API请求超时，请检查网络连接或稍后重试",
            "status": "timeout",
            "success": False
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": "无法连接到OpenPOM API服务器",
            "status": "connection_error",
            "success": False
        }
    except requests.exceptions.HTTPError as e:
        return {
            "error": f"API返回HTTP错误: {e.response.status_code}",
            "status": "http_error",
            "success": False,
            "details": e.response.text if e.response else "无详细信息"
        }
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON解析错误: {str(e)}",
            "status": "json_error",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"未知错误: {str(e)}",
            "status": "unknown_error",
            "success": False
        }

# 测试函数
if __name__ == "__main__":
    # 测试数据
    test_data = {
        "molecules": [
            {
                "smiles": "CCO",
                "name": "乙醇",
                "percentage": 0.5,
                "source": "发酵过程"
            },
            {
                "smiles": "CC(=O)OCC",
                "name": "乙酸乙酯",
                "percentage": 0.3,
                "source": "发酵过程"
            }
        ]
    }
    
    # 运行测试
    result = main(json.dumps(test_data))
    print("测试结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))