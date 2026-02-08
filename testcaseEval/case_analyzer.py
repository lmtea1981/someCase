import os
import sqlite3
from typing import List, Dict, Any
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

from config import *
from tool import DocumentLoader

class CaseAnalyzer:
    def __init__(self):
        # 初始化文档加载器
        self.loader = DocumentLoader()
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=SEPARATORS
        )
        
        # 初始化嵌入模型
        self.embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL
        )
        
        # 初始化LLM（带流式输出）
        self.llm = Ollama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        
        # 初始化数据库
        self.db_conn = sqlite3.connect('test_cases.db')
        self._create_table()
    
    def _create_table(self):
        """
        创建数据库表
        """
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                test_method TEXT,
                content TEXT,
                embedding BLOB
            )
        ''')
        self.db_conn.commit()
    
    def load_case_library(self) -> List[Dict[str, Any]]:
        """
        加载测试用例库
        """
        print("正在加载测试用例库...")
        case_data = self.loader.load_document(CASE_LIBRARY_PATH)
        processed_data = self.loader.process_case_data(case_data)
        return processed_data
    
    def analyze_test_method(self, case_content: str) -> str:
        """
        分析测试用例的设计方法
        """
        # 检查测试用例内容是否过于简单（占位符文本）
        simple_indicators = ["测试用例标题_", "执行步骤", "预期结果", "测试用例描述_"]
        is_simple = any(indicator in case_content for indicator in simple_indicators)
        
        # 如果是简单占位符，直接返回默认的测试设计方法
        if is_simple:
            return "场景法"
        
        # 定义提示模板，优化归类能力
        prompt_template = PromptTemplate(
            input_variables=["case_content", "test_methods"],
            template="""你是一位经验丰富的测试工程师，擅长分析测试用例的设计方法。请仔细分析以下测试用例内容，判断它使用了哪种或哪些测试设计方法。

测试设计方法列表及说明：
1. 等价类划分法：将输入数据划分为若干等价类，从每个等价类中选取代表性数据进行测试
2. 边界值分析法：针对输入输出的边界值进行测试，如最大值、最小值、临界值等
3. 异常分析法：针对异常情况进行测试，如错误输入、异常流程等
4. 场景法：模拟用户实际使用场景，测试完整的业务流程
5. 因果图法：通过分析输入条件与输出结果之间的因果关系来设计测试用例
6. 正交试验法：使用正交表来设计全面且高效的测试用例
7. 判定表法：使用判定表来描述输入条件与输出结果之间的关系

测试用例内容：{case_content}

请严格从测试设计方法列表中选择，多个方法用逗号分隔。如果确实无法确定，请返回'场景法'（默认）。

仅返回测试设计方法，不要包含其他内容或解释。
"""
        )
        
        # 生成提示
        prompt = prompt_template.format(
            case_content=case_content,
            test_methods=", ".join(TEST_METHODS)
        )
        
        # 调用LLM分析
        result = self.llm.invoke(prompt)
        
        # 处理结果
        result = result.strip()
        if not result or result == "未知":
            return "场景法"  # 默认使用场景法
        
        # 验证结果是否在允许的方法列表中
        valid_methods = []
        for method in result.split("，"):
            method = method.strip()
            if method in TEST_METHODS or method == "未知":
                valid_methods.append(method)
        
        return "，".join(valid_methods) if valid_methods else "场景法"
    
    def batch_analyze_cases(self):
        """
        批量分析测试用例
        """
        # 加载用例库
        case_data = self.load_case_library()
        
        print(f"\n开始批量分析测试用例，共 {len(case_data)} 个用例...")
        
        # 处理用例
        for i, case in enumerate(case_data):
            # 实时输出进度
            print(f"\n[{i+1}/{len(case_data)}] 正在分析用例...")
            
            # 提取用例信息（适配testdata_1.xlsx格式）
            case_id = case.get('ID', '') or case.get('用例ID', '') or case.get('Case ID', '')
            case_title = case.get('*用例标题', '') or case.get('用例标题', '') or case.get('Case Title', '') or case.get('标题', '')
            case_desc = case.get('描述', '') or case.get('用例描述', '') or case.get('Description', '')
            case_steps = case.get('*测试步骤', '') or case.get('测试步骤', '') or case.get('Steps', '') or case.get('步骤', '')
            case_expected = case.get('*预期结果', '') or case.get('预期结果', '') or case.get('Expected Result', '') or case.get('预期', '')
            
            # 合并用例内容
            case_content = f"标题：{case_title}\n描述：{case_desc}\n步骤：{case_steps}\n预期结果：{case_expected}"
            case_content = self.loader.preprocess_text(case_content)
            
            print(f"用例ID: {case_id}")
            print(f"用例标题: {case_title}")
            print(f"正在分析设计方法...", end=" ")
            
            # 分析测试设计方法（流式输出）
            test_method = self.analyze_test_method(case_content)
            print(f"✓ 完成")
            
            # 存储到数据库
            cursor = self.db_conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO test_cases (id, title, description, test_method, content) VALUES (?, ?, ?, ?, ?)",
                (case_id, case_title, case_desc, test_method, case_content)
            )
            self.db_conn.commit()
            
            # 实时输出分析结果
            print(f"设计方法: {test_method}")
            print("-" * 50)
        
        print(f"\n所有用例分析完成！共分析 {len(case_data)} 个用例")
        print("\n批量分析任务完成！")
        
        # 关闭数据库连接
        self.db_conn.close()
        
        print("\n所有用例分析完成！")

if __name__ == "__main__":
    analyzer = CaseAnalyzer()
    analyzer.batch_analyze_cases()
