import os
import pandas as pd

def process_csv_duplicates(folder_path):
    """
    读取指定目录下所有CSV文件，删除重复内容并保存，最后打印文件名和最后一行数据

    Args:
        folder_path (str): CSV文件所在目录路径
    """
    # 检查目录是否存在
    if not os.path.exists(folder_path):
        print(f"错误：目录 {folder_path} 不存在！")
        return

    # 遍历目录下的所有文件
    for filename in os.listdir(folder_path):
        # 筛选CSV文件（忽略大小写）
        if filename.lower().endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            # print("=" * 60)
            # print(f"正在处理文件：{filename}")

            try:
                # 读取CSV文件
                df = pd.read_csv(
                    file_path,
                    encoding='utf-8-sig',  # 兼容BOM，解决中文乱码
                    dtype=str  # 所有列强制为字符串类型，保留前置零
                )
                original_rows = len(df)

                if original_rows == 0:
                    print(f"文件 {filename} 为空，无需处理")
                    print(f"最后一行数据：无")
                    continue

                # 去重操作：默认按所有列去重，保留第一次出现的行
                # subset参数可指定按特定列去重，例如 subset=['date', 'code']
                df_deduplicated = df.drop_duplicates(keep='first')
                deduplicated_rows = len(df_deduplicated)
                removed_rows = original_rows - deduplicated_rows

                # 打印去重信息
                # print(f"去重前行数：{original_rows}")
                # print(f"去重后行数：{deduplicated_rows}")
                # print(f"删除重复行数：{removed_rows}")

                # 将去重后的数据保存回原文件（覆盖）
                # index=False 避免保存时生成额外的索引列
                df_deduplicated.to_csv(
                    file_path,
                    index=False,
                    encoding='utf-8-sig',    # 带BOM的UTF-8，Excel可正确识别
                    # 关键：保存时禁用数值自动转换（pandas默认会尝试转换，加此参数确保字符串）
                    float_format=None
                )
                # print(f"去重后的数据已保存到：{file_path}")

                # 获取去重后的最后一行数据（转为字典格式更易读）
                last_line = df_deduplicated.iloc[-1].to_dict()
                # print(f"最后一行数据：{last_line}")
                print(f"名称：{last_line['name']}，涨跌幅：{last_line['gszzl']}")

            except Exception as e:
                print(f"处理文件 {filename} 失败：{str(e)}")

if __name__ == "__main__":
    # 替换为你的CSV文件目录路径（相对/绝对路径均可）
    csv_folder = "data"
    process_csv_duplicates(csv_folder)