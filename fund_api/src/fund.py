import requests
import json
import pandas as pd
import os
from datetime import datetime
from src.utils import get_data_dir

class Fund:
    def __init__(self, code, name, enabled=1):
        self.code = code
        self.name = name
        self.enabled = enabled
        self.url = f"http://fundgz.1234567.com.cn/js/{code}.js"
        self.data = {}
        self.previous_data = {}
    
    def get_realtime_data(self):
        """获取实时基金估值数据"""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            
            # 解析JSONP格式响应
            data_str = response.text
            data_str = data_str.replace('jsonpgz(', '').replace(');', '')
            self.data = json.loads(data_str)
            return self.data
        except Exception as e:
            print(f"获取基金 {self.name}({self.code}) 数据失败: {e}")
            return None
    
    def save_to_csv(self):
        """保存数据到CSV文件"""
        if not self.data:
            return False
        
        data_dir = get_data_dir()
        csv_file = os.path.join(data_dir, f"{self.name}({self.code}).csv")
        
        # 准备数据
        fund_data = {
            'fundcode': [self.data.get('fundcode')],
            'name': [self.data.get('name')],
            'jzrq': [self.data.get('jzrq')],
            'dwjz': [self.data.get('dwjz')],
            'gsz': [self.data.get('gsz')],
            'gszzl': [self.data.get('gszzl')],
            'gztime': [self.data.get('gztime')]
        }
        
        df = pd.DataFrame(fund_data)
        
        # 检查文件是否存在，不存在则写入表头
        if not os.path.exists(csv_file):
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8-sig')
        
        return True
    
    def print_change(self):
        """打印基金变化情况"""
        if not self.data:
            return
        
        # 只有当enabled为1时才打印输出
        if self.enabled == 1:
            print(f"=== 基金: {self.name}({self.code}) ===")
            print(f"前一天净值: {self.data.get('dwjz')}")
            print(f"当前估值: {self.data.get('gsz')}")
            print(f"涨跌幅度: {self.data.get('gszzl')}%")
            print(f"估值时间: {self.data.get('gztime')}")
            print()
    
    def update(self):
        """更新基金数据"""
        self.previous_data = self.data.copy()
        self.get_realtime_data()
        if self.data:
            self.save_to_csv()
            self.print_change()
        return self.data