import sqlite3
from typing import List, Dict, Any
from langchain_community.llms import Ollama
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

from config import *

class CaseRetriever:
    def __init__(self):
        # 初始化LLM（带流式输出）
        self.llm = Ollama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        
        # 初始化数据库连接
        self.db_conn = sqlite3.connect('test_cases.db')
    
    def get_user_requirement(self) -> str:
        """
        获取用户测试目的
        """
        print("\n欢迎使用测试用例智能检索系统！")
        print("请输入您的测试目的（例如：UAT测试、功能测试、回归测试等）：")
        user_input = input("\n您的测试目的：")
        return user_input.strip()
    
    def analyze_matching_methods(self, user_requirement: str) -> List[str]:
        """
        分析用户需求匹配的测试设计方法
        """
        # 定义提示模板
        prompt_template = PromptTemplate(
            input_variables=["user_requirement", "test_methods"],
            template="""你是一位专业的测试工程师，请根据用户的测试目的，分析需要使用哪些测试设计方法。

测试设计方法列表：{test_methods}

用户测试目的：{user_requirement}

请严格从测试设计方法列表中选择，多个方法用逗号分隔。

仅返回测试设计方法，不要包含其他内容。
"""
        )
        
        # 生成提示
        prompt = prompt_template.format(
            user_requirement=user_requirement,
            test_methods=", ".join(TEST_METHODS)
        )
        
        # 调用LLM分析
        result = self.llm.invoke(prompt)
        
        # 处理结果
        result = result.strip()
        methods = []
        
        if result and result != "未知":
            for method in result.split("，"):
                method = method.strip()
                if method in TEST_METHODS:
                    methods.append(method)
        
        # 如果没有匹配到方法，返回所有方法
        if not methods:
            methods = TEST_METHODS
        
        return methods
    
    def retrieve_cases(self, user_requirement: str, matching_methods: List[str]) -> List[Dict[str, Any]]:
        """
        检索匹配的测试用例
        """
        print(f"\n正在检索匹配的测试用例...")
        print(f"用户测试目的：{user_requirement}")
        print(f"匹配的测试设计方法：{', '.join(matching_methods)}")
        
        # 直接从数据库中查询
        cursor = self.db_conn.cursor()
        
        # 构建查询条件
        query = """
            SELECT id, title, description, test_method, content 
            FROM test_cases 
        """
        
        cursor.execute(query)
        cases = cursor.fetchall()
        
        # 转换为字典格式
        case_list = []
        for case in cases:
            case_dict = {
                "id": case[0],
                "title": case[1],
                "description": case[2],
                "test_method": case[3],
                "content": case[4]
            }
            case_list.append(case_dict)
        
        # 筛选匹配测试方法的用例
        matched_cases = []
        for case in case_list:
            case_methods = case["test_method"].split("，")
            # 检查是否有匹配的方法
            if any(method in matching_methods for method in case_methods) or case["test_method"] == "未知":
                matched_cases.append(case)
        
        # 限制结果数量
        matched_cases = matched_cases[:TOP_K]
        
        print(f"共检索到 {len(matched_cases)} 个匹配的测试用例")
        
        return matched_cases
    
    def stream_output_results(self, matched_cases: List[Dict[str, Any]]):
        """
        流式输出检索结果
        """
        print("\n========== 检索结果 ==========")
        
        for i, case in enumerate(matched_cases, 1):
            print(f"\n\n--- 测试用例 {i} ---")
            print(f"用例ID：{case['id']}")
            print(f"用例标题：{case['title']}")
            print(f"测试方法：{case['test_method']}")
            if case['description']:
                print(f"用例描述：{case['description']}")
            print(f"用例内容：{case['content']}")
        
        print("\n\n========== 检索完成 ==========")
    
    def run(self):
        """
        运行交互式检索
        """
        while True:
            # 获取用户需求
            user_requirement = self.get_user_requirement()
            
            if not user_requirement:
                print("\n输入不能为空，请重新输入！")
                continue
            
            # 分析匹配的测试设计方法
            print(f"\n正在分析匹配的测试设计方法...")
            matching_methods = self.analyze_matching_methods(user_requirement)
            print(f"\n匹配的测试设计方法：{', '.join(matching_methods)}")
            
            # 检索匹配的测试用例
            matched_cases = self.retrieve_cases(user_requirement, matching_methods)
            
            # 流式输出结果
            self.stream_output_results(matched_cases)
            
            # 询问是否继续
            print("\n\n是否继续检索？（y/n）")
            continue_input = input().strip().lower()
            if continue_input != 'y':
                print("\n感谢使用测试用例智能检索系统！")
                break
    
    def __del__(self):
        """
        关闭数据库连接
        """
        if hasattr(self, 'db_conn'):
            self.db_conn.close()

if __name__ == "__main__":
    retriever = CaseRetriever()
    retriever.run()
