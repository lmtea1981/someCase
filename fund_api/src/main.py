import os
import sys
import schedule
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils import load_config, load_funds_config, get_config_dir
from src.fund import Fund

# 退出标记
exit_flag = False

def update_all_funds():
    """更新所有基金数据"""
    global exit_flag
    now = datetime.now()

    print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] 开始更新基金数据...")

    # 加载基金配置
    config_dir = get_config_dir()
    funds_config = load_funds_config(os.path.join(config_dir, 'funds.yaml'))

    # 创建基金实例并更新数据
    for fund_info in funds_config:
        code = fund_info.get('code')
        name = fund_info.get('name')
        enabled = fund_info.get('enabled', 1)
        fund = Fund(code, name, enabled)
        fund.update()

    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 基金数据更新完成！\n")
    print("$" * 60)
    print("\n")

    # ===================== 修复：15点判断 =====================
    # 用 datetime 方式判断，绝对不报错
    if now.hour >= 15:
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 已完成收盘最后一次更新，程序自动退出！")
        exit_flag = True
    # =========================================================

def main():
    global exit_flag
    # 加载配置
    config_dir = get_config_dir()
    config = load_config(os.path.join(config_dir, 'config.yaml'))
    update_interval = config.get('update_interval', 15)

    print(f"A股基金实时估值系统启动")
    print(f"更新间隔: {update_interval} 分钟")
    print("=" * 60)

    # 立即执行一次更新
    update_all_funds()

    # 设置定时任务
    schedule.every(update_interval).minutes.do(update_all_funds)

    # 启动循环
    while True:
        if exit_flag:
            break

        schedule.run_pending()

        # 退出判断（sleep 之前）
        now = datetime.now()
        if now.hour >= 15:
            print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] 当前时间已过15点，直接终止程序！")
            break

        # 防卡顿：拆成60次1秒，不卡CMD
        for _ in range(60):
            if exit_flag:
                break
            time.sleep(1)

if __name__ == "__main__":
    main()
