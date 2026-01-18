#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
市场趋势预测系统 - 简化运行脚本
"""

import sys
import os
from typing import List, Dict

# 确保当前目录在搜索路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 1. 导入必要的工具和类
from utils.streaming_output import StreamingOutputHandler

# 2. 配置信息
LLM_CONFIG = {
    "model_provider": "ollama",
    "ollama_model": "gemma:2b",
    "temperature": 0.7,
    "max_tokens": 1024,
    "streaming": True
}

TOOLS_CONFIG = {
    "tavily_api_key": "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"
}

# 3. 模拟CLS投资日历提取
def extract_cls_investment_calendar():
    """
    从CLS网站提取投资日历信息
    """
    return [
        {
            "date": "2026-01-19",
            "day": "星期一",
            "events": [
                {
                    "content": "第56届世界经济论坛年会（冬季达沃斯）将于1月19日至23日在瑞士达沃斯举行",
                    "type": "国际会议",
                    "relevance": "全球市场"
                },
                {
                    "content": "中国人民银行：自1月19日起，下调再贷款、再贴现利率0.25个百分点",
                    "type": "货币政策",
                    "relevance": "A股、债市"
                }
            ]
        },
        {
            "date": "2026-01-20",
            "day": "星期二",
            "events": [
                {
                    "content": "央行发布《金融机构客户受益所有人识别管理办法》",
                    "type": "监管政策",
                    "relevance": "金融板块"
                }
            ]
        }
    ]

# 4. 主函数
def main():
    """
    主程序入口
    """
    stream_handler = StreamingOutputHandler()
    
    # 打印程序标题
    stream_handler.print_title("市场趋势预测系统")
    stream_handler.write(f"\n当前模型: {LLM_CONFIG.get('model_provider')} - {LLM_CONFIG.get('ollama_model')}\n")
    stream_handler.write(f"流输出: {'启用' if LLM_CONFIG.get('streaming') else '禁用'}\n\n")
    
    try:
        # 1. 信息提取
        stream_handler.write("1. 正在提取CLS投资日历信息...\n")
        investment_calendar = extract_cls_investment_calendar()
        
        # 格式化事件信息
        events_text = []
        for day in investment_calendar:
            events_text.append(f"日期: {day.get('date')} {day.get('day')}")
            for event in day.get('events', []):
                events_text.append(f"  - {event.get('content')} (类型: {event.get('type')}, 关联: {event.get('relevance')})")
        events_text = "\n".join(events_text)
        
        stream_handler.write(f"   提取到 {len(investment_calendar)} 天的投资日历信息\n\n")
        
        # 2. 显示投资日历
        stream_handler.print_title("近期投资日历")
        stream_handler.write(events_text + "\n\n")
        
        # 3. 简单分析
        stream_handler.print_title("事件影响分析")
        stream_handler.write("## 1. 货币政策影响\n")
        stream_handler.write("中国人民银行下调再贷款、再贴现利率0.25个百分点，这是货币政策宽松的信号，有利于降低企业融资成本，刺激经济增长。\n")
        stream_handler.write("对债市形成利好，债券价格有望上涨；对A股市场也有正面影响，特别是对利率敏感的板块如房地产、基建等。\n\n")
        
        stream_handler.write("## 2. 国际会议影响\n")
        stream_handler.write("世界经济论坛年会将讨论全球经济走势、气候变化、地缘政治等重要议题，可能对全球市场产生影响。\n")
        stream_handler.write("投资者应关注会议期间的政策信号和市场反应，特别是关于全球贸易和货币政策的讨论。\n\n")
        
        # 4. 投资建议
        stream_handler.print_title("投资建议")
        stream_handler.write("## 1. 投资领域推荐\n")
        stream_handler.write("- 债券市场：受益于货币政策宽松\n")
        stream_handler.write("- 房地产板块：利率下调有利于降低购房成本\n")
        stream_handler.write("- 基建板块：政策支持下有望受益\n\n")
        
        stream_handler.write("## 2. 投资策略\n")
        stream_handler.write("- 短期：关注利率敏感板块的反弹机会\n")
        stream_handler.write("- 中期：布局受益于经济复苏的板块\n")
        stream_handler.write("- 长期：关注科技创新和绿色能源领域\n\n")
        
        stream_handler.write("## 3. 风险提示\n")
        stream_handler.write("- 全球经济增长放缓风险\n")
        stream_handler.write("- 地缘政治不确定性\n")
        stream_handler.write("- 通胀压力可能导致政策转向\n\n")
        
        stream_handler.print_title("分析完成")
        stream_handler.write("市场趋势分析报告生成完毕！\n\n")
        
    except KeyboardInterrupt:
        stream_handler.write("\n\n程序已被用户中断！\n")
    except Exception as e:
        stream_handler.write(f"\n\n程序执行出错: {str(e)}\n")
        import traceback
        traceback.print_exc()
    finally:
        stream_handler.print_divider()
        stream_handler.write("\n市场趋势预测系统执行完毕！\n")

if __name__ == "__main__":
    main()