from langchain_core.prompts import PromptTemplate
from llm.llm_factory import LLMFactory
from llm.token_counter import TokenUsageTracker

class CycleAnalysisChain:
    """
    投资周期分析链，用于分析投资周期规律并给出投资周期建议
    """
    
    def __init__(self):
        """
        初始化投资周期分析链
        """
        self.llm = LLMFactory.get_llm()
        self.token_tracker = TokenUsageTracker()
        
        # 创建提示词模板
        self.prompt_template = PromptTemplate(
            input_variables=["events", "market_context"],
            template="""
            请根据以下近期投资事件和市场背景，分析投资周期规律并给出投资周期建议：
            
            近期事件：
            {events}
            
            市场背景：当前是2026年1月，全球经济处于复苏阶段，中国经济增长稳定，货币政策适度宽松。
            
            请从以下几个方面进行分析：
            1. 短期周期（1-4周）：近期事件对短期市场的影响如何？有哪些短期投资机会？
            2. 中期周期（1-3个月）：中期市场走势如何？有哪些中期投资机会？
            3. 长期周期（3个月以上）：长期市场趋势如何？有哪些长期投资机会？
            4. 周期轮动：不同周期之间的轮动关系如何？投资者应如何应对？
            5. 投资建议：针对不同投资周期，投资者应采取什么策略？
            
            请提供结构化、详细的分析，使用清晰的标题和段落。
            """
        )
    
    def analyze(self, events: str, market_context: str = "") -> str:
        """
        分析投资周期规律并给出建议
        
        Args:
            events: 近期事件列表
            market_context: 市场背景信息
            
        Returns:
            投资周期分析报告
        """
        try:
            # 直接使用LLM进行分析，不依赖LLMChain
            formatted_prompt = self.prompt_template.format(events=events, market_context=market_context)
            result = self.llm.invoke(formatted_prompt)
            return result
        except Exception as e:
            return f"投资周期分析失败: {str(e)}"
    
    def get_token_usage(self):
        """
        获取Token使用情况
        
        Returns:
            Token使用情况报告
        """
        return self.token_tracker.get_usage_report()
