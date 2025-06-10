#!/usr/bin/env python3
"""
分子气味预测 API 服务器
提供HTTP REST API接口，专为服务器部署设计
"""

from flask import Flask, request, jsonify
from predict_odor_cpu import OdorPredictorCPU
import os
import logging
import time
from functools import wraps

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 全局预测器实例
predictor = None

def init_predictor():
    """初始化预测器"""
    global predictor
    try:
        logger.info("正在初始化气味预测器...")
        predictor = OdorPredictorCPU(use_cpu_only=True)
        logger.info("预测器初始化完成")
        return True
    except Exception as e:
        logger.error(f"预测器初始化失败: {e}")
        return False

def require_predictor(f):
    """装饰器：确保预测器已初始化"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if predictor is None:
            return jsonify({
                'error': 'Predictor not initialized',
                'message': '预测器未初始化，请重启服务'
            }), 500
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
def health_check():
    """健康检查接口"""
    status = 'healthy' if predictor is not None else 'unhealthy'
    info = {
        'status': status,
        'service': 'Odor Prediction API',
        'version': '1.0.0',
        'cpu_only': True
    }
    
    if predictor is not None:
        try:
            sys_info = predictor.get_system_info()
            info.update(sys_info)
        except Exception as e:
            logger.warning(f"获取系统信息失败: {e}")
    
    return jsonify(info)

@app.route('/predict', methods=['POST'])
@require_predictor
def predict_single():
    """预测单个分子的气味"""
    try:
        data = request.get_json()
        
        if not data or 'smiles' not in data:
            return jsonify({
                'error': 'Missing SMILES',
                'message': '请提供SMILES字符串'
            }), 400
        
        smiles = data['smiles']
        top_k = data.get('top_k', 10)
        
        if not isinstance(smiles, str) or not smiles.strip():
            return jsonify({
                'error': 'Invalid SMILES',
                'message': 'SMILES必须是非空字符串'
            }), 400
        
        if not isinstance(top_k, int) or top_k <= 0:
            return jsonify({
                'error': 'Invalid top_k',
                'message': 'top_k必须是正整数'
            }), 400
        
        start_time = time.time()
        top_odors = predictor.get_top_odors(smiles, top_k=min(top_k, 50))
        prediction_time = time.time() - start_time
        
        result = {
            'smiles': smiles,
            'top_odors': top_odors.to_dict('records'),
            'prediction_time_seconds': round(prediction_time, 3)
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"预测失败: {e}")
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500

@app.route('/predict_batch', methods=['POST'])
@require_predictor
def predict_batch():
    """批量预测多个分子的气味"""
    try:
        data = request.get_json()
        
        if not data or 'smiles_list' not in data:
            return jsonify({
                'error': 'Missing SMILES list',
                'message': '请提供SMILES字符串列表'
            }), 400
        
        smiles_list = data['smiles_list']
        threshold = data.get('threshold', 0.5)
        
        if not isinstance(smiles_list, list) or len(smiles_list) == 0:
            return jsonify({
                'error': 'Invalid SMILES list',
                'message': 'smiles_list必须是非空列表'
            }), 400
        
        if len(smiles_list) > 100:
            return jsonify({
                'error': 'Too many molecules',
                'message': '单次最多预测100个分子'
            }), 400
        
        if not isinstance(threshold, (int, float)) or not (0 <= threshold <= 1):
            return jsonify({
                'error': 'Invalid threshold',
                'message': 'threshold必须在0-1之间'
            }), 400
        
        start_time = time.time()
        results, binary_results = predictor.predict_smiles(smiles_list, threshold=threshold)
        prediction_time = time.time() - start_time
        
        result = {
            'molecule_count': len(smiles_list),
            'threshold': threshold,
            'predictions': results.to_dict('records'),
            'binary_predictions': binary_results.to_dict('records'),
            'prediction_time_seconds': round(prediction_time, 3)
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"批量预测失败: {e}")
        return jsonify({
            'error': 'Batch prediction failed',
            'message': str(e)
        }), 500

@app.route('/tasks', methods=['GET'])
@require_predictor
def get_tasks():
    """获取所有支持的气味任务"""
    return jsonify({
        'tasks': predictor.tasks,
        'task_count': predictor.n_tasks
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'API接口不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': '服务器内部错误'
    }), 500

def main():
    """启动服务器"""
    print("=== 分子气味预测 API 服务器 ===")
    
    # 初始化预测器
    if not init_predictor():
        print("❌ 预测器初始化失败，服务器启动中止")
        return
    
    print("✓ 预测器初始化成功")
    
    # 服务器配置
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"\n服务器配置:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Debug: {debug}")
    
    print(f"\nAPI接口:")
    print(f"  健康检查: http://{host}:{port}/")
    print(f"  单分子预测: http://{host}:{port}/predict")
    print(f"  批量预测: http://{host}:{port}/predict_batch")
    print(f"  气味任务: http://{host}:{port}/tasks")
    
    print(f"\n使用示例:")
    print(f"  curl -X POST http://{host}:{port}/predict \\")
    print(f"       -H 'Content-Type: application/json' \\")
    print(f"       -d '{{\"smiles\": \"CCO\", \"top_k\": 5}}'")
    
    print(f"\n✓ 启动服务器...")
    
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    except KeyboardInterrupt:
        print("\n✓ 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")

if __name__ == "__main__":
    main() 