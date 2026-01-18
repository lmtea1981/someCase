#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试CLS投资日历提取工具
"""

import sys
import os

# 添加当前目录到Python搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.cls_extractor_tool import extract_cls_investment_calendar

def test_cls_extractor():
    """
    测试CLS投资日历提取工具
    """
    print("开始测试CLS投资日历提取工具...")
    
    try:
        # 调用提取工具
        result = extract_cls_investment_calendar()
        
        print(f"\n提取结果:")
        print(f"共提取到 {len(result)} 天的投资日历信息")
        
        # 打印详细信息
        for i, day in enumerate(result):
            if "error" in day:
                print(f"\n错误信息: {day['error']}")
                continue
                
            print(f"\n第 {i+1} 天: {day['date']} {day['day']}")
            print(f"  事件数量: {len(day['events'])}")
            
            # 打印前3个事件
            for j, event in enumerate(day['events'][:3]):
                print(f"  事件 {j+1}: {event['content']}")
                print(f"     类型: {event['type']}")
                print(f"     关联: {event['relevance']}")
            
            # 如果事件超过3个，显示剩余数量
            if len(day['events']) > 3:
                print(f"  ... 还有 {len(day['events']) - 3} 个事件")
        
        print("\n测试完成！")
        return True
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_cls_extractor()
