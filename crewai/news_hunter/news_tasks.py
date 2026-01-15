# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name ：   news_tasks
  Description :    
  Author :    lmtea
  date ：    2026/1/15
-------------------------------------------------
  Change Activity:    2026/1/15
-------------------------------------------------
__author__ = 'lmtea'
"""
from crewai import Task
import yaml
from dotenv import load_dotenv
import os
from tools.browser_tools import BrowserTool

# 加载环境变量
load_dotenv()

# 加载任务配置
def load_task_config():
    with open("config/tasks.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 定义任务
class NewsTasks:
    def __init__(self):
        self.task_config = load_task_config()
        self.target_url = os.environ.get("TARGET_URL")

    # 提取网页内容任务
    def extract_content_task(self, agent):
        # 直接调用工具获取真实数据
        browser_tool = BrowserTool()
        tool_result = browser_tool._run(self.target_url)
        
        # 创建一个包含真实数据的任务，确保Agent使用实际提取的结果
        return Task(
            description=f"1. 已使用工具获取到目标网页 {self.target_url} 的真实数据\n2. 请直接使用以下提取的JSON结果进行后续处理，不要使用示例数据：\n{tool_result}",
            expected_output="必须使用以上真实提取的数据，生成JSON格式的新闻列表，格式：[{\"title\":\"xxx\",\"summary\":\"xxx\",\"publish_time\":\"xxx\",\"link\":\"xxx\"},...]",
            agent=agent
        )

    # 翻译新闻内容任务
    def translate_content_task(self, agent, extract_task):
        return Task(
            description=self.task_config["translate_content_task"]["description"],
            expected_output=self.task_config["translate_content_task"]["expected_output"],
            agent=agent,
            context=[extract_task]  # 依赖提取任务的结果
        )