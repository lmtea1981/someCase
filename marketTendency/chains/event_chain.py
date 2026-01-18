from langchain_core.prompts import PromptTemplate
from llm.llm_factory import LLMFactory
from llm.token_counter import TokenUsageTracker

class EventAnalysisChain:
    """
    事件分析链，用于分析事件的热度、影响和趋势
    """
    
    def __init__(self):
        """
        初始化事件分析链
        """
        self.llm = LLMFactory.get_llm()
        self.token_tracker = TokenUsageTracker()
        
        # 创建提示词模板
        self.prompt_template = PromptTemplate(
            input_variables=["event", "related_news"],
            template="""
            请分析以下投资事件及其相关资讯，提供详细的分析报告：
            
            事件详情：
            {event}
            
            相关资讯：
            {related_news}
            
            请从以下几个方面进行分析：
            1. 总体事件评估：对所有事件进行整体梳理，识别核心主题和关联关系
            2. 重点事件深度分析：针对重要事件，分析其热度、影响范围和发展趋势
            3. 事件联动影响：不同事件之间的相互作用和综合影响
            4. 行业板块映射：事件对各行业板块的具体影响
            5. 投资启示与策略：基于事件分析，提供具体的投资建议和操作策略
            
            请提供结构化、详细的分析，使用清晰的标题和段落。
            """
        )
    
    def analyze(self, event: str, related_news: str) -> str:
        """
        分析事件及其相关资讯
        
        Args:
            event: 事件详情
            related_news: 相关资讯
            
        Returns:
            事件分析报告
        """
        try:
            # 直接使用LLM进行分析，不依赖LLMChain
            formatted_prompt = self.prompt_template.format(event=event, related_news=related_news)
            result = self.llm.invoke(formatted_prompt)
            return result
        except Exception as e:
            return f"事件分析失败: {str(e)}"
    
    def get_token_usage(self):
        """
        获取Token使用情况
        
        Returns:
            Token使用情况报告
        """
        return self.token_tracker.get_usage_report()
