"""
===================================
@Author: Djl
@Date: 2026/5/7 15:05
@Description: 
===================================
"""
# -*- coding: utf-8 -*-
# LLM 配置：支持本地Ollama / 线上模型
LLM_MODE = "local"  # local / online

OLLAMA_CONFIG = {
    "host": "http://localhost:11434",
    "model": "qwen3:8b"
}

ONLINE_LLM_CONFIG = {
    "api_key": "your-api-key",
    "base_url": "https://api.example.com/v1",
    "model": "gpt-4o-mini"
}

LLM_PROMPT = """
你是性能测试专家，分析以下压测数据：
1. 剔除异常数据（网络波动、服务重启、超时毛刺）
2. 若异常影响结果，给出复测建议
3. 找出最终拐点，并推荐三级基线专属门禁，公式：设拐点并发为P，安全基线 = P × 0.6、标准基线 = P × 0.8~0.85、临界基线 = P + 10% P 或固定上浮 5~15 并发
4. 输出格式：JSON，包含：is_abnormal、re_test、recommend_concurrency、reason
"""
