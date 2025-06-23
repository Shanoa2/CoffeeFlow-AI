import requests
import json
import time

def test_api_health():
    """测试OpenPOM API的健康状态和功能"""
    
    api_base = "https://capi.shanoa.net"
    
    print("=" * 50)
    print("OpenPOM API 健康度测试")
    print("=" * 50)
    
    # 1. 测试健康检查端点
    print("\n1. 测试健康检查端点...")
    try:
        response = requests.get(f"{api_base}/", timeout=10)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   响应: {response.json()}")
            print("   ✅ 健康检查通过")
        else:
            print(f"   ❌ 健康检查失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 连接错误: {str(e)}")
    
    # 2. 测试单分子预测
    print("\n2. 测试单分子预测...")
    try:
        test_data = {
            "smiles": "CCO",  # 乙醇
            "top_k": 5
        }
        response = requests.post(
            f"{api_base}/predict", 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   预测成功:")
            print(f"   - SMILES: {result.get('smiles')}")
            print(f"   - 预测时间: {result.get('prediction_time_seconds', 'N/A')}秒")
            if 'top_odors' in result:
                print(f"   - Top气味:")
                for odor in result['top_odors'][:3]:
                    print(f"     • {odor['odor']}: {odor['probability']:.3f}")
            print("   ✅ 单分子预测通过")
        else:
            print(f"   ❌ 预测失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求错误: {str(e)}")
    
    # 3. 测试批量预测
    print("\n3. 测试批量预测...")
    try:
        test_data = {
            "smiles_list": [
                "CCO",           # 乙醇
                "CC(=O)OCC",     # 乙酸乙酯
                "c1ccccc1"       # 苯
            ],
            "threshold": 0.3,
            "top_k": 5
        }
        
        print(f"   请求数据: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{api_base}/predict_batch",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 批量预测成功")
            if 'predictions' in result:
                print(f"   预测了 {len(result['predictions'])} 个分子")
                for i, pred in enumerate(result['predictions'][:2]):
                    print(f"   分子{i+1}: {pred.get('smiles', 'N/A')}")
                    if 'odors' in pred and pred['odors']:
                        print(f"   - Top气味: {pred['odors'][0]['odor']} ({pred['odors'][0]['probability']:.3f})")
        else:
            print(f"   ❌ 批量预测失败")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求错误: {str(e)}")
    
    # 4. 测试错误处理
    print("\n4. 测试错误处理...")
    try:
        # 测试空列表
        test_data = {
            "smiles_list": [],
            "threshold": 0.3,
            "top_k": 5
        }
        response = requests.post(
            f"{api_base}/predict_batch",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   空列表测试 - 状态码: {response.status_code}")
        if response.status_code == 400:
            print(f"   ✅ 正确返回400错误: {response.json()}")
        
        # 测试无效SMILES
        test_data = {
            "smiles": "INVALID_SMILES_STRING",
            "top_k": 5
        }
        response = requests.post(
            f"{api_base}/predict",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   无效SMILES测试 - 状态码: {response.status_code}")
        
    except Exception as e:
        print(f"   错误处理测试异常: {str(e)}")
    
    # 5. 性能测试
    print("\n5. 简单性能测试...")
    try:
        start_time = time.time()
        test_data = {
            "smiles_list": ["CCO"] * 5,  # 5个相同分子
            "threshold": 0.3,
            "top_k": 5
        }
        response = requests.post(
            f"{api_base}/predict_batch",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"   ✅ 5个分子批量预测耗时: {end_time - start_time:.2f}秒")
            result = response.json()
            if 'total_time_seconds' in result:
                print(f"   服务器报告处理时间: {result['total_time_seconds']:.2f}秒")
    except Exception as e:
        print(f"   性能测试错误: {str(e)}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_api_health()