import sys
import os

# 添加项目根目录到Python搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.cls_extractor_tool import extract_cls_investment_calendar
from tools.web_search_tool import web_search
from chains.event_chain import EventAnalysisChain
from chains.sector_chain import SectorAnalysisChain
from chains.cycle_chain import CycleAnalysisChain
from chains.strategy_chain import StrategyRecommendationChain
from llm.token_counter import TokenUsageTracker, format_token_report
from utils.streaming_output import StreamingOutputHandler

class SimpleMarketWorkflow:
    """
    简化的市场趋势分析工作流，直接使用chains和tools
    """
    
    def __init__(self):
        """
        初始化简化工作流
        """
        self.stream_handler = StreamingOutputHandler()
        self.token_tracker = TokenUsageTracker()
        
        # 初始化分析链
        self.event_chain = EventAnalysisChain()
        self.sector_chain = SectorAnalysisChain()
        self.cycle_chain = CycleAnalysisChain()
        self.strategy_chain = StrategyRecommendationChain()
    
    def run(self):
        """
        运行简化工作流
        
        Returns:
            完整的分析报告
        """
        try:
            # 1. 信息提取
            self.stream_handler.write("1. 正在提取CLS投资日历信息...\n")
            investment_calendar = extract_cls_investment_calendar()
            
            # 格式化事件信息
            events_text = self._format_events(investment_calendar)
            self.stream_handler.write(f"   提取到 {len(investment_calendar)} 天的投资日历信息\n\n")
            
            # 2. 关联资讯搜索（针对重要事件）
            self.stream_handler.write("2. 正在搜索相关资讯...\n")
            important_events = self._get_important_events(investment_calendar)
            related_news = []
            
            for event in important_events[:3]:  # 只搜索前3个重要事件
                self.stream_handler.write(f"   搜索事件: {event[:50]}...\n")
                search_results = web_search(event, max_results=2)
                related_news.append({
                    "event": event,
                    "news": search_results
                })
            
            related_news_text = self._format_related_news(related_news)
            self.stream_handler.write(f"   完成 {len(related_news)} 个事件的资讯搜索\n\n")
            
            # 3. 综合分析
            self.stream_handler.write("3. 正在进行综合分析...\n")
            
            # 3.1 事件分析
            self.stream_handler.write("   3.1 事件分析...\n")
            event_analysis = self.event_chain.analyze(events_text[:1000], related_news_text[:500])
            
            # 3.2 板块分析
            self.stream_handler.write("   3.2 板块分析...\n")
            sector_analysis = self.sector_chain.analyze(events_text[:1000])
            
            # 3.3 投资周期分析
            self.stream_handler.write("   3.3 投资周期分析...\n")
            cycle_analysis = self.cycle_chain.analyze(events_text[:1000])
            
            self.stream_handler.write("   综合分析完成\n\n")
            
            # 4. 建议生成
            self.stream_handler.write("4. 正在生成投资建议...\n")
            strategy_recommendation = self.strategy_chain.recommend(
                events_text[:500],
                event_analysis[:500],
                sector_analysis[:500],
                cycle_analysis[:500]
            )
            self.stream_handler.write("   投资建议生成完成\n\n")
            
            # 5. 整合结果
            self.stream_handler.print_title("市场趋势分析报告")
            
            # 5.1 投资日历摘要
            self.stream_handler.write("## 一、近期投资日历\n")
            self.stream_handler.write(events_text[:2000] + "\n\n")
            
            # 5.2 事件分析
            self.stream_handler.write("## 二、事件影响分析\n")
            self.stream_handler.write(event_analysis + "\n\n")
            
            # 5.3 板块分析
            self.stream_handler.write("## 三、板块利好/风险分析\n")
            self.stream_handler.write(sector_analysis + "\n\n")
            
            # 5.4 投资周期分析
            self.stream_handler.write("## 四、投资周期建议\n")
            self.stream_handler.write(cycle_analysis + "\n\n")
            
            # 5.5 投资策略建议
            self.stream_handler.write("## 五、投资策略建议\n")
            self.stream_handler.write(strategy_recommendation + "\n\n")
            
            # 6. 生成Token用量报告
            self.stream_handler.write("## 六、Token用量统计\n")
            
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
            
            token_report = format_token_report(total_tokens)
            self.stream_handler.write(token_report + "\n")
            
            return "市场趋势分析报告生成完成！"
            
        except Exception as e:
            self.stream_handler.write(f"工作流执行失败: {str(e)}\n")
            import traceback
            traceback.print_exc()
            return f"工作流执行失败: {str(e)}"
    
    def _format_events(self, investment_calendar):
        """
        格式化事件信息
        """
        formatted = []
        for day in investment_calendar:
            formatted.append(f"日期: {day.get('date')} {day.get('day')}")
            for event in day.get('events', []):
                formatted.append(f"  - {event.get('content')} (类型: {event.get('type')}, 关联: {event.get('relevance')})")
        return "\n".join(formatted)
    
    def _get_important_events(self, investment_calendar):
        """
        提取重要事件
        """
        important_events = []
        for day in investment_calendar:
            for event in day.get('events', []):
                # 筛选重要事件类型
                if event.get('type') in ['货币政策', '监管政策', '国际会议', '经济数据']:
                    important_events.append(event.get('content'))
        return important_events
    
    def _format_related_news(self, related_news):
        """
        格式化相关资讯
        """
        formatted = []
        for item in related_news:
            formatted.append(f"事件: {item['event']}")
            for news in item['news']:
                if 'error' not in news:
                    formatted.append(f"  - {news.get('title', '')}: {news.get('snippet', '')[:100]}...")
        return "\n".join(formatted)
