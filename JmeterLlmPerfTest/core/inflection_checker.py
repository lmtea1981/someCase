"""
===================================
@Author: Djl
@Date: 2026/5/7 15:07
@Description: 
===================================
"""
# -*- coding: utf-8 -*-
from config.settings import RT_THRESHOLD_MS, ERROR_RATE_THRESHOLD

class InflectionChecker:
    def __init__(self):
        self.rt_max = RT_THRESHOLD_MS
        self.err_max = ERROR_RATE_THRESHOLD * 100

    def check(self, current, history):
        # 规则1：RT超标
        if current["avg_rt"] > self.rt_max or current["p90_rt"] > self.rt_max:
            return True, "RT超过阈值"

        # 规则2：错误率超标
        if current["error_rate"] > self.err_max:
            return True, "错误率超标"

        # 规则3：TPS连续下跌/震荡
        if len(history) >= 2:
            h1 = history[-1]["tps"]
            h2 = history[-2]["tps"]
            if current["tps"] <= h1 <= h2:
                return True, "TPS连续下跌/震荡"

        # 规则4：TPS-RT背离
        if len(history) >= 1:
            last = history[-1]
            tps_up = (current["tps"] - last["tps"]) / last["tps"] if last["tps"] > 0 else 0
            rt_up = current["avg_rt"] > last["avg_rt"] * 1.5
            if tps_up < 0.05 and rt_up:
                return True, "TPS-RT走势背离"

        return False, "未到达拐点"
