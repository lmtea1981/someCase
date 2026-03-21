import requests
import time
import random
import re
import json
import yaml
import os
from typing import Optional, Dict, Any, List
import csv
from datetime import datetime

# 获取配置目录
def get_config_dir():
    """获取配置目录路径"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')

# 加载基金配置
def load_funds_config(funds_file):
    """加载基金配置文件"""
    with open(funds_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config.get('funds', [])

# 字段含义映射（方便理解和展示）
FIELD_MAP = {
    "FSRQ": "发布日期",
    "DWJZ": "单位净值",
    "LJJZ": "累计净值",
    "JZZZL": "净值增长率(%)",
    "SGZT": "申购状态",
    "SHZT": "赎回状态",
    "NAVTYPE": "净值类型",
    "ACTUALSYI": "实际收益率",
    "FHFCZ": "分红方式",
    "FHFCBZ": "分红标志",
    "FHSP": "分红送配"
}

def get_fund_history_net_value(
    fund_code: str,
    page_index: int = 1,
    page_size: int = 20,
    start_date: Optional[str] = "",
    end_date: Optional[str] = ""
) -> Dict[str, Any]:
    """
    参数化请求东方财富基金历史净值接口
    
    Args:
        fund_code: 基金代码，如"008888"
        page_index: 页码，默认1
        page_size: 每页条数，默认20
        start_date: 开始日期，格式"YYYY-MM-DD"，默认空
        end_date: 结束日期，格式"YYYY-MM-DD"，默认空
    
    Returns:
        解析后的基金净值数据字典
    """
    # 1. 基础配置
    url = "https://api.fund.eastmoney.com/f10/lsjz"
    
    # 2. 参数化配置（核心）
    params = {
        "callback": f"jQuery1830{random.randint(1000000000000000000, 9999999999999999999)}_{int(time.time() * 1000)}",
        "fundCode": fund_code,
        "pageIndex": page_index,
        "pageSize": page_size,
        "startDate": start_date,
        "endDate": end_date,
        "_": int(time.time() * 1000)
    }
    
    # 3. 请求头（模拟浏览器，避免被拦截）
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://fund.eastmoney.com/",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    try:
        # 4. 发送请求
        response = requests.get(
            url=url,
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()  # 抛出HTTP错误
        
        # 打印原始响应（调试用）
        print("原始响应内容前500字符：")
        print(response.text[:500])
        print("-" * 50)
        
        # 5. 解析JSONP响应（优化正则，更宽松的匹配）
        # 优化后的正则：匹配 jQuery任意数字_任意数字(...) 格式，忽略前后空格和结尾分号
        jsonp_pattern = re.compile(r'jQuery\d+_\d+\s*\(\s*(.*?)\s*\)\s*;?', re.DOTALL)
        match = jsonp_pattern.search(response.text)
        
        if not match:
            # 终极方案：如果正则匹配失败，直接截取括号内的内容
            print("正则匹配失败，尝试手动截取JSON内容...")
            # 找到第一个 ( 和最后一个 ) 的位置
            start_idx = response.text.find('(')
            end_idx = response.text.rfind(')')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response.text[start_idx+1:end_idx].strip()
            else:
                raise ValueError("未匹配到JSONP数据，也无法手动截取")
        else:
            json_str = match.group(1).strip()
        
        # 6. 转换为字典
        result = json.loads(json_str)
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"JSON解析失败：{e}")
        print(f"待解析的JSON字符串：{json_str[:500]}")
        return {}
    except Exception as e:
        print(f"未知错误：{e}")
        return {}

def format_fund_data(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    格式化基金数据，只保留核心字段并添加中文说明
    
    Args:
        raw_data: 原始接口返回数据
    
    Returns:
        格式化后的基金净值列表
    """
    formatted_list = []
    if not raw_data or "Data" not in raw_data or "LSJZList" not in raw_data["Data"]:
        print("数据格式异常，缺少关键字段")
        print(f"原始数据结构：{list(raw_data.keys()) if raw_data else '空'}")
        return formatted_list
    
    for item in raw_data["Data"]["LSJZList"]:
        formatted_item = {
            "发布日期": item.get("FSRQ", ""),
            "单位净值": item.get("DWJZ", ""),
            "累计净值": item.get("LJJZ", ""),
            "净值增长率(%)": item.get("JZZZL", ""),
            "申购状态": item.get("SGZT", ""),
            "赎回状态": item.get("SHZT", "")
        }
        formatted_list.append(formatted_item)
    
    return formatted_list

