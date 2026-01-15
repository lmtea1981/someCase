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
        return Task(
            description=self.task_config["extract_content_task"]["description"].replace("{{TARGET_URL}}", self.target_url),
            expected_output=self.task_config["extract_content_task"]["expected_output"],
            agent=agent,
            # 强制要求使用提供的工具，不能使用内置知识或示例数据
            tools=[BrowserTool()]
        )

    # 翻译新闻内容任务
    def translate_content_task(self, agent, extract_task):
        return Task(
            description=self.task_config["translate_content_task"]["description"],
            expected_output=self.task_config["translate_content_task"]["expected_output"],
            agent=agent,
            context=[extract_task]  # 依赖提取任务的结果
        )