#!/usr/bin/env python3
"""
分子气味预测器 - CPU专用服务器版本
专门为服务器部署优化，强制使用CPU推理，提升部署稳定性
"""

import deepchem as dc
from openpom.feat.graph_featurizer import GraphFeaturizer, GraphConvConstants
from openpom.utils.data_utils import get_class_imbalance_ratio
from openpom.models.mpnn_pom import MPNNPOMModel
import torch
import numpy as np
import pandas as pd
import os
import warnings

class OdorPredictorCPU:
    def __init__(self, model_dir_prefix=None, n_models=10, use_cpu_only=True):
        """
        初始化气味预测器 - CPU专用版本
        
        Args:
            model_dir_prefix: 模型目录前缀，如果为None则自动搜索
            n_models: 集成模型数量
            use_cpu_only: 强制只使用CPU，默认True
        """
        # 强制使用CPU
        if use_cpu_only:
            # 设置环境变量，禁用CUDA
            os.environ['CUDA_VISIBLE_DEVICES'] = ''
            # 确保PyTorch使用CPU
            torch.set_default_device('cpu')
            print("✓ 强制使用CPU模式")
        
        self.n_models = n_models
        self.featurizer = GraphFeaturizer()
        self.use_cpu_only = use_cpu_only
        
        # 138个气味任务 (完整版本)
        self.tasks = [
            'alcoholic', 'aldehydic', 'alliaceous', 'almond', 'amber', 'animal',
            'anisic', 'apple', 'apricot', 'aromatic', 'balsamic', 'banana', 'beefy',
            'bergamot', 'berry', 'bitter', 'black currant', 'brandy', 'burnt',
            'buttery', 'cabbage', 'camphoreous', 'caramellic', 'cedar', 'celery',
            'chamomile', 'cheesy', 'cherry', 'chocolate', 'cinnamon', 'citrus', 'clean',
            'clove', 'cocoa', 'coconut', 'coffee', 'cognac', 'cooked', 'cooling',
            'cortex', 'coumarinic', 'creamy', 'cucumber', 'dairy', 'dry', 'earthy',
            'ethereal', 'fatty', 'fermented', 'fishy', 'floral', 'fresh', 'fruit skin',
            'fruity', 'garlic', 'gassy', 'geranium', 'grape', 'grapefruit', 'grassy',
            'green', 'hawthorn', 'hay', 'hazelnut', 'herbal', 'honey', 'hyacinth',
            'jasmin', 'juicy', 'ketonic', 'lactonic', 'lavender', 'leafy', 'leathery',
            'lemon', 'lily', 'malty', 'meaty', 'medicinal', 'melon', 'metallic',
            'milky', 'mint', 'muguet', 'mushroom', 'musk', 'musty', 'natural', 'nutty',
            'odorless', 'oily', 'onion', 'orange', 'orangeflower', 'orris', 'ozone',
            'peach', 'pear', 'phenolic', 'pine', 'pineapple', 'plum', 'popcorn',
            'potato', 'powdery', 'pungent', 'radish', 'raspberry', 'ripe', 'roasted',
            'rose', 'rummy', 'sandalwood', 'savory', 'sharp', 'smoky', 'soapy',
            'solvent', 'sour', 'spicy', 'strawberry', 'sulfurous', 'sweaty', 'sweet',
            'tea', 'terpenic', 'tobacco', 'tomato', 'tropical', 'vanilla', 'vegetable',
            'vetiver', 'violet', 'warm', 'waxy', 'weedy', 'winey', 'woody'
        ]
        
        self.n_tasks = len(self.tasks)
        self.models = []
        
        # 自动搜索模型目录
        if model_dir_prefix is None:
            self.model_dir_prefix = self._find_model_directory()
        else:
            self.model_dir_prefix = model_dir_prefix
        
        # 从原始训练集加载类别不平衡比例（这里用默认值，如果有保存的话可以加载）
        self.train_ratios = [1.0] * self.n_tasks  # 占位符，建议保存真实的train_ratios
        
        print(f"使用模型目录: {self.model_dir_prefix}")
        print(f"设备信息: {'CPU Only' if use_cpu_only else 'Auto-detect'}")
        print(f"CUDA可用: {torch.cuda.is_available() and not use_cpu_only}")
        
        self._load_models()
    
    def _find_model_directory(self):
        """自动搜索模型目录"""
        possible_paths = [
            './ensemble_models/experiments_',
            '../ensemble_models/experiments_',
            './examples/ensemble_models/experiments_',
            '../examples/ensemble_models/experiments_',
            '../../ensemble_models/experiments_',
            '/opt/models/ensemble_models/experiments_',  # 服务器常用路径
            '/app/models/ensemble_models/experiments_',   # Docker容器常用路径
        ]
        
        for path in possible_paths:
            test_path = f"{path}1/checkpoint2.pt"
            if os.path.exists(test_path):
                print(f"找到模型文件: {test_path}")
                return path
        
        # 如果都找不到，返回默认路径并给出提示
        print("警告: 未找到模型文件，使用默认路径")
        return './ensemble_models/experiments_'
    
    def _load_models(self):
        """加载所有集成模型 - CPU优化版本"""
        print(f"正在加载{self.n_models}个集成模型（CPU模式）...")
        
        # 禁用不必要的警告
        warnings.filterwarnings('ignore', category=UserWarning)
        
        learning_rate = dc.models.optimizers.ExponentialDecay(
            initial_rate=0.001, decay_rate=0.5, decay_steps=32*20, staircase=True
        )
        
        successfully_loaded = 0
        for i in range(self.n_models):
            print(f"加载模型 {i+1}/{self.n_models}")
            
            # 检查模型文件是否存在
            checkpoint_path = f"{self.model_dir_prefix}{i+1}/checkpoint2.pt"
            if not os.path.exists(checkpoint_path):
                print(f"警告: 模型文件不存在: {checkpoint_path}")
                continue
            
            try:
                model = MPNNPOMModel(
                    n_tasks=self.n_tasks,
                    batch_size=64,  # 减少batch_size以节省内存
                    learning_rate=learning_rate,
                    class_imbalance_ratio=self.train_ratios,
                    loss_aggr_type='sum',
                    node_out_feats=100,
                    edge_hidden_feats=75,
                    edge_out_feats=100,
                    num_step_message_passing=5,
                    mpnn_residual=True,
                    message_aggregator_type='sum',
                    mode='classification',
                    number_atom_features=GraphConvConstants.ATOM_FDIM,
                    number_bond_features=GraphConvConstants.BOND_FDIM,
                    n_classes=1,
                    readout_type='set2set',
                    num_step_set2set=3,
                    num_layer_set2set=2,
                    ffn_hidden_list=[392, 392],
                    ffn_embeddings=256,
                    ffn_activation='relu',
                    ffn_dropout_p=0.12,
                    ffn_dropout_at_input_no_act=False,
                    weight_decay=1e-5,
                    self_loop=False,
                    optimizer_name='adam',
                    log_frequency=32,
                    model_dir=f'{self.model_dir_prefix}{i+1}',
                    device_name='cpu'  # 强制使用CPU
                )
                
                # 恢复模型权重
                model.restore(checkpoint_path)
                
                # 设置模型为评估模式以提升推理速度
                if hasattr(model.model, 'eval'):
                    model.model.eval()
                
                self.models.append(model)
                successfully_loaded += 1
                print(f"  ✓ 模型 {i+1} 加载成功（CPU模式）")
                
            except Exception as e:
                print(f"  ✗ 模型 {i+1} 加载失败: {e}")
                continue
        
        if successfully_loaded == 0:
            raise RuntimeError("没有成功加载任何模型！请检查模型文件路径。")
        
        print(f"成功加载 {successfully_loaded}/{self.n_models} 个模型")
        self.n_models = successfully_loaded  # 更新实际可用的模型数量
        
        # 进行一次小的预热预测以优化后续推理速度
        try:
            print("正在预热模型...")
            self._warmup_models()
            print("✓ 模型预热完成")
        except Exception as e:
            print(f"模型预热失败（可忽略）: {e}")
    
    def _warmup_models(self):
        """预热模型以提升后续推理速度"""
        warmup_smiles = 'CCO'  # 简单的乙醇分子
        try:
            with torch.no_grad():  # 禁用梯度计算以节省内存
                self.get_top_odors(warmup_smiles, top_k=1)
        except Exception:
            pass  # 预热失败不影响正常使用
    
    def predict_smiles(self, smiles_list, threshold=0.5, batch_size=None):
        """
        预测SMILES列表的气味 - CPU优化版本
        
        Args:
            smiles_list: SMILES字符串列表
            threshold: 预测阈值，大于该值认为具有对应气味
            batch_size: 批处理大小，None时自动设置
            
        Returns:
            DataFrame: 包含预测结果的数据框
        """
        if isinstance(smiles_list, str):
            smiles_list = [smiles_list]
        
        print(f"正在预测{len(smiles_list)}个分子的气味（CPU模式）...")
        
        # 自动设置batch_size以优化CPU性能
        if batch_size is None:
            batch_size = min(32, len(smiles_list))  # CPU模式使用较小的batch_size
        
        # 创建临时数据集
        temp_data = pd.DataFrame({
            'nonStereoSMILES': smiles_list,
            **{task: [0] * len(smiles_list) for task in self.tasks}  # 占位符标签
        })
        temp_file = 'temp_predict_cpu.csv'
        temp_data.to_csv(temp_file, index=False)
        
        try:
            # 使用featurizer处理数据
            loader = dc.data.CSVLoader(
                tasks=self.tasks,
                feature_field='nonStereoSMILES',
                featurizer=self.featurizer
            )
            dataset = loader.create_dataset(inputs=[temp_file])
            
            # 获取每个模型的预测（使用torch.no_grad()优化内存）
            all_predictions = []
            with torch.no_grad():  # 禁用梯度计算以节省内存和提升速度
                for i, model in enumerate(self.models):
                    print(f"使用模型 {i+1}/{len(self.models)} 进行预测")
                    preds = model.predict(dataset)
                    all_predictions.append(preds)
            
            # 计算集成平均
            ensemble_predictions = np.mean(np.array(all_predictions), axis=0)
            
            # 创建结果DataFrame
            results = pd.DataFrame({
                'SMILES': smiles_list,
                **{task: ensemble_predictions[:, i] for i, task in enumerate(self.tasks)}
            })
            
            # 添加二进制预测（基于阈值）
            binary_results = pd.DataFrame({
                'SMILES': smiles_list,
                **{f'{task}_binary': (ensemble_predictions[:, i] > threshold).astype(int) 
                   for i, task in enumerate(self.tasks)}
            })
            
            return results, binary_results
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def get_top_odors(self, smiles, top_k=10):
        """
        获取分子最可能的前k个气味 - CPU优化版本
        
        Args:
            smiles: 单个SMILES字符串
            top_k: 返回前k个最可能的气味
            
        Returns:
            DataFrame: 包含top-k气味及其概率的数据框
        """
        with torch.no_grad():  # 禁用梯度计算
            results, _ = self.predict_smiles([smiles])
            
            # 获取除SMILES外的所有预测分数
            scores = results.iloc[0, 1:].values
            task_names = self.tasks
            
            # 排序并获取top-k
            sorted_indices = np.argsort(scores)[::-1][:top_k]
            
            top_odors = pd.DataFrame({
                'odor': [task_names[i] for i in sorted_indices],
                'probability': [scores[i] for i in sorted_indices]
            })
            
            return top_odors
    
    def get_system_info(self):
        """获取系统信息，用于部署监控"""
        import psutil
        import platform
        
        info = {
            'platform': platform.system(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'python_version': platform.python_version(),
            'torch_version': torch.__version__,
            'device_mode': 'CPU Only' if self.use_cpu_only else 'Auto',
            'cuda_available': torch.cuda.is_available() and not self.use_cpu_only,
            'models_loaded': self.n_models
        }
        return info

def main():
    """服务器部署示例"""
    try:
        # 初始化CPU专用预测器
        print("=== 分子气味预测器 - 服务器CPU版本 ===")
        predictor = OdorPredictorCPU(use_cpu_only=True)
        
        # 显示系统信息
        print("\n系统信息:")
        sys_info = predictor.get_system_info()
        for key, value in sys_info.items():
            print(f"  {key}: {value}")
        
        # 示例分子SMILES
        example_smiles = [
            'CCO',  # 乙醇
            'CC(=O)OCC',  # 乙酸乙酯
            'c1ccc(cc1)O',  # 苯酚
        ]
        
        print(f"\n示例预测（{len(example_smiles)}个分子）:")
        
        # 预测气味
        results, binary_results = predictor.predict_smiles(example_smiles)
        
        # 保存结果
        results.to_csv('cpu_odor_predictions.csv', index=False)
        binary_results.to_csv('cpu_odor_predictions_binary.csv', index=False)
        
        print("\n✓ 预测完成！结果已保存到:")
        print("- cpu_odor_predictions.csv (概率分数)")
        print("- cpu_odor_predictions_binary.csv (二进制预测)")
        
        # 显示每个分子的top-3气味
        print("\n各分子最可能的3种气味:")
        for smiles in example_smiles:
            top_odors = predictor.get_top_odors(smiles, top_k=3)
            print(f"\n{smiles}:")
            for _, row in top_odors.iterrows():
                print(f"  {row['odor']:15s}: {row['probability']:.3f}")
        
        print(f"\n✓ 服务器部署测试完成！模型可在CPU环境下正常运行")
                
    except Exception as e:
        print(f"运行出错: {e}")
        print("\n故障排除:")
        print("1. 检查模型文件是否存在")
        print("2. 确认依赖包安装正确")
        print("3. 检查CPU内存是否充足（建议至少8GB）")

if __name__ == "__main__":
    main() 