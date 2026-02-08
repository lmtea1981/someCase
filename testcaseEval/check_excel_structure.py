import pandas as pd

# 读取testdata_1.xlsx文件
print("读取testdata_1.xlsx文件...")
df = pd.read_excel("./testdata_1.xlsx")

# 打印文件的基本信息
print("\n文件基本信息：")
print(df.info())

# 打印前5行数据
print("\n前5行数据：")
print(df.head())

# 打印列名
print("\n列名：")
print(df.columns.tolist())

# 打印数据统计信息
print("\n数据统计信息：")
print(df.describe())

# 检查是否有空行
print("\n空行数量：")
print(df.isnull().all(axis=1).sum())

# 检查每列的非空值数量
print("\n每列非空值数量：")
print(df.count())