def print_fund_data(formatted_data: List[Dict[str, Any]], fund_code: str):
    """
    友好地打印基金数据
    
    Args:
        formatted_data: 格式化后的基金数据
        fund_code: 基金代码
    """
    if not formatted_data:
        print("暂无基金数据")
        return
    
    print(f"\n========== 基金 {fund_code} 净值数据 ==========")
    # 打印表头
    headers = list(formatted_data[0].keys())
    header_line = " | ".join([f"{h:<12}" for h in headers])
    print(header_line)
    print("-" * len(header_line.replace(" | ", "")) * 2)
    
    # 打印数据行
    for item in formatted_data:
        data_line = " | ".join([f"{item[h]:<12}" for h in headers])
        print(data_line)
    
    print(f"\n总计：{len(formatted_data)} 条记录")

def save_fund_data_to_csv(formatted_data: List[Dict[str, Any]], fund_code: str, fund_name: str = "", save_path: str = ""):
    """
    将基金数据保存为CSV文件
    
    Args:
        formatted_data: 格式化后的基金数据
        fund_code: 基金代码
        fund_name: 基金名称
        save_path: 保存路径，为空则使用默认路径
    """
    if not formatted_data:
        print("暂无数据可保存")
        return
    
    # 创建history目录
    history_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'history')
    os.makedirs(history_dir, exist_ok=True)
    
    # 默认保存路径：使用基金名称命名
    if not save_path:
        if fund_name:
            # 去除文件名中可能的非法字符
            safe_name = fund_name.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
            save_path = os.path.join(history_dir, f"{safe_name}({fund_code})_净值数据.csv")
        else:
            save_path = os.path.join(history_dir, f"fund_{fund_code}_净值数据.csv")
    
    try:
        # 检查文件是否存在
        existing_data = []
        if os.path.exists(save_path):
            # 读取现有数据
            with open(save_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                existing_data = list(reader)
        
        # 合并数据并去重
        all_data = existing_data + formatted_data
        
        # 按发布日期去重，保留最新的记录
        seen_dates = set()
        unique_data = []
        for item in all_data:
            date = item.get('发布日期')
            if date not in seen_dates:
                seen_dates.add(date)
                unique_data.append(item)
        
        # 按发布日期倒序排序
        unique_data.sort(key=lambda x: x.get('发布日期', ''), reverse=True)
        
        # 保存数据
        with open(save_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=unique_data[0].keys() if unique_data else formatted_data[0].keys())
            writer.writeheader()
            writer.writerows(unique_data)
        print(f"\n数据已成功保存到：{save_path}")
        print(f"保存记录数：{len(unique_data)}")
        print(f"去重后新增记录数：{len(unique_data) - len(existing_data)}")
    except Exception as e:
        print(f"保存CSV失败：{e}")

# ------------------- 主函数：一站式使用 -------------------
def main():
    # 加载基金配置
    config_dir = get_config_dir()
    funds_file = os.path.join(config_dir, 'funds.yaml')
    funds = load_funds_config(funds_file)
    
    if not funds:
        print("未找到基金配置，请确保funds.yaml文件存在且包含基金信息")
        return
    
    # 显示基金列表
    print("可用基金列表：")
    for i, fund in enumerate(funds, 1):
        code = fund.get('code')
        name = fund.get('name', '未知名称')
        enabled = fund.get('enabled', 0)
        print(f"{i}. {name} ({code}) {'[启用]' if enabled == 1 else '[禁用]'}")
    
    # 添加全选选项
    print(f"{len(funds) + 1}. 全选所有基金")
    
    # 选择基金
    selected_funds = []
    while True:
        try:
            choice = int(input("请选择要查询的基金编号："))
            if 1 <= choice <= len(funds):
                # 选择单个基金
                selected_fund = funds[choice - 1]
                selected_funds = [selected_fund]
                break
            elif choice == len(funds) + 1:
                # 全选所有基金
                selected_funds = funds
                print("已选择所有基金")
                break
            else:
                print(f"请输入1到{len(funds) + 1}之间的数字")
        except ValueError:
            print("请输入有效的数字")
    
    # 对于单个基金，设置FUND_CODE和FUND_NAME
    if len(selected_funds) == 1:
        selected_fund = selected_funds[0]
        FUND_CODE = selected_fund.get('code')
        FUND_NAME = selected_fund.get('name', '未知名称')
    
    # 选择页码范围（1~6）
    start_page = 1
    end_page = 1
    
    # 询问是否查询多个页码
    while True:
        page_range = input("是否查询多个页码？(y/n)：").lower()
        if page_range in ['y', 'n']:
            break
        print("请输入y或n")
    
    if page_range == 'y':
        # 查询多个页码
        while True:
            try:
                start_page = int(input("请输入起始页码（1及以上）："))
                if start_page >= 1:
                    break
                else:
                    print("请输入1及以上的数字")
            except ValueError:
                print("请输入有效的数字")
        
        while True:
            try:
                end_page = int(input("请输入结束页码（不小于起始页码）："))
                if end_page >= start_page:
                    break
                else:
                    print(f"请输入不小于{start_page}的数字")
            except ValueError:
                print("请输入有效的数字")
        
        print(f"已选择页码范围：{start_page} - {end_page}")
    else:
        # 查询单个页码
        while True:
            try:
                start_page = int(input("请输入页码（1及以上）："))
                if start_page >= 1:
                    end_page = start_page
                    break
                else:
                    print("请输入1及以上的数字")
            except ValueError:
                print("请输入有效的数字")
        
        print(f"已选择页码：{start_page}")
    
    # 其他配置参数
    PAGE_SIZE = 20                # 每页条数
    START_DATE = ""     # 开始日期（可选）
    END_DATE = ""       # 结束日期（可选）
    
    # 处理选择的基金
    for fund in selected_funds:
        FUND_CODE = fund.get('code')
        FUND_NAME = fund.get('name', '未知名称')
        
        print(f"\n======================================")
        print(f"查询基金：{FUND_NAME} ({FUND_CODE})")
        
        # 处理页码范围
        for page_index in range(start_page, end_page + 1):
            print(f"\n页码：{page_index}")
            
            # 1. 获取原始数据
            raw_data = get_fund_history_net_value(
                fund_code=FUND_CODE,
                page_index=page_index,
                page_size=PAGE_SIZE,
                start_date=START_DATE,
                end_date=END_DATE
            )
            
            if not raw_data:
                print("获取基金数据失败")
                continue
            
            # 打印原始数据的关键信息（调试用）
            print(f"原始数据 - 总记录数：{raw_data.get('TotalCount', '未知')}")
            print(f"原始数据 - 页码：{raw_data.get('PageIndex', '未知')}")
            print(f"原始数据 - 每页条数：{raw_data.get('PageSize', '未知')}")
            
            # 2. 格式化数据
            formatted_data = format_fund_data(raw_data)
            
            # 3. 打印数据
            print_fund_data(formatted_data, FUND_CODE)
            
            # 4. 保存为CSV（可选）
            save_fund_data_to_csv(formatted_data, FUND_CODE, FUND_NAME)
            
            # 5. 提取关键统计信息
            if formatted_data:
                latest_data = formatted_data[0]
                print(f"\n关键信息：")
                print(f"最新净值日期：{latest_data['发布日期']}")
                print(f"最新单位净值：{latest_data['单位净值']}")
                print(f"最新净值增长率：{latest_data['净值增长率(%)']}%")
                print(f"申购状态：{latest_data['申购状态']}")
                print(f"赎回状态：{latest_data['赎回状态']}")
            
            # 避免请求过于频繁
            if page_index < end_page:
                time.sleep(1)

if __name__ == "__main__":
    main()