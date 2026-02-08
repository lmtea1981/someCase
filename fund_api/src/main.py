import os
import sys
import schedule
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils import load_config, load_funds_config, get_config_dir
from src.fund import Fund

def update_all_funds():
    """更新所有基金数据"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始更新基金数据...")
    
    # 加载基金配置
    config_dir = get_config_dir()
    funds_config = load_funds_config(os.path.join(config_dir, 'funds.yaml'))
    
    # 创建基金实例并更新数据
    for fund_info in funds_config:
        code = fund_info.get('code')
        name = fund_info.get('name')
        enabled = fund_info.get('enabled', 1)  # 默认值为1
        fund = Fund(code, name, enabled)
        fund.update()
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 基金数据更新完成！")

def main():
    """主函数"""
    # 加载配置
    config_dir = get_config_dir()
    config = load_config(os.path.join(config_dir, 'config.yaml'))
    update_interval = config.get('update_interval', 15)  # 默认15分钟
    
    print(f"A股基金实时估值系统启动")
    print(f"更新间隔: {update_interval} 分钟")
    print("=" * 60)
    
    # 立即执行一次更新
    update_all_funds()
    
    # 设置定时任务
    schedule.every(update_interval).minutes.do(update_all_funds)
    
    # 启动定时任务循环
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每秒检查一次

if __name__ == "__main__":
    main()