from langchain_core.callbacks import BaseCallbackHandler
from typing import Dict, Any

class TokenUsageTracker(BaseCallbackHandler):
    """
    Token用量跟踪器，用于统计LLM调用的token使用情况
    """
    
    def __init__(self):
        """
        初始化Token用量跟踪器
        """
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0
        self.requests = 0
    
    def on_llm_end(self, response: Any, **kwargs: Any) -> Any:
        """
        LLM调用结束时触发，统计token用量
        """
        self.requests += 1
        
        # 处理不同模型的token使用情况
        if hasattr(response, 'usage_metadata'):
            # 处理LangChain 1.2+的usage_metadata
            usage = response.usage_metadata
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)
        elif hasattr(response, 'llm_output'):
            # 处理旧版LangChain的llm_output
            llm_output = response.llm_output
            if isinstance(llm_output, dict):
                usage = llm_output.get('usage', {})
                input_tokens = usage.get('prompt_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0)
            else:
                input_tokens = 0
                output_tokens = 0
        else:
            # 无法获取token使用情况，使用近似值
            input_tokens = 0
            output_tokens = 0
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_tokens = self.total_input_tokens + self.total_output_tokens
    
    def get_usage_report(self) -> Dict[str, Any]:
        """
        获取Token用量报告
        
        Returns:
            Token用量报告字典
        """
        return {
            "total_requests": self.requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens
        }
    
    def reset(self) -> None:
        """
        重置Token用量统计
        """
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0
        self.requests = 0

def format_token_report(report: Dict[str, Any]) -> str:
    """
    格式化Token用量报告为可读字符串
    
    Args:
        report: Token用量报告字典
        
    Returns:
        格式化的Token用量报告字符串
    """
    return f"""=== Token用量统计 ===
总请求次数: {report['total_requests']}
输入Token: {report['total_input_tokens']}
输出Token: {report['total_output_tokens']}
总Token: {report['total_tokens']}
=== Token用量统计结束 ==="""
