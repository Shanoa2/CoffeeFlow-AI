#!/usr/bin/env python3
"""
API客户端测试脚本
用于测试分子气味预测API服务器
"""

import requests
import json
import time

class OdorPredictionClient:
    def __init__(self, base_url='http://localhost:5000'):
        """
        初始化客户端
        
        Args:
            base_url: API服务器地址
        """
        self.base_url = base_url.rstrip('/')
        
    def health_check(self):
        """健康检查"""
        try:
            response = requests.get(f'{self.base_url}/')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def predict_single(self, smiles, top_k=10):
        """预测单个分子"""
        try:
            data = {
                'smiles': smiles,
                'top_k': top_k
            }
            response = requests.post(
                f'{self.base_url}/predict',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def predict_batch(self, smiles_list, threshold=0.5):
        """批量预测多个分子"""
        try:
            data = {
                'smiles_list': smiles_list,
                'threshold': threshold
            }
            response = requests.post(
                f'{self.base_url}/predict_batch',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def get_tasks(self):
        """获取所有气味任务"""
        try:
            response = requests.get(f'{self.base_url}/tasks')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}

def test_api(server_url='http://localhost:5000'):
    """测试API的所有功能"""
    print(f"=== API客户端测试 ===")
    print(f"服务器地址: {server_url}")
    
    client = OdorPredictionClient(server_url)
    
    # 1. 健康检查
    print(f"\n1. 健康检查:")
    health = client.health_check()
    if 'error' in health:
        print(f"   ❌ 失败: {health['error']}")
        return False
    else:
        print(f"   ✓ 状态: {health.get('status', 'unknown')}")
        print(f"   - 服务: {health.get('service', 'unknown')}")
        print(f"   - 版本: {health.get('version', 'unknown')}")
        print(f"   - CPU模式: {health.get('cpu_only', False)}")
        print(f"   - 已加载模型: {health.get('models_loaded', 0)}")
    
    # 2. 获取气味任务
    print(f"\n2. 获取气味任务:")
    tasks = client.get_tasks()
    if 'error' in tasks:
        print(f"   ❌ 失败: {tasks['error']}")
    else:
        print(f"   ✓ 气味任务数量: {tasks.get('task_count', 0)}")
        if 'tasks' in tasks:
            print(f"   - 前10个任务: {tasks['tasks'][:10]}")
    
    # 3. 单分子预测
    print(f"\n3. 单分子预测:")
    test_smiles = 'CCO'  # 乙醇
    result = client.predict_single(test_smiles, top_k=5)
    if 'error' in result:
        print(f"   ❌ 失败: {result['error']}")
    else:
        print(f"   ✓ 分子: {result.get('smiles', 'unknown')}")
        print(f"   - 预测时间: {result.get('prediction_time_seconds', 0):.3f}秒")
        print(f"   - 前5种气味:")
        for odor in result.get('top_odors', [])[:5]:
            print(f"     {odor['odor']:15s}: {odor['probability']:.3f}")
    
    # 4. 批量预测
    print(f"\n4. 批量预测:")
    test_smiles_list = ['CCO', 'CC(=O)OCC', 'c1ccc(cc1)O']  # 乙醇、乙酸乙酯、苯酚
    result = client.predict_batch(test_smiles_list, threshold=0.5)
    if 'error' in result:
        print(f"   ❌ 失败: {result['error']}")
    else:
        print(f"   ✓ 分子数量: {result.get('molecule_count', 0)}")
        print(f"   - 预测时间: {result.get('prediction_time_seconds', 0):.3f}秒")
        print(f"   - 阈值: {result.get('threshold', 0.5)}")
        
        # 显示每个分子的预测概率最高的3种气味
        predictions = result.get('predictions', [])
        for pred in predictions:
            smiles = pred['SMILES']
            # 获取除SMILES外的所有气味概率
            odor_probs = [(k, v) for k, v in pred.items() if k != 'SMILES']
            # 按概率排序
            odor_probs.sort(key=lambda x: x[1], reverse=True)
            print(f"   - {smiles} 最可能的3种气味:")
            for odor, prob in odor_probs[:3]:
                print(f"     {odor:15s}: {prob:.3f}")
    
    print(f"\n✓ API测试完成")
    return True

def performance_test(server_url='http://localhost:5000', num_requests=10):
    """性能测试"""
    print(f"\n=== 性能测试 ===")
    print(f"发送 {num_requests} 个单分子预测请求...")
    
    client = OdorPredictionClient(server_url)
    test_smiles = 'CCO'
    
    times = []
    success_count = 0
    
    for i in range(num_requests):
        start_time = time.time()
        result = client.predict_single(test_smiles, top_k=5)
        end_time = time.time()
        
        request_time = end_time - start_time
        times.append(request_time)
        
        if 'error' not in result:
            success_count += 1
            print(f"  请求 {i+1:2d}: {request_time:.3f}秒 ✓")
        else:
            print(f"  请求 {i+1:2d}: {request_time:.3f}秒 ❌ {result['error']}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n性能统计:")
        print(f"  成功率: {success_count}/{num_requests} ({success_count/num_requests*100:.1f}%)")
        print(f"  平均响应时间: {avg_time:.3f}秒")
        print(f"  最短响应时间: {min_time:.3f}秒")
        print(f"  最长响应时间: {max_time:.3f}秒")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='API客户端测试工具')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='API服务器地址 (默认: http://localhost:5000)')
    parser.add_argument('--perf-test', action='store_true',
                       help='运行性能测试')
    parser.add_argument('--num-requests', type=int, default=10,
                       help='性能测试请求数量 (默认: 10)')
    
    args = parser.parse_args()
    
    # 基本功能测试
    if test_api(args.url):
        # 性能测试（可选）
        if args.perf_test:
            performance_test(args.url, args.num_requests)
    else:
        print("❌ 基本功能测试失败，跳过性能测试")

if __name__ == "__main__":
    main() 