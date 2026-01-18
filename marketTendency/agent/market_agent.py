from tools.cls_extractor_tool import extract_cls_investment_calendar
from tools.web_search_tool import web_search
from llm.llm_factory import LLMFactory
from llm.token_counter import TokenUsageTracker, format_token_report
from agent.agent_prompt import MARKET_AGENT_PROMPT
from config import AGENT_CONFIG
from chains.event_chain import EventAnalysisChain
from chains.sector_chain import SectorAnalysisChain
from chains.cycle_chain import CycleAnalysisChain
from chains.strategy_chain import StrategyRecommendationChain

class MarketTrendAgent:
    """
    市场趋势分析Agent，用于协调工作流程，完成从信息提取到建议生成的全流程
    """
    
    def __init__(self):
        """
        初始化市场趋势分析Agent
        """
        # 创建Token跟踪器
        self.token_tracker = TokenUsageTracker()
        
        # 初始化分析链
        self.event_chain = EventAnalysisChain()
        self.sector_chain = SectorAnalysisChain()
        self.cycle_chain = CycleAnalysisChain()
        self.strategy_chain = StrategyRecommendationChain()
    
    def run(self, query: str = "分析2026年1月的投资日历事件并生成投资建议") -> str:
        """
        运行市场趋势分析Agent
        
        Args:
            query: 分析查询指令
            
        Returns:
            完整的分析报告和投资建议
        """
        try:
            # 1. 信息提取
            investment_calendar = extract_cls_investment_calendar()
            
            # 格式化事件信息
            events_text = []
            for day in investment_calendar:
                events_text.append(f"日期: {day.get('date')} {day.get('day')}")
                for event in day.get('events', []):
                    events_text.append(f"  - {event.get('content')} (类型: {event.get('type')}, 关联: {event.get('relevance')})")
            events_text = "\n".join(events_text)
            
            # 2. 关联资讯搜索
            important_events = []
            for day in investment_calendar:
                for event in day.get('events', []):
                    if event.get('type') in ['货币政策', '监管政策', '国际会议', '经济数据']:
                        important_events.append(event.get('content'))
            
            related_news = []
            for event in important_events[:3]:  # 只搜索前3个重要事件
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
            
            # 3. 综合分析
            event_analysis = self.event_chain.analyze(events_text[:1000], related_news_text[:500])
            sector_analysis = self.sector_chain.analyze(events_text[:1000])
            cycle_analysis = self.cycle_chain.analyze(events_text[:1000])
            
            # 4. 建议生成
            strategy_recommendation = self.strategy_chain.recommend(
                events_text[:500],
                event_analysis[:500],
                sector_analysis[:500],
                cycle_analysis[:500]
            )
            
            # 5. 整合结果
            final_result = f"""
=== 市场趋势分析报告 ===

## 一、近期投资日历
{events_text}

## 二、事件影响分析
{event_analysis}

## 三、板块利好/风险分析
{sector_analysis}

## 四、投资周期建议
{cycle_analysis}

## 五、投资策略建议
{strategy_recommendation}

=== Token用量统计 ===
"""
            
            # 汇总所有链的Token使用情况
            total_tokens = {
                "total_requests": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0
            }
            
            for chain in [self.event_chain, self.sector_chain, self.cycle_chain, self.strategy_chain]:
                usage = chain.get_token_usage()
                for key in total_tokens:
                    total_tokens[key] += usage.get(key, 0)
            
            # 添加Token报告
            final_result += format_token_report(total_tokens)
            
            return final_result
        except Exception as e:
            return f"Agent执行失败: {str(e)}"
    
    def get_token_usage(self):
        """
        获取Token使用情况
        
        Returns:
            Token使用情况报告
        """
        return self.token_tracker.get_usage_report()
