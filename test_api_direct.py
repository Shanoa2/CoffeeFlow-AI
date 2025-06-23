import requests
import json

# 测试数据
test_smiles = [
    "COC1=C(C=CC(=C1)C=O)O",
    "C1=CC=C(C=C1)C=O",
    "C(=O)C1=CC=CS1"
]

# 调用API
url = "https://capi.shanoa.net/predict_batch"
payload = {
    "smiles_list": test_smiles,
    "threshold": 0.3,
    "top_k": 5
}

print("发送请求:")
print(json.dumps(payload, indent=2))

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(f"\n响应状态码: {response.status_code}")
print("响应内容:")
print(response.text)