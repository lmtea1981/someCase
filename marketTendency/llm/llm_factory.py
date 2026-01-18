from config import LLM_CONFIG
from llm.ollama_llm import OllamaLLMIntegration
from llm.qianfan_llm import QianfanLLMIntegration

class LLMFactory:
    """
    LLM工厂类，用于根据配置创建合适的LLM实例
    """
    
    @staticmethod
    def get_llm(streaming=None):
        """
        根据配置获取LLM实例
        
        Args:
            streaming: 是否启用流输出，默认使用配置值
            
        Returns:
            配置好的LLM实例
        """
        model_provider = LLM_CONFIG.get("model_provider", "ollama")
        
        if model_provider == "ollama":
            # 使用Ollama模型
            return OllamaLLMIntegration().get_llm(streaming)
        elif model_provider == "qianfan":
            # 使用千帆模型
            return QianfanLLMIntegration().get_llm(streaming)
        else:
            # 默认使用Ollama模型
            return OllamaLLMIntegration().get_llm(streaming)
    
    @staticmethod
    def get_model_info():
        """
        获取当前模型信息
        
        Returns:
            模型信息字典
        """
        model_provider = LLM_CONFIG.get("model_provider", "ollama")
        
        if model_provider == "ollama":
            return {
                "provider": "ollama",
                "model": LLM_CONFIG.get("ollama_model", "llama3")
            }
        elif model_provider == "qianfan":
            return {
                "provider": "qianfan",
                "model": LLM_CONFIG.get("qianfan_model", "ERNIE-Bot-4")
            }
        else:
            return {
                "provider": "ollama",
                "model": LLM_CONFIG.get("ollama_model", "llama3")
            }
