"""
===================================
@Author: Djl
@Date: 2026/5/7 15:06
@Description: 
===================================
"""
# -*- coding: utf-8 -*-
import os
import time
import subprocess
import pandas as pd
from config.settings import (
    JMETER_BIN_PATH,
    JMETER_SCRIPT_PATH,
    REPORT_ROOT_DIR,
    JMETER_DURATION
)

class JMeterController:
    def __init__(self):
        self.script = JMETER_SCRIPT_PATH
        self.duration = JMETER_DURATION
        self.report_root = REPORT_ROOT_DIR

        # 整个压测过程只创建 1 次 年月日_时分秒 目录
        self.run_dir = self._create_run_directory()

    def _create_run_directory(self):
        """创建本次运行的独立目录：年月日_时分秒"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(self.report_root, timestamp)
        os.makedirs(run_dir, exist_ok=True)
        return run_dir

    def run_test(self, concurrency):
        """执行JMeter压测，指定并发数"""
        # 文件名：result_50.jtl
        jtl_file = f"result_{concurrency}.jtl"
        jtl_path = os.path.join(self.run_dir, jtl_file)
        cmd = (
            f"{JMETER_BIN_PATH} -n -t {self.script} "
            f"-Jthreads={concurrency} "
            f"-l {jtl_path} -e -o {self.run_dir}/report_{concurrency}"
        )
        # subprocess.run(cmd, shell=True, check=True)
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return self._parse(concurrency)

    def _parse(self, concurrency):
        """解析JMeter结果文件"""
        jtl_file = f"{self.run_dir}/result_{concurrency}.jtl"
        df = pd.read_csv(jtl_file)

        sample_count = len(df)
        error_count = len(df[df['success'] == False]) if 'success' in df.columns else 0

        if sample_count == 0:
            return {
                "tps": 0.0,
                "avg_rt": 99999.0,
                "p90_rt": 99999.0,
                "error_rate": 100.0,
                "duration": JMETER_DURATION
            }

        # success_count = len(df[df['success'] == True])
        # duration = (df['timeStamp'].max() - df['timeStamp'].min()) / 1000
        # tps = success_count / duration if duration > 0 else 0
        total = len(df)
        success_count = len(df[df['success'] == True])
        fail_count = total - success_count

        # JMeter 官方耗时：第一条请求开始 → 最后一条请求开始 + 最后一条耗时
        start_time = df['timeStamp'].min()
        end_time   = df['timeStamp'].max() + df['elapsed'].max()
        duration = (end_time - start_time) / 1000

        # JMeter TPS = 总请求数 / 总耗时（包含失败）
        tps = total / duration if duration > 0 else 0
        # tps = sample_count / JMETER_DURATION
        avg_rt = df['elapsed'].mean() if 'elapsed' in df.columns else 99999
        p90_rt = df['elapsed'].quantile(0.90) if 'elapsed' in df.columns else 99999
        error_rate = (error_count / sample_count) * 100

        return {
            "tps": round(float(tps), 2),
            "avg_rt": round(float(avg_rt), 2),
            "p90_rt": round(float(p90_rt), 2),
            "error_rate": round(float(error_rate), 2),
            "duration": JMETER_DURATION
        }
