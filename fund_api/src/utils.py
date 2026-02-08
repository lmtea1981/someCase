import yaml
import os

def load_config(config_file):
    """加载YAML配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_funds_config(funds_file):
    """加载基金配置文件"""
    with open(funds_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        return config.get('funds', [])

def get_data_dir():
    """获取数据存储目录"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def get_config_dir():
    """获取配置目录"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')