# -*- coding: utf-8 -*-

import csv
import os

class ParameterLoader:
    @staticmethod
    def load_parameters(file_path):
        """加载参数文件（支持CSV和TXT）"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"参数文件不存在: {file_path}")

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == '.csv':
            return ParameterLoader._load_csv(file_path)
        elif ext in ['.txt', '.text']:
            return ParameterLoader._load_txt(file_path)
        else:
            raise ValueError(f"不支持的参数文件格式: {ext}")

    @staticmethod
    def _load_csv(file_path):
        """加载CSV文件"""
        params = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                params.append({k: v for k, v in row.items()})
        return params

    @staticmethod
    def _load_txt(file_path, delimiter=','):
        """加载TXT文件"""
        params = []
        with open(file_path, 'r', encoding='utf-8') as f:
            # 读取标题行
            headers = f.readline().strip().split(delimiter)

            for line in f:
                values = line.strip().split(delimiter)
                param_dict = {}
                for i, header in enumerate(headers):
                    if i < len(values):
                        param_dict[header] = values[i]
                    else:
                        param_dict[header] = None
                params.append(param_dict)
        return params
