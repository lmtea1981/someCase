"""
===================================
@Author: Djl
@Date: 2026/5/7 14:50
@Description: 
===================================
"""
# -*- coding: utf-8 -*-
# ====================== 性能拐点测试配置 ======================
# 初始并发
INIT_CONCURRENCY = 50

# 拐点阈值
RT_THRESHOLD_MS = 3000
ERROR_RATE_THRESHOLD = 0.001  # 0.1%

# 加压步进规则
INCREASE_HIGH = 1.0    # TPS≥30% → ×2
INCREASE_MID = 0.4     # 10%~30% → +40%
INCREASE_LOW = 0.15    # <10% → +15%

# 回踩规则：×2触发拐点 → 回踩原并发×1.5
RETEST_MULTIPLIER = 1.5

# 执行控制
MAX_ROUNDS = 20
ROUND_INTERVAL_SECONDS = 10

# JMeter 配置
JMETER_BIN_PATH = r"D:/jmeter_parm.cmd"     # JMeter 命令路径
JMETER_SCRIPT_PATH = "./jmx/test_api_oo.jmx"  # 压测脚本
# JMETER_RESULT_PATH = "./reports/jmeter_result.csv"
REPORT_ROOT_DIR = "./reports"
JMETER_DURATION = 15  # 新增：压测执行时长（秒）
