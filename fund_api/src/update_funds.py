import os
import sys
import yaml
import requests
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils import get_config_dir

def update_funds_info():
    """更新基金信息，自动补全基金名称"""
    config_dir = get_config_dir()
    funds_file = os.path.join(config_dir, 'funds.yaml')
    
    # 读取基金配置
    with open(funds_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    funds = config.get('funds', [])
    
    # 按code去重处理
    unique_funds = []
    seen_codes = set()
    for fund in funds:
        code = str(fund.get('code'))
        if code not in seen_codes:
            seen_codes.add(code)
            unique_funds.append(fund)
    
    funds = unique_funds
    updated_funds = []
    
    print("开始更新基金信息...")
    
    for fund_info in funds:
        code = fund_info.get('code')
        # 确保基金代码为字符串类型
        code = str(code)
        name = fund_info.get('name')
        
        # 如果没有基金名称，则通过API获取
        if not name:
            try:
                url = f"http://fundgz.1234567.com.cn/js/{code}.js"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # 解析JSONP格式响应
                data_str = response.text
                data_str = data_str.replace('jsonpgz(', '').replace(');', '')
                fund_data = json.loads(data_str)
                
                # 获取基金名称
                name = fund_data.get('name', '')
                print(f"获取基金 {code} 名称成功: {name}")
            except Exception as e:
                print(f"获取基金 {code} 名称失败: {e}")
                name = ''
        
        # 保留enabled字段，默认值改为0
        enabled = fund_info.get('enabled', 0)
        updated_funds.append({
            'code': code,
            'name': name,
            'enabled': enabled
        })
    
    # 更新配置文件
    config['funds'] = updated_funds
    
    # 确保基金代码以字符串格式保存
    for fund_info in config['funds']:
        fund_info['code'] = str(fund_info['code'])
    
    # 按enabled降序，name升序排序
    config['funds'].sort(key=lambda x: (-x.get('enabled', 1), x.get('name', '')))
    
    # 直接写入YAML格式，确保正确保存
    yaml_content = "funds:\n"
    for fund in config['funds']:
        yaml_content += f"  - code: \"{fund['code']}\"\n"
        yaml_content += f"    name: \"{fund['name']}\"\n"
        yaml_content += f"    enabled: {fund.get('enabled', 1)}\n"
    
    # 确保目录存在
    os.makedirs(os.path.dirname(funds_file), exist_ok=True)
    
    # 写入文件
    try:
        # 使用utf-8-sig编码，确保中文正确显示
        with open(funds_file, 'w', encoding='utf-8-sig') as f:
            f.write(yaml_content)
        print("基金信息更新完成！")
    except Exception as e:
        print(f"写入文件失败: {e}")

if __name__ == "__main__":
    update_funds_info()