# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name ：   news_agents
  Description :    
  Author :    lmtea
  date ：    2026/1/15
-------------------------------------------------
  Change Activity:    2026/1/15
-------------------------------------------------
__author__ = 'lmtea'
"""
from crewai import Agent
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import os
import yaml

# 提前导入遵循官方规范的自定义工具
from tools.browser_tools import BrowserTool
from tools.search_tools import SearchTool

# 加载环境变量
load_dotenv()

# 加载代理配置
def load_agent_config():
    with open("config/agents.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 初始化Ollama LLM
llm = Ollama(
    model=os.environ.get("OLLAMA_MODEL", "ollama/qwen3:latest"),
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
)

# 定义代理
class NewsAgents:
    def __init__(self):
        self.agent_config = load_agent_config()

    # 内容提取代理
    def content_extractor_agent(self):
        # 实例化遵循官方规范的网页提取工具（直接实例化类即可，无需额外包装）
        browser_tool_instance = BrowserTool()

        return Agent(
            role=self.agent_config["content_extractor"]["role"],
            goal=self.agent_config["content_extractor"]["goal"],
            backstory=self.agent_config["content_extractor"]["backstory"],
            verbose=self.agent_config["content_extractor"]["verbose"],
            allow_delegation=self.agent_config["content_extractor"]["allow_delegation"],
            llm=llm,
            tools=[browser_tool_instance]  # 传入工具实例，完美通过pydantic类型校验
        )

    # 内容翻译代理
    def content_translator_agent(self):
        # 实例化遵循官方规范的Tavily搜索工具
        search_tool_instance = SearchTool()

        return Agent(
            role=self.agent_config["content_translator"]["role"],
            goal=self.agent_config["content_translator"]["goal"],
            backstory=self.agent_config["content_translator"]["backstory"],
            verbose=self.agent_config["content_translator"]["verbose"],
            allow_delegation=self.agent_config["content_translator"]["allow_delegation"],
            llm=llm,
            tools=[search_tool_instance]  # 传入工具实例，完美通过pydantic类型校验
        )