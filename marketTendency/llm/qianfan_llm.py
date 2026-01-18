from langchain_community.llms import QianfanLLMEndpoint
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from config import LLM_CONFIG

class QianfanLLMIntegration:
    """
    千帆模型集成类，用于创建和配置千帆LLM实例
    """
    
    def __init__(self):
        """
        初始化千帆LLM集成
        """
        self.model_name = LLM_CONFIG.get("qianfan_model", "ERNIE-Bot-4")
        self.temperature = LLM_CONFIG.get("temperature", 0.7)
        self.max_tokens = LLM_CONFIG.get("max_tokens", 2048)
        self.streaming = LLM_CONFIG.get("streaming", True)
        # 注意：实际使用时需要设置环境变量或配置文件中的API密钥
        # 例如：os.environ["QIANFAN_AK"] = "your_ak"
        #       os.environ["QIANFAN_SK"] = "your_sk"
        
    def get_llm(self, streaming=None):
        """
        获取配置好的千帆LLM实例
        
        Args:
            streaming: 是否启用流输出，默认使用配置值
            
        Returns:
            配置好的千帆LLM实例
        """
        if streaming is None:
            streaming = self.streaming
        
        callbacks = [StreamingStdOutCallbackHandler()] if streaming else []
        
        return QianfanLLMEndpoint(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            streaming=streaming,
            callbacks=callbacks
        )
