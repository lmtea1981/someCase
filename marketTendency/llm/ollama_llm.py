from langchain_ollama.llms import OllamaLLM
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from config import LLM_CONFIG

class OllamaLLMIntegration:
    """
    Ollama模型集成类，用于创建和配置Ollama LLM实例
    """
    
    def __init__(self):
        """
        初始化Ollama LLM集成
        """
        self.model_name = LLM_CONFIG.get("ollama_model", "llama3")
        self.temperature = LLM_CONFIG.get("temperature", 0.7)
        self.max_tokens = LLM_CONFIG.get("max_tokens", 2048)
        self.streaming = LLM_CONFIG.get("streaming", True)
        
    def get_llm(self, streaming=None):
        """
        获取配置好的Ollama LLM实例
        
        Args:
            streaming: 是否启用流输出，默认使用配置值
            
        Returns:
            配置好的Ollama LLM实例
        """
        if streaming is None:
            streaming = self.streaming
        
        callbacks = [StreamingStdOutCallbackHandler()] if streaming else []
        
        return OllamaLLM(
            model=self.model_name,
            temperature=self.temperature,
            num_ctx=self.max_tokens,
            callbacks=callbacks,
            stream=streaming
        )
