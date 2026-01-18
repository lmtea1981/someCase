#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试模块导入脚本
"""

import sys
import os

# 添加当前目录到Python搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("当前工作目录:", os.getcwd())
print("Python搜索路径:", sys.path)

# 测试模块导入
try:
    print("\n1. 测试导入utils.streaming_output...")
    from utils.streaming_output import StreamingOutputHandler
    print("✓ utils.streaming_output导入成功")
except Exception as e:
    print(f"✗ utils.streaming_output导入失败: {e}")

try:
    print("\n2. 测试导入tools.cls_extractor_tool...")
    from tools.cls_extractor_tool import extract_cls_investment_calendar
    print("✓ tools.cls_extractor_tool导入成功")
except Exception as e:
    print(f"✗ tools.cls_extractor_tool导入失败: {e}")

try:
    print("\n3. 测试导入chains.event_chain...")
    from chains.event_chain import EventAnalysisChain
    print("✓ chains.event_chain导入成功")
except Exception as e:
    print(f"✗ chains.event_chain导入失败: {e}")

try:
    print("\n4. 测试导入llm.ollama_llm...")
    from llm.ollama_llm import OllamaLLMIntegration
    print("✓ llm.ollama_llm导入成功")
except Exception as e:
    print(f"✗ llm.ollama_llm导入失败: {e}")

print("\n测试完成!")
