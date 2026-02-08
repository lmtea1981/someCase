import pandas as pd

# 读取testdata_1.xlsx文件
print("读取testdata_1.xlsx文件...")
df = pd.read_excel("./testdata_1.xlsx")

# 选择关键列
key_columns = ['ID', '*用例标题', '*测试步骤', '*预期结果', '描述']
df_key = df[key_columns]

# 打印前10行数据
print("\n前10行测试用例关键信息：")
for i in range(min(10, len(df_key))):
    row = df_key.iloc[i]
    print(f"\n用例ID: {row['ID']}")
    print(f"用例标题: {row['*用例标题']}")
    print(f"测试步骤: {row['*测试步骤']}")
    print(f"预期结果: {row['*预期结果']}")
    print(f"描述: {row['描述']}")
    print("-" * 50)
