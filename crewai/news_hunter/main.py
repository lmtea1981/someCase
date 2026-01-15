# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name ：   main
  Description :    
  Author :    lmtea
  date ：    2026/1/15
-------------------------------------------------
  Change Activity:    2026/1/15
-------------------------------------------------
__author__ = 'lmtea'
"""
from crewai import Crew, Process
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 导入代理和任务
from news_agents import NewsAgents
from news_tasks import NewsTasks

def main():
    # 初始化代理和任务
    news_agents = NewsAgents()
    news_tasks = NewsTasks()

    # 创建代理实例
    extractor_agent = news_agents.content_extractor_agent()
    translator_agent = news_agents.content_translator_agent()

    # 创建任务实例
    extract_task = news_tasks.extract_content_task(extractor_agent)
    translate_task = news_tasks.translate_content_task(translator_agent, extract_task)

    # 组建Crew并执行
    news_crew = Crew(
        agents=[extractor_agent, translator_agent],
        tasks=[extract_task, translate_task],
        process=Process.sequential,  # 顺序执行任务
        verbose=True  # 详细日志输出
    )

    # 执行任务并输出结果
    print("=== 开始提取并翻译The Hacker News内容 ===")
    result = news_crew.kickoff()

    # 打印最终结果
    print("\n=== 提取翻译完成 ===")
    print(result)

if __name__ == "__main__":
    # 检查Ollama是否启动（可选）
    import requests
    try:
        ollama_url = os.environ.get("OLLAMA_BASE_URL")
        requests.get(f"{ollama_url}/api/tags")
    except requests.exceptions.ConnectionError:
        print("错误：Ollama服务未启动，请先执行 `ollama serve` 并确保模型已拉取（如 `ollama pull llama3`）")
        exit(1)

    main()