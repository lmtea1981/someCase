import pandas as pd
import re
from typing import List, Dict, Any

class DocumentLoader:
    """
    通用文档加载工具，支持多类型文档解析
    核心支持Excel（XLS/XLSX）格式
    """
    
    def __init__(self):
        self.supported_formats = {
            'xls': self._load_excel,
            'xlsx': self._load_excel
        }
    
    def load_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载文档并返回结构化数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Dict[str, Any]]: 结构化数据列表
        """
        file_extension = file_path.split('.')[-1].lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {file_extension}")
        
        return self.supported_formats[file_extension](file_path)
    
    def _load_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载Excel文件
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            List[Dict[str, Any]]: 结构化数据列表
        """
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 过滤空行
        df = df.dropna(how="all")
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        # 转换为字典列表
        data_list = df.to_dict('records')
        
        # 过滤有效数据（用例ID和标题非空）
        valid_data = []
        processed_ids = set()
        
        for item in data_list:
            # 提取用例ID和标题（适配testdata_1.xlsx格式）
            case_id = item.get('ID', '') or item.get('用例ID', '') or item.get('Case ID', '')
            case_title = item.get('*用例标题', '') or item.get('用例标题', '') or item.get('Case Title', '') or item.get('标题', '')
            
            # 验证用例ID和标题是否有效
            if case_id and case_title:
                # 去重
                if case_id not in processed_ids:
                    processed_ids.add(case_id)
                    valid_data.append(item)
        
        print(f"加载Excel文件: {file_path}")
        print(f"原始数据行数: {len(data_list)}")
        print(f"有效数据行数: {len(valid_data)}")
        
        return valid_data
    
    def preprocess_text(self, text: str) -> str:
        """
        文本预处理
        
        Args:
            text: 原始文本
            
        Returns:
            str: 预处理后的文本
        """
        if not isinstance(text, str):
            text = str(text)
        
        # 清理特殊字符
        text = re.sub(r'[\r\n]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^一-龥a-zA-Z0-9\s，。！？,.!?;；:：、]', '', text)
        
        # 截断超长文本
        text = text[:2000]
        
        return text.strip()
    
    def process_case_data(self, case_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理用例数据，进行文本预处理
        
        Args:
            case_data: 原始用例数据
            
        Returns:
            List[Dict[str, Any]]: 处理后的用例数据
        """
        processed_data = []
        
        for case in case_data:
            processed_case = {}
            for key, value in case.items():
                if isinstance(value, str):
                    processed_case[key] = self.preprocess_text(value)
                else:
                    processed_case[key] = value
            processed_data.append(processed_case)
        
        return processed_data
