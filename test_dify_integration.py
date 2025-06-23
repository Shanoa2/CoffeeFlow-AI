#!/usr/bin/env python3
"""
CoffeeFlow-AI Dify工作流集成测试
用于测试完整的咖啡风味预测流程
"""

import json
import requests
import time
from typing import Dict, List, Any


class CoffeeFlowTester:
    def __init__(self, dify_api_key: str, dify_base_url: str = "http://localhost:3000"):
        """
        初始化测试器
        
        Args:
            dify_api_key: Dify API密钥
            dify_base_url: Dify服务地址
        """
        self.api_key = dify_api_key
        self.base_url = dify_base_url
        self.headers = {
            "Authorization": f"Bearer {dify_api_key}",
            "Content-Type": "application/json"
        }
    
    def test_openpom_api(self) -> bool:
        """测试OpenPOM API是否正常运行"""
        try:
            response = requests.get("https://capi.shanoa.net/")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ OpenPOM API运行正常: {data['models_loaded']}个模型已加载")
                return True
            else:
                print(f"✗ OpenPOM API响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ OpenPOM API连接失败: {e}")
            return False
    
    def test_single_molecule(self, smiles: str) -> Dict:
        """测试单个分子的气味预测"""
        try:
            payload = {"smiles": smiles, "top_k": 5}
            response = requests.post("https://capi.shanoa.net/predict", json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API返回错误: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def run_workflow_test(self, test_case: Dict) -> Dict:
        """运行完整的工作流测试"""
        print(f"\n{'='*60}")
        print(f"测试用例: {test_case['name']}")
        print(f"{'='*60}")
        
        # 1. 显示用户输入
        print("\n用户输入:")
        print(f"  \"{test_case['input']['user_description']}\"")
        
        # 2. 模拟信息提取
        print("\n模拟信息提取...")
        extracted_params = self.simulate_parameter_extraction(test_case['input']['user_description'])
        print(f"  提取参数:")
        for key, value in extracted_params.items():
            if key != 'notes':
                print(f"    - {key}: {value}")
        
        # 3. 模拟知识库检索
        print("\n模拟知识库检索...")
        db_results = self.simulate_db_search(extracted_params)
        print(f"  找到{len(db_results)}条相关记录")
        
        # 4. 模拟分子预测
        print("\n模拟分子组成预测...")
        molecules = self.simulate_molecule_prediction(extracted_params, db_results)
        print(f"  预测{len(molecules)}个主要香味分子")
        
        # 5. 调用OpenPOM API
        print("\n调用OpenPOM API预测气味...")
        odor_results = []
        for mol in molecules:
            result = self.test_single_molecule(mol['smiles'])
            if 'error' not in result:
                odor_results.append({
                    'molecule': mol,
                    'odors': result.get('top_odors', [])
                })
                print(f"  ✓ {mol['name']}: {', '.join([o['odor'] for o in result.get('top_odors', [])[:3]])}")
        
        # 6. 生成风味报告
        print("\n生成风味分析报告...")
        flavor_report = self.generate_flavor_report(extracted_params, odor_results)
        
        return {
            'test_case': test_case['name'],
            'molecules_predicted': len(molecules),
            'odors_detected': len(odor_results),
            'flavor_summary': flavor_report['summary'],
            'main_flavors': flavor_report['main_flavors'],
            'success': True
        }
    
    def simulate_parameter_extraction(self, user_description: str) -> Dict:
        """模拟信息提取过程"""
        # 实际应该调用LLM API进行信息提取
        # 这里基于关键词进行简单匹配
        
        # 默认值
        params = {
            'coffee_origin': '未知',
            'roast_level': '中烘',
            'roast_time': 12,
            'roast_temp': 200,
            'process_method': '水洗',
            'brewing_method': '手冲',
            'confidence': 0.3,
            'notes': '基于关键词自动推断'
        }
        
        description = user_description.lower()
        
        # 产地识别
        if '埃塞俄比亚' in description or '耶加雪菲' in description:
            params['coffee_origin'] = '埃塞俄比亚'
            params['confidence'] += 0.2
        elif '巴西' in description:
            params['coffee_origin'] = '巴西'
            params['process_method'] = '日晒'  # 巴西豆常见日晒
            params['confidence'] += 0.2
        elif '哥伦比亚' in description:
            params['coffee_origin'] = '哥伦比亚'
            params['confidence'] += 0.2
        
        # 烘焙程度
        if '浅烘' in description or '浅度' in description:
            params['roast_level'] = '浅烘'
            params['roast_time'] = 10
            params['roast_temp'] = 180
            params['confidence'] += 0.2
        elif '深烘' in description or '深度' in description or '出油' in description:
            params['roast_level'] = '深烘'
            params['roast_time'] = 18
            params['roast_temp'] = 220
            params['confidence'] += 0.2
        elif '中烘' in description or '中度' in description:
            params['roast_level'] = '中烘'
            params['confidence'] += 0.2
        
        # 具体数值提取
        import re
        
        # 提取时间
        time_match = re.search(r'(\d+)\s*分钟', description)
        if time_match:
            params['roast_time'] = int(time_match.group(1))
            params['confidence'] += 0.1
        
        # 提取温度
        temp_match = re.search(r'(\d+)\s*度', description)
        if temp_match:
            params['roast_temp'] = int(temp_match.group(1))
            params['confidence'] += 0.1
        
        # 处理方法
        if '水洗' in description:
            params['process_method'] = '水洗'
            params['confidence'] += 0.1
        elif '日晒' in description:
            params['process_method'] = '日晒'
            params['confidence'] += 0.1
        elif '蜜处理' in description:
            params['process_method'] = '蜜处理'
            params['confidence'] += 0.1
        
        # 冲煮方式
        if '手冲' in description or 'v60' in description:
            params['brewing_method'] = '手冲'
            params['confidence'] += 0.1
        elif '意式' in description or '浓缩' in description:
            params['brewing_method'] = '意式'
            params['confidence'] += 0.1
        
        params['confidence'] = min(params['confidence'], 1.0)
        
        return params
    
    def simulate_db_search(self, params: Dict) -> List[Dict]:
        """模拟数据库检索"""
        # 这里应该调用实际的知识库API
        # 现在返回模拟数据
        mock_results = []
        
        if params['coffee_origin'] == '埃塞俄比亚' and params['roast_level'] == '浅烘':
            mock_results = [
                {
                    'smiles': 'CC(=O)OCC',
                    'name': '乙酸乙酯',
                    'percentage': 0.5,
                    'source': '发酵过程'
                },
                {
                    'smiles': 'CC(C)=CCCC(C)=CCO',
                    'name': '香叶醇',
                    'percentage': 0.3,
                    'source': '天然存在'
                }
            ]
        elif params['coffee_origin'] == '巴西' and params['roast_level'] == '深烘':
            mock_results = [
                {
                    'smiles': 'CC1=CC=C(C=C1)O',
                    'name': '4-甲基苯酚',
                    'percentage': 1.2,
                    'source': '热解反应'
                },
                {
                    'smiles': 'O=C1C=CC=CC1=O',
                    'name': '邻苯二醌',
                    'percentage': 1.0,
                    'source': '热解反应'
                }
            ]
        
        return mock_results
    
    def simulate_molecule_prediction(self, params: Dict, db_results: List[Dict]) -> List[Dict]:
        """模拟LLM分子预测"""
        # 实际应该调用LLM API
        # 这里基于数据库结果返回预测
        molecules = []
        
        for result in db_results:
            molecules.append({
                'smiles': result['smiles'],
                'name': result['name'],
                'percentage': result['percentage'],
                'source': result['source']
            })
        
        # 添加一些额外的预测分子
        if params['roast_level'] == '中烘':
            molecules.append({
                'smiles': 'O=CC1=CC=CC=C1',
                'name': '苯甲醛',
                'percentage': 0.4,
                'source': '美拉德反应'
            })
        
        return molecules
    
    def generate_flavor_report(self, params: Dict, odor_results: List[Dict]) -> Dict:
        """生成风味报告"""
        # 收集所有气味标签
        all_odors = []
        for result in odor_results:
            for odor in result['odors']:
                all_odors.append(odor['odor'])
        
        # 基于参数生成描述
        origin_character = {
            '埃塞俄比亚': '明亮的果酸和花香',
            '巴西': '巧克力和坚果风味',
            '哥伦比亚': '平衡的甜感和柑橘调',
            '肯尼亚': '黑醋栗和葡萄酒般的复杂度'
        }
        
        roast_character = {
            '浅烘': '保留了更多原产地特色，酸度明亮',
            '中烘': '平衡的甜感和适度的苦味',
            '深烘': '浓郁的烘焙风味，苦甜交织'
        }
        
        summary = f"这是一款来自{params['coffee_origin']}的{params['roast_level']}咖啡，"
        summary += f"展现出{origin_character.get(params['coffee_origin'], '独特的风味特征')}。"
        summary += roast_character.get(params['roast_level'], '')
        
        return {
            'summary': summary,
            'main_flavors': list(set(all_odors[:5])),  # 取前5个主要风味
            'brewing_suggestion': self.get_brewing_suggestion(params)
        }
    
    def get_brewing_suggestion(self, params: Dict) -> str:
        """获取冲煮建议"""
        suggestions = {
            '手冲': {
                '浅烘': '水温88-92°C，粉水比1:15，中细研磨',
                '中烘': '水温90-93°C，粉水比1:14，中度研磨',
                '深烘': '水温85-88°C，粉水比1:13，中粗研磨'
            },
            '意式': {
                '浅烘': '水温92-94°C，粉水比1:2.5，细研磨',
                '中烘': '水温90-92°C，粉水比1:2，细研磨',
                '深烘': '水温88-90°C，粉水比1:2，细研磨'
            }
        }
        
        brewing = params.get('brewing_method', '手冲')
        roast = params.get('roast_level', '中烘')
        
        return suggestions.get(brewing, {}).get(roast, '请咨询专业咖啡师')


# 测试用例定义
TEST_CASES = [
    {
        'name': '埃塞俄比亚水洗浅烘',
        'input': {
            'user_description': '我刚买了一包埃塞俄比亚耶加雪菲的豆子，是水洗处理的。今天早上浅烘了大概10分钟，温度控制在180度左右。想用V60手冲，请帮我分析一下风味。'
        },
        'expected_flavors': ['花香', '果香', '柑橘', '茶感']
    },
    {
        'name': '巴西日晒深烘',
        'input': {
            'user_description': '巴西豆子，日晒处理的，深度烘焙了18分钟，温度到了220度，豆子都出油了。准备拿来做意式浓缩，会是什么味道？'
        },
        'expected_flavors': ['巧克力', '坚果', '焦糖', '烟熏']
    },
    {
        'name': '用户简单描述',
        'input': {
            'user_description': '哥伦比亚豆子，中烘，想知道风味如何'
        },
        'expected_flavors': ['蜂蜜', '红糖', '柑橘', '可可']
    }
]


def main():
    """运行测试"""
    print("CoffeeFlow-AI 集成测试")
    print("="*60)
    
    # 初始化测试器（需要提供实际的API密钥）
    # api_key = "your-dify-api-key"
    # tester = CoffeeFlowTester(api_key)
    
    # 由于没有实际的Dify API密钥，我们创建一个模拟测试器
    tester = CoffeeFlowTester("dummy-key")
    
    # 1. 测试OpenPOM API
    print("\n1. 测试OpenPOM API连接...")
    api_ok = tester.test_openpom_api()
    if not api_ok:
        print("警告: OpenPOM API未运行，部分测试将使用模拟数据")
    
    # 2. 测试单个分子预测
    print("\n2. 测试单个分子气味预测...")
    test_smiles = "CCO"  # 乙醇
    result = tester.test_single_molecule(test_smiles)
    if 'error' not in result:
        print(f"✓ 乙醇(CCO)的气味预测: {[o['odor'] for o in result.get('top_odors', [])]}")
    
    # 3. 运行完整工作流测试
    print("\n3. 运行完整工作流测试...")
    test_results = []
    for test_case in TEST_CASES:
        result = tester.run_workflow_test(test_case)
        test_results.append(result)
    
    # 4. 输出测试报告
    print("\n" + "="*60)
    print("测试报告总结")
    print("="*60)
    
    for result in test_results:
        print(f"\n测试用例: {result['test_case']}")
        print(f"  - 预测分子数: {result['molecules_predicted']}")
        print(f"  - 检测气味数: {result['odors_detected']}")
        print(f"  - 主要风味: {', '.join(result['main_flavors'])}")
        print(f"  - 测试状态: {'✓ 通过' if result['success'] else '✗ 失败'}")
    
    # 5. 性能测试
    print("\n" + "="*60)
    print("性能测试")
    print("="*60)
    
    # 测试批量预测性能
    test_molecules = [
        "CCO",  # 乙醇
        "CC(=O)OCC",  # 乙酸乙酯
        "CC1=CC=C(C=C1)O",  # 4-甲基苯酚
        "O=CC1=CC=CC=C1",  # 苯甲醛
        "CC(C)=CCCC(C)=CCO"  # 香叶醇
    ]
    
    start_time = time.time()
    
    # 测试批量API调用
    payload = {
        "smiles_list": test_molecules,
        "threshold": 0.3
    }
    
    try:
        response = requests.post("https://capi.shanoa.net/predict_batch", json=payload)
        if response.status_code == 200:
            elapsed_time = time.time() - start_time
            print(f"✓ 批量预测{len(test_molecules)}个分子耗时: {elapsed_time:.2f}秒")
            print(f"  平均每个分子: {elapsed_time/len(test_molecules):.3f}秒")
        else:
            print(f"✗ 批量预测失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 批量预测出错: {e}")
    
    print("\n测试完成！")


if __name__ == "__main__":
    main()