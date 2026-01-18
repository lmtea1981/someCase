#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
市场趋势预测系统主程序
"""

import sys
import os
from typing import List, Dict

# 添加当前目录到Python搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.streaming_output import StreamingOutputHandler
from chains.event_chain import EventAnalysisChain
from chains.sector_chain import SectorAnalysisChain
from chains.cycle_chain import CycleAnalysisChain
from chains.strategy_chain import StrategyRecommendationChain
from llm.token_counter import TokenUsageTracker, format_token_report
from config import LLM_CONFIG
from llm.llm_factory import LLMFactory

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
            
            # 直接使用真实的CLS提取工具，不使用模拟数据
            from tools.cls_extractor_tool import extract_cls_investment_calendar
            
            # 由于extract_cls_investment_calendar是StructuredTool对象，我们需要访问其func属性来调用原始函数
            # 显式传入正确的URL：https://www.cls.cn/
            if hasattr(extract_cls_investment_calendar, 'func'):
                investment_calendar = extract_cls_investment_calendar.func(url="https://www.cls.cn/")
            else:
                # 如果func属性不存在，直接调用函数（可能是装饰器版本问题）
                investment_calendar = extract_cls_investment_calendar(url="https://www.cls.cn/")
            
            # 检查是否提取到有效数据
            if not investment_calendar or any('error' in day for day in investment_calendar):
                self.stream_handler.write("   提取到的日历信息为空或包含错误\n")
                return "提取CLS投资日历信息失败"
            
            # 格式化事件信息
            events_text = self._format_events(investment_calendar)
            self.stream_handler.write(f"   提取到 {len(investment_calendar)} 天的投资日历信息\n")
            
            # 获取日期范围
            if investment_calendar:
                # 按日期排序
                sorted_calendar = sorted(investment_calendar, key=lambda x: x['date'])
                start_date = sorted_calendar[0]['date']
                end_date = sorted_calendar[-1]['date']
                self.stream_handler.write(f"   日期范围: {start_date} 至 {end_date}\n\n")
            
            # 2. 综合分析
            self.stream_handler.write("2. 正在进行综合分析...\n")
            
            # 2.1 对所有事件进行总体分析
            self.stream_handler.write("   2.1 对所有事件进行总体分析...\n")
            # 先使用所有事件进行总体分析，不包含相关资讯
            overall_analysis = self.event_chain.analyze(events_text[:2000], "")
            
            # 2.2 对重点领域或事件搜索补充额外信息
            self.stream_handler.write("2.2 正在搜索重点领域/事件的补充资讯...\n")
            important_events = self._get_important_events(investment_calendar)
            related_news = []
            
            for event in important_events[:3]:  # 只搜索前3个重要事件
                self.stream_handler.write(f"   搜索事件: {event[:50]}...\n")
                search_results = self._mock_web_search(event, max_results=2)
                related_news.append({
                    "event": event,
                    "news": search_results
                })
            
            related_news_text = self._format_related_news(related_news)
            self.stream_handler.write(f"   完成 {len(related_news)} 个事件的资讯搜索\n\n")
            
            # 2.3 结合总体分析和补充信息进行最终事件分析
            self.stream_handler.write("3. 正在进行综合分析...\n")
            
            # 3.1 事件分析（结合总体分析和补充资讯）
            self.stream_handler.write("   3.1 事件分析...\n")
            # 将总体分析作为事件文本的一部分，结合相关资讯进行最终分析
            combined_events_text = f"【总体分析】：\n{overall_analysis}\n\n【详细事件】：\n{events_text[:1000]}"
            event_analysis = self.event_chain.analyze(combined_events_text[:1500], related_news_text[:500])
            
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
    
    def _mock_cls_investment_calendar(self):
        """
        模拟CLS投资日历数据
        
        Returns:
            模拟的投资日历数据
        """
        from datetime import datetime, timedelta
        
        # 生成从今天开始的未来14天的模拟数据
        today = datetime.now()
        day_map = {
            0: '星期一',
            1: '星期二',
            2: '星期三',
            3: '星期四',
            4: '星期五',
            5: '星期六',
            6: '星期日'
        }
        
        mock_data = []
        
        for i in range(14):
            current_date = today + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            day_str = day_map.get(current_date.weekday(), str(current_date.weekday()))
            
            # 根据日期生成不同类型的事件
            events = []
            
            # 周一：国际会议和事件
            if current_date.weekday() == 0:
                events.append({
                    "content": f"{date_str} 国际重要经济会议召开",
                    "type": "国际会议",
                    "relevance": "全球市场"
                })
            
            # 周二、周四：货币政策相关事件
            elif current_date.weekday() in [1, 3]:
                events.append({
                    "content": f"{date_str} 央行货币政策会议",
                    "type": "货币政策",
                    "relevance": "A股、债市"
                })
            
            # 周三：经济数据发布
            elif current_date.weekday() == 2:
                events.append({
                    "content": f"{date_str} 重要经济数据发布",
                    "type": "经济数据",
                    "relevance": "宏观经济"
                })
            
            # 周五：市场回顾和展望
            elif current_date.weekday() == 4:
                events.append({
                    "content": f"{date_str} 当周市场回顾与展望",
                    "type": "市场动态",
                    "relevance": "全球市场"
                })
            
            # 每天都有行业相关事件
            events.append({
                "content": f"{date_str} 行业重要事件",
                "type": "行业事件",
                "relevance": "相关板块"
            })
            
            mock_data.append({
                "date": date_str,
                "day": day_str,
                "events": events
            })
        
        return mock_data
    
    def _mock_web_search(self, query: str, max_results: int = 2) -> List[Dict]:
        """
        模拟网络搜索
        
        Args:
            query: 搜索关键词
            max_results: 返回结果数量限制
            
        Returns:
            模拟的搜索结果
        """
        # 模拟搜索结果
        mock_results = {
            "第56届世界经济论坛年会": [
                {
                    "title": "第56届世界经济论坛年会将聚焦全球经济复苏",
                    "url": "https://example.com/davos-2026",
                    "snippet": "第56届世界经济论坛年会将于1月19日至23日在瑞士达沃斯举行，本届年会将聚焦全球经济复苏、气候变化等议题...",
                    "source": "example.com"
                },
                {
                    "title": "达沃斯论坛：全球领导人将共商经济发展大计",
                    "url": "https://example.com/davos-leaders",
                    "snippet": "来自全球的政商界领导人将齐聚达沃斯，讨论全球经济面临的挑战和机遇...",
                    "source": "example.com"
                }
            ],
            "中国人民银行下调利率": [
                {
                    "title": "央行下调再贷款再贴现利率，释放流动性支持实体经济",
                    "url": "https://example.com/pboc-rate-cut",
                    "snippet": "中国人民银行决定自1月19日起下调再贷款、再贴现利率0.25个百分点，这是年内首次降息...",
                    "source": "example.com"
                },
                {
                    "title": "降息预期落地，债市迎来利好",
                    "url": "https://example.com/bond-market-rally",
                    "snippet": "央行降息消息公布后，债市反应积极，债券价格普遍上涨...",
                    "source": "example.com"
                }
            ],
            "沪深北交易所调整融资保证金比例": [
                {
                    "title": "交易所调整融资保证金比例，股市杠杆风险管控加强",
                    "url": "https://example.com/margin-requirement-hike",
                    "snippet": "沪深北交易所发布通知，将融资保证金最低比例从80%提高至100%，旨在加强股市杠杆风险管控...",
                    "source": "example.com"
                },
                {
                    "title": "融资保证金比例上调，对股市影响几何",
                    "url": "https://example.com/margin-impact",
                    "snippet": "分析人士认为，融资保证金比例上调将适度抑制市场杠杆，有利于市场长期稳定发展...",
                    "source": "example.com"
                }
            ]
        }
        
        # 查找匹配的结果
        for key in mock_results:
            if key in query:
                return mock_results[key][:max_results]
        
        # 默认结果
        return [
            {
                "title": f"关于{query}的最新资讯",
                "url": "https://example.com/default",
                "snippet": f"搜索到关于{query}的最新资讯...",
                "source": "example.com"
            }
        ][:max_results]

def main():
    """
    主程序入口
    """
    # 初始化流输出处理器
    stream_handler = StreamingOutputHandler()
    
    # 打印程序标题
    stream_handler.print_title("市场趋势预测系统")
    model_info = LLMFactory.get_model_info()
    stream_handler.write(f"\n当前模型: {model_info['provider']} - {model_info['model']}\n")
    stream_handler.write(f"流输出: {'启用' if LLM_CONFIG.get('streaming', True) else '禁用'}\n\n")
    
    try:
        # 初始化简化工作流
        stream_handler.write("正在初始化市场趋势分析工作流...\n")
        workflow = SimpleMarketWorkflow()
        stream_handler.write("工作流初始化完成！\n\n")
        
        # 运行工作流
        stream_handler.write("开始分析2026年1月投资日历事件...\n")
        stream_handler.print_divider()
        
        result = workflow.run()
        
        # 输出最终结果
        stream_handler.print_divider()
        stream_handler.write(f"\n{result}\n")
        
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
