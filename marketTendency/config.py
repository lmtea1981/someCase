# 项目配置文件

# LLM配置
LLM_CONFIG = {
    "model_provider": "ollama",  # 可选值: ollama, qianfan
    "ollama_model": "qwen3:latest",  # 使用更小的模型，更容易获取
    "qianfan_model": "ERNIE-Bot-4",  # 千帆模型名称
    "temperature": 0.7,
    "max_tokens": 2048,
    "streaming": True  # 启用流输出
}

# 工具配置
TOOLS_CONFIG = {
    "cls_url": "https://www.cls.cn/",  # CLS网站URL
    "search_engine": "tavily",  # 搜索引擎
    "search_result_limit": 5,  # 搜索结果数量限制
    "tavily_api_key": "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"  # Tavily API密钥，需自行设置        
}

# Agent配置
AGENT_CONFIG = {
    "max_iterations": 10,  # Agent最大迭代次数
    "verbose": True,  # 启用详细日志
    "return_intermediate_steps": True  # 返回中间步骤
}

# 工作流程配置
WORKFLOW_CONFIG = {
    "analysis_period": "month",  # 分析周期: week, month, quarter
    "event_priority_threshold": 0.7,  # 事件优先级阈值
    "sector_analysis_depth": 3  # 板块分析深度
}
