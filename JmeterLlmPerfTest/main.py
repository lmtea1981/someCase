"""
===================================
@Author: Djl
@Date: 2026/5/7 15:07
@Description: 
===================================
"""
# -*- coding: utf-8 -*-
import json
from config.settings import *
from runtime_ctrl.runner import RuntimeController
from core.jmeter_controller import JMeterController
from core.inflection_checker import InflectionChecker
from core.llm_analyzer import LLMAnalyzer

def calc_next(prev_tps, curr_tps, curr_concurrency):
    growth = (curr_tps - prev_tps) / prev_tps if prev_tps > 0 else 0
    if growth >= 0.3:
        return int(curr_concurrency * 2)
    elif 0.1 <= growth < 0.3:
        return int(curr_concurrency * 1.4)
    else:
        return int(curr_concurrency * 1.15)

def main():
    runner = RuntimeController()
    jmeter = JMeterController()
    checker = InflectionChecker()
    llm = LLMAnalyzer()

    concurrency = INIT_CONCURRENCY
    history = []
    retest_needed = False
    retest_concurrency = 0

    print("========== 性能拐点测试启动 ==========")

    for round_idx in range(1, MAX_ROUNDS + 1):
        runner.log_round(round_idx, concurrency)
        res = jmeter.run_test(concurrency)
        history.append({
            "round": round_idx,
            "concurrency": concurrency,
            **res
        })
        print(f"结果：{res}")

        # 拐点判定
        hit, reason = checker.check(res, history[:-1])
        if hit:
            print(f"\n✅ 触发拐点：{reason}")

            # ====================== 【全局更正：所有 ×2 触发拐点都回踩 ×1.5】 ======================
            # 判断当前并发是否由上一轮 ×2 得到
            if len(history) >= 2:
                prev_concurrency = history[-2]["concurrency"]
                if concurrency == prev_concurrency * 2:
                    print(f"⚠️ 当前并发 {concurrency} 是由上一轮 ×2 触发拐点，启动回踩：×1.5")
                    retest_concurrency = int(prev_concurrency * RETEST_MULTIPLIER)
                    retest_needed = True
                    break
            break

        # 第二轮强制翻倍
        if round_idx == 1:
            concurrency *= 2
            print(f"🔁 第二轮并发强制翻倍：{concurrency}")
        else:
            # 第三轮开始按TPS计算
            if len(history) >= 2:
                prev_tps = history[-2]["tps"]
                curr_tps = res["tps"]
                concurrency = calc_next(prev_tps, curr_tps, concurrency)

        runner.wait_next()

    # ====================== 回踩执行 ======================
    if retest_needed:
        round_idx += 1
        print(f"\n===== 回踩测试 | 并发：{retest_concurrency} =====")
        res_retest = jmeter.run_test(retest_concurrency)
        history.append({
            "round": round_idx,
            "concurrency": retest_concurrency,
            **res_retest
        })
        print(f"回踩结果：{res_retest}")
        print("\n✅ 回踩完成，获取更精准拐点")

    # LLM分析
    print("\n========== LLM 智能分析报告 ==========")
    report = llm.analyze(history)
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
