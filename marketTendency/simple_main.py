#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的市场趋势预测系统主程序
"""

import sys
from typing import List, Dict
from langchain_core.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_community.tools.tavily_search import TavilySearchResults

# 配置信息
LLM_CONFIG = {
    "model_provider": "ollama",
    "ollama_model": "llama3",
    "temperature": 0.7,
    "max_tokens": 2048,
    "streaming": True
}

TOOLS_CONFIG = {
    "tavily_api_key": "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"
}

# 流输出处理器
class StreamingOutputHandler:
    def write(self, content: str):
        sys.stdout.write(content)
        sys.stdout.flush()
    
    def writelines(self, lines):
        for line in lines:
            self.write(line)
    
    def print_divider(self, char: str = '-', length: int = 80):
        self.write(f"\n{char * length}\n")
    
    def print_title(self, title: str):
        self.print_divider()
        self.write(f"\n{title}\n")
        self.print_divider()

# 模拟CLS投资日历提取
def extract_cls_investment_calendar():
    """
    从CLS网站提取投资日历信息
    """
    return [
        {
            "date": "2026-01-19",
            "day": "星期一",
            "events": [
                {
                    "content": "第56届世界经济论坛年会（冬季达沃斯）将于1月19日至23日在瑞士达沃斯举行",
                    "type": "国际会议",
                    "relevance": "全球市场"
                },
                {
                    "content": "中国人民银行：自1月19日起，下调再贷款、再贴现利率0.25个百分点",
                    "type": "货币政策",
                    "relevance": "A股、债市"
                },
                {
                    "content": "沪深北交易所发布通知调整融资保证金比例，将投资者融资买入证券时的融资保证金最低比例从80%提高至100%，相关安排自1月19日起正式施行",
                    "type": "监管政策",
                    "relevance": "A股"
                }
            ]
        },
        {
            "date": "2026-01-20",
            "day": "星期二",
            "events": [
                {
                    "content": "央行发布《金融机构客户受益所有人识别管理办法》，自2026年1月20日起施行",
                    "type": "监管政策",
                    "relevance": "金融板块"
                },
                {
                    "content": "2026阿里云PolarDB开发者大会将于1月20日举办",
                    "type": "行业会议",
                    "relevance": "云计算、科技板块"
                }
            ]
        }
    ]

# 模拟网络搜索
def web_search(query: str, max_results: int = 2) -> List[Dict]:
    """
    搜索网络资讯
    """
    try:
        # 使用Tavily搜索
        tavily_search = TavilySearchResults(
            api_key=TOOLS_CONFIG.get("tavily_api_key", ""),
            max_results=max_results
        )
        search_results = tavily_search.run(query)
        
        results = []
        for result in search_results:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("content", ""),
                "source": "tavily"
            })
        
        return results
    except Exception as e:
        return [{"error": f"搜索失败: {str(e)}"}]

# 事件分析链
class EventAnalysisChain:
    def __init__(self):
        self.llm = OllamaLLM(
            model=LLM_CONFIG.get("ollama_model", "llama3"),
            temperature=LLM_CONFIG.get("temperature", 0.7),
            num_ctx=LLM_CONFIG.get("max_tokens", 2048),
            callbacks=[StreamingStdOutCallbackHandler()],
            stream=LLM_CONFIG.get("streaming", True)
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["event", "related_news"],
            template="""
            请分析以下投资事件及其相关资讯，提供详细的分析报告：
            
            事件详情：
            {event}
            
            相关资讯：
            {related_news}
            
            请从以下几个方面进行分析：
            1. 事件热度：该事件在市场中的关注度如何？
            2. 影响范围：该事件会影响哪些市场、行业或板块？
            3. 发展趋势：该事件可能的发展方向和后续影响？
            4. 投资启示：该事件对投资者有哪些启示？
            
            请提供结构化、详细的分析，使用清晰的标题和段落。
            """
        )
    
    def analyze(self, event: str, related_news: str) -> str:
        """
        分析事件及其相关资讯
        """
        try:
            # 直接使用LLM进行分析，不依赖LLMChain
            formatted_prompt = self.prompt_template.format(event=event, related_news=related_news)
            result = self.llm.invoke(formatted_prompt)
            return result
        except Exception as e:
            return f"事件分析失败: {str(e)}"

# 板块分析链
class SectorAnalysisChain:
    def __init__(self):
        self.llm = OllamaLLM(
            model=LLM_CONFIG.get("ollama_model", "llama3"),
            temperature=LLM_CONFIG.get("temperature", 0.7),
            num_ctx=LLM_CONFIG.get("max_tokens", 2048),
            callbacks=[StreamingStdOutCallbackHandler()],
            stream=LLM_CONFIG.get("streaming", True)
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["events", "market_context"],
            template="""
            请根据以下近期投资事件和市场背景，分析对各个板块的利好和风险影响：
            
            近期事件：
            {events}
            
            市场背景：当前是2026年1月，全球经济处于复苏阶段，中国经济增长稳定，货币政策适度宽松。
            
            请从以下几个方面进行分析：
            1. 利好板块：哪些板块会受益于这些事件？具体受益原因是什么？
            2. 风险板块：哪些板块会受到负面影响？具体风险是什么？
            3. 投资建议：针对不同板块，投资者应采取什么策略？
            
            请提供结构化、详细的分析，使用清晰的标题和段落。
            """
        )
    
    def analyze(self, events: str, market_context: str = "") -> str:
        """
        分析事件对各板块的影响
        """
        try:
            # 直接使用LLM进行分析，不依赖LLMChain
            formatted_prompt = self.prompt_template.format(events=events, market_context=market_context)
            result = self.llm.invoke(formatted_prompt)
            return result
        except Exception as e:
            return f"板块分析失败: {str(e)}"

# 简化的市场趋势分析工作流
def main():
    """
    主程序入口
    """
    stream_handler = StreamingOutputHandler()
    
    # 打印程序标题
    stream_handler.print_title("市场趋势预测系统")
    stream_handler.write(f"\n当前模型: ollama - {LLM_CONFIG.get('ollama_model', 'llama3')}\n")
    stream_handler.write(f"流输出: {'启用' if LLM_CONFIG.get('streaming', True) else '禁用'}\n\n")
    
    try:
        # 1. 信息提取
        stream_handler.write("1. 正在提取CLS投资日历信息...\n")
        investment_calendar = extract_cls_investment_calendar()
        
        # 格式化事件信息
        events_text = []
        for day in investment_calendar:
            events_text.append(f"日期: {day.get('date')} {day.get('day')}")
            for event in day.get('events', []):
                events_text.append(f"  - {event.get('content')} (类型: {event.get('type')}, 关联: {event.get('relevance')})")
        events_text = "\n".join(events_text)
        
        stream_handler.write(f"   提取到 {len(investment_calendar)} 天的投资日历信息\n\n")
        
        # 2. 关联资讯搜索（针对重要事件）
        stream_handler.write("2. 正在搜索相关资讯...\n")
        
        # 提取重要事件
        important_events = []
        for day in investment_calendar:
            for event in day.get('events', []):
                if event.get('type') in ['货币政策', '监管政策', '国际会议', '经济数据']:
                    important_events.append(event.get('content'))
        
        # 搜索相关资讯
        related_news = []
        for event in important_events[:2]:  # 只搜索前2个重要事件
            stream_handler.write(f"   搜索事件: {event[:50]}...\n")
            search_results = web_search(event, max_results=2)
            related_news.append({"event": event, "news": search_results})
        
        # 格式化相关资讯
        related_news_text = []
        for item in related_news:
            related_news_text.append(f"事件: {item['event']}")
            for news in item['news']:
                if 'error' not in news:
                    related_news_text.append(f"  - {news.get('title', '')}: {news.get('snippet', '')[:100]}...")
        related_news_text = "\n".join(related_news_text)
        
        stream_handler.write(f"   完成 {len(related_news)} 个事件的资讯搜索\n\n")
        
        # 3. 综合分析
        stream_handler.write("3. 正在进行综合分析...\n")
        
        # 3.1 事件分析
        stream_handler.write("   3.1 事件分析...\n")
        event_chain = EventAnalysisChain()
        event_analysis = event_chain.analyze(events_text[:800], related_news_text[:500])
        stream_handler.write("   事件分析完成\n")
        
        # 3.2 板块分析
        stream_handler.write("   3.2 板块分析...\n")
        sector_chain = SectorAnalysisChain()
        sector_analysis = sector_chain.analyze(events_text[:800])
        stream_handler.write("   板块分析完成\n\n")
        
        # 4. 输出结果
        stream_handler.print_title("市场趋势分析报告")
        
        # 4.1 投资日历摘要
        stream_handler.write("## 一、近期投资日历\n")
        stream_handler.write(events_text[:1500] + "\n\n")
        
        # 4.2 事件分析
        stream_handler.write("## 二、事件影响分析\n")
        stream_handler.write(event_analysis + "\n\n")
        
        # 4.3 板块分析
        stream_handler.write("## 三、板块利好/风险分析\n")
        stream_handler.write(sector_analysis + "\n\n")
        
        # 4.4 投资建议
        stream_handler.write("## 四、投资建议\n")
        stream_handler.write("基于以上分析，建议投资者关注货币政策宽松带来的机会，同时注意市场波动风险。\n\n")
        
        stream_handler.print_title("分析完成")
        stream_handler.write("\n市场趋势分析报告生成完毕！\n")
        
    except KeyboardInterrupt:
        stream_handler.write("\n\n程序已被用户中断！\n")
    except Exception as e:
        stream_handler.write(f"\n\n程序执行出错: {str(e)}\n")
        import traceback
        traceback.print_exc()
    finally:
        stream_handler.print_divider()
        stream_handler.write("\n市场趋势预测系统执行完毕！\n")

if __name__ == "__main__":
    main()