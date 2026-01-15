# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name ：   browser_tools
  Description :    
  Author :    lmtea
  date ：    2026/1/15
-------------------------------------------------
  Change Activity:    2026/1/15
-------------------------------------------------
__author__ = 'lmtea'
"""
import os
import requests
import json
from typing import Type
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 定义工具输入Schema（遵循官方示例，继承BaseModel）
class ScrapeWebsiteInput(BaseModel):
    """Input schema for BrowserTool - Scrape website with BeautifulSoup"""
    website: str = Field(..., description="完整的网页URL字符串，例如：https://thehackernews.com/")

# 自定义工具（继承BaseTool，遵循官方示例规范）
class BrowserTool(BaseTool):
    # 工具基本信息（官方要求必须定义）
    name: str = "Scrape and extract website content with BeautifulSoup"
    description: str = "使用BeautifulSoup提取指定网页的核心新闻内容，仅接收完整且有效的URL字符串，优先用于提取https://thehackernews.com/的新闻条目"
    args_schema: Type[BaseModel] = ScrapeWebsiteInput  # 绑定输入Schema

    def _run(self, website: str) -> str:
        """
        工具核心执行逻辑（官方要求必须实现的_run方法，参数与args_schema对应）
        提取目标网页的新闻标题、摘要、发布时间和链接，返回JSON格式结果
        """
        try:
            # 请求网页内容（添加请求头避免被反爬）
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(website, headers=headers, timeout=10)
            response.raise_for_status()  # 抛出HTTP错误（4xx/5xx）

            # BeautifulSoup解析网页结构
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []

            # 定位The Hacker News的新闻条目（适配当前网页结构）
            for item in soup.find_all('div', class_='body-post clear'):
                # 提取新闻链接（从story-link类的a标签中获取）
                link_elem = item.find('a', class_='story-link')
                link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
                # 提取标题
                title_elem = item.find('h2', class_='home-title')
                title = title_elem.get_text(strip=True) if title_elem else ""
                # 提取新闻摘要
                summary_elem = item.find('div', class_='home-desc')
                summary = summary_elem.get_text(strip=True) if summary_elem else ""
                # 提取发布时间
                time_elem = item.find('span', class_='h-datetime')
                publish_time = time_elem.get_text(strip=True) if time_elem else ""

                # 过滤空内容，仅保留有效新闻条目
                if title and summary:
                    news_items.append({
                        "title": title,
                        "summary": summary,
                        "publish_time": publish_time,
                        "link": link
                    })

            # 转换为JSON格式字符串返回，确保中文（若有）正常显示
            return json.dumps(news_items, ensure_ascii=False, indent=2)

        except requests.exceptions.RequestException as e:
            return f"网页请求失败：{str(e)}"
        except Exception as e:
            return f"网页提取异常：{str(e)}"