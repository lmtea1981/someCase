# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name ：   search_tools
  Description :    
  Author :    lmtea
  date ：    2026/1/15
-------------------------------------------------
  Change Activity:    2026/1/15
-------------------------------------------------
__author__ = 'lmtea'
"""
import os
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 定义工具输入Schema（遵循官方示例，继承BaseModel）
class TavilySearchInput(BaseModel):
    """Input schema for SearchTool - Tavily internet search"""
    query: str = Field(..., description="搜索关键词字符串，用于查询互联网相关信息，例如：cybersecurity latest terminology")

# 自定义工具（继承BaseTool，遵循官方示例规范）
class SearchTool(BaseTool):
    # 工具基本信息（官方要求必须定义）
    name: str = "Search internet with Tavily"
    description: str = "使用Tavily搜索引擎查询互联网最新信息，适用于补充新闻背景、验证专业术语、获取最新行业动态，接收搜索关键词作为参数"
    args_schema: Type[BaseModel] = TavilySearchInput  # 绑定输入Schema

    def _run(self, query: str) -> str:
        """
        工具核心执行逻辑（官方要求必须实现的_run方法，参数与args_schema对应）
        执行Tavily搜索，返回格式化的搜索结果
        """
        try:
            # 初始化Tavily搜索工具
            tavily = TavilySearchResults(
                api_key=os.environ.get("TAVILY_API_KEY"),
                max_results=5,  # 控制返回结果数量，避免信息过载
                search_depth="basic"  # 基础搜索，平衡效率和结果丰富度
            )

            # 执行搜索并返回结果
            search_results = tavily.run(query)
            return f"Tavily搜索结果（关键词：{query}）：\n{search_results}"

        except Exception as e:
            return f"Tavily搜索失败：{str(e)}"