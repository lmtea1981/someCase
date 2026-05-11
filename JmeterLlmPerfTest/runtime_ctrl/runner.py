"""
===================================
@Author: Djl
@Date: 2026/5/7 15:06
@Description: 
===================================
"""
# -*- coding: utf-8 -*-
import time
from config.settings import ROUND_INTERVAL_SECONDS

class RuntimeController:
    def __init__(self):
        self.interval = ROUND_INTERVAL_SECONDS

    def wait_next(self):
        print(f"\n等待 {self.interval}s 后开始下一轮...\n")
        time.sleep(self.interval)

    def log_round(self, r, c):
        print(f"\n===== 第 {r} 轮 | 并发：{c} =====")
