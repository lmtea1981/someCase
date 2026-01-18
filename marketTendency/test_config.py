#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置文件测试脚本
"""

import sys
import os

# 添加当前目录到Python搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
print(f"当前工作目录: {os.getcwd()}")
print(f"脚本目录: {current_dir}")
print(f"Python搜索路径: {sys.path}")

# 查看config模块的位置
import importlib.util
config_path = importlib.util.find_spec('config').origin
print(f"\n实际加载的config.py路径: {config_path}")

# 直接读取文件内容
with open(config_path, 'r', encoding='utf-8') as f:
    config_content = f.read()
    print(f"\n实际config.py内容:")
    print(config_content)

# 导入配置
from config import LLM_CONFIG

print("\n读取到的配置内容:")
print(f"model_provider: {LLM_CONFIG.get('model_provider')}")
print(f"ollama_model: {LLM_CONFIG.get('ollama_model')}")
print(f"temperature: {LLM_CONFIG.get('temperature')}")
print(f"streaming: {LLM_CONFIG.get('streaming')}")

# 测试LLMFactory
from llm.llm_factory import LLMFactory

print("\nLLMFactory模型信息:")
model_info = LLMFactory.get_model_info()
print(f"provider: {model_info['provider']}")
print(f"model: {model_info['model']}")

# 测试OllamaLLMIntegration
from llm.ollama_llm import OllamaLLMIntegration

print("\nOllamaLLMIntegration初始化:")
ollama_llm = OllamaLLMIntegration()
print(f"model_name: {ollama_llm.model_name}")
print(f"temperature: {ollama_llm.temperature}")
print(f"max_tokens: {ollama_llm.max_tokens}")
print(f"streaming: {ollama_llm.streaming}")
