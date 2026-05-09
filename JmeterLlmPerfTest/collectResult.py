"""
===================================
@Author: Djl
@Date: 2026/5/8 14:32
@Description: 
===================================
"""
# -*- coding: utf-8 -*-
import os
import pandas as pd
import csv

# 常量定义
JMETER_DURATION = 0  # 可根据实际需求修改
TARGET_FILE_SUFFIX = ".jtl"  # 目标文件后缀
FILE_PREFIX = "result_"  # JTL文件名前缀


def calculate_jtl_metrics(jtl_path: str):
    """
    解析单个JTL文件，计算性能指标（严格使用你提供的计算逻辑）
    :param jtl_path: JTL文件完整路径
    :return: 指标字典
    """
    try:
        df = pd.read_csv(jtl_path)
    except Exception as e:
        # 文件读取失败，返回默认异常值
        return {
            "tps": 0.0,
            "avg_rt": 99999.0,
            "p90_rt": 99999.0,
            "error_rate": 100.0,
            "duration": JMETER_DURATION
        }

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

    total = len(df)
    success_count = len(df[df['success'] == True]) if 'success' in df.columns else 0
    fail_count = total - success_count

    # JMeter 官方耗时计算逻辑
    start_time = df['timeStamp'].min()
    end_time = df['timeStamp'].max() + df['elapsed'].max()
    duration = (end_time - start_time) / 1000

    # 核心指标计算
    tps = total / duration if duration > 0 else 0
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


def extract_concurrency_from_filename(filename: str):
    """
    从文件名提取并发量，如 result_100.jtl → 100
    :param filename: 文件名
    :return: 并发量（整数），解析失败返回0
    """
    if not filename.startswith(FILE_PREFIX) or not filename.endswith(TARGET_FILE_SUFFIX):
        return 0

    # 截取中间数字部分
    num_str = filename.replace(FILE_PREFIX, "").replace(TARGET_FILE_SUFFIX, "")
    try:
        return int(num_str)
    except ValueError:
        return 0


def aggregate_jtl_results(root_dir: str, output_csv: str = "agg_result.csv"):
    """
    遍历根目录，聚合所有JTL文件指标并写入CSV
    :param root_dir: 根目录（存放时间戳子目录的文件夹）
    :param output_csv: 输出CSV路径
    """
    # CSV表头
    headers = ["目录名", "并发量", "tps", "avg_rt", "p90_rt", "error_rate"]
    result_data = []

    # 遍历根目录下的所有一级子目录
    for dir_name in os.listdir(root_dir):
        dir_path = os.path.join(root_dir, dir_name)

        # 只处理文件夹，跳过文件
        if not os.path.isdir(dir_path):
            continue

        # 遍历目录中的所有文件
        for file_name in os.listdir(dir_path):
            # 只处理符合规则的 result_*.jtl 文件
            concurrency = extract_concurrency_from_filename(file_name)
            if concurrency == 0:
                continue

            # 计算指标
            jtl_full_path = os.path.join(dir_path, file_name)
            metrics = calculate_jtl_metrics(jtl_full_path)

            # 组装一行数据
            row = [
                dir_name,
                concurrency,
                metrics["tps"],
                metrics["avg_rt"],
                metrics["p90_rt"],
                metrics["error_rate"]
            ]
            result_data.append(row)
            print(f"✅ 处理完成：目录={dir_name}，并发={concurrency}")

    # ====================== 核心排序：目录名升序 → 并发量升序 ======================
    result_data.sort(key=lambda x: (x[0], x[1]))
    # ==========================================================================

    # 写入CSV文件
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(result_data)

    print(f"\n🎉 所有文件处理完成，结果已保存到：{output_csv}")


if __name__ == "__main__":
    # ====================== 请修改这里的根目录 ======================
    ROOT_DIRECTORY = "./reports"  # 你的根目录（包含20260508_134506这类子目录的文件夹）
    # ===============================================================

    # 执行聚合分析
    aggregate_jtl_results(ROOT_DIRECTORY)
