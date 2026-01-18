from langchain_core.prompts import PromptTemplate
from llm.llm_factory import LLMFactory
from llm.token_counter import TokenUsageTracker

class SectorAnalysisChain:
    """
    板块分析链，用于分析事件对各板块的利好/风险影响
    """
    
    def __init__(self):
        """
        初始化板块分析链
        """
        self.llm = LLMFactory.get_llm()
        self.token_tracker = TokenUsageTracker()
        
        # 创建提示词模板
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
            3. 中性板块：哪些板块受影响较小？为什么？
            4. 板块轮动：这些事件可能导致哪些板块轮动？
            5. 投资建议：针对不同板块，投资者应采取什么策略？
            
            请提供结构化、详细的分析，使用清晰的标题和段落。
            """
        )
    
    def analyze(self, events: str, market_context: str = "") -> str:
        """
        分析事件对各板块的影响
        
        Args:
            events: 近期事件列表
            market_context: 市场背景信息
            
        Returns:
            板块分析报告
        """
        try:
            # 直接使用LLM进行分析，不依赖LLMChain
            formatted_prompt = self.prompt_template.format(events=events, market_context=market_context)
            result = self.llm.invoke(formatted_prompt)
            return result
        except Exception as e:
            return f"板块分析失败: {str(e)}"
    
    def get_token_usage(self):
        """
        获取Token使用情况
        
        Returns:
            Token使用情况报告
        """
        return self.token_tracker.get_usage_report()
