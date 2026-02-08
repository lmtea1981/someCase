import pandas as pd

# 读取生成的Excel文件
df = pd.read_excel('testdata_1.xlsx')

# 查看文件的基本信息
print('文件基本信息：')
print(f'行数：{len(df)}')
print(f'列数：{len(df.columns)}')
print('\n列名：')
print(df.columns.tolist())

# 查看前5行数据
print('\n前5行数据：')
print(df.head())
