from langchain_core.prompts import PromptTemplate
from llm.llm_factory import LLMFactory
from llm.token_counter import TokenUsageTracker

class StrategyRecommendationChain:
    """
    投资策略链，用于生成最终的投资建议
    """
    
    def __init__(self):
        """
        初始化投资策略链
        """
        self.llm = LLMFactory.get_llm()
        self.token_tracker = TokenUsageTracker()
        
        # 创建提示词模板
        self.prompt_template = PromptTemplate(
            input_variables=["events", "event_analysis", "sector_analysis", "cycle_analysis"],
            template="""
            请根据以下近期投资事件、事件分析、板块分析和投资周期分析，生成详细的投资建议报告：
            
            近期事件：
            {events}
            
            事件分析：
            {event_analysis}
            
            板块分析：
            {sector_analysis}
            
            投资周期分析：
            {cycle_analysis}
            
            请生成包含以下内容的投资建议报告：
            1. 投资领域：推荐关注的投资领域及其优先级
            2. 投资策略：针对不同投资领域的具体投资策略
            3. 配置文案推荐：适合不同投资者的资产配置文案
            4. 加仓及减仓窗口：建议的加仓和减仓时机
            5. 总结和建议：综合总结和行动建议
            
            请提供结构化、详细的建议，使用清晰的标题和段落，确保建议具有可操作性和实用性。
            """
        )
        
        
    
    def recommend(self, events: str, event_analysis: str, sector_analysis: str, cycle_analysis: str) -> str:
        """
        生成投资建议报告
        
        Args:
            events: 近期事件列表
            event_analysis: 事件分析报告
            sector_analysis: 板块分析报告
            cycle_analysis: 投资周期分析报告
            
        Returns:
            投资建议报告
        """
        try:
            # 直接使用LLM进行分析，不依赖LLMChain
            formatted_prompt = self.prompt_template.format(
                events=events,
                event_analysis=event_analysis,
                sector_analysis=sector_analysis,
                cycle_analysis=cycle_analysis
            )
            result = self.llm.invoke(formatted_prompt)
            return result
        except Exception as e:
            return f"投资建议生成失败: {str(e)}"
    
    def get_token_usage(self):
        """
        获取Token使用情况
        
        Returns:
            Token使用情况报告
        """
        return self.token_tracker.get_usage_report()
