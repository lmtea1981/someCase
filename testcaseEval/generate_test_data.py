import pandas as pd
import random
from datetime import datetime, timedelta

# 定义列名
columns = [
    '序号', 'ID', '*用例标题', '前置条件', '*测试步骤', '*预期结果', '优先级', 
    '*用例目录', '*用例类型', '*执行方式', '关联故事编号', '关联产品需求编号', 
    '描述', '标签', '编写方式', '关联自动化脚本数', '所属项目', '更新人', 
    '更新时间', '创建人', '创建时间'
]

# 生成随机数据
priority_list = ['P0', 'P1', 'P2', 'P3']
case_type_list = ['功能用例', '性能用例', '安全用例', '兼容性用例', '回归用例']
execution_way_list = ['手工测试', '自动化测试', 'UI自然语言测试']
catalog_list = ['F-ITTMP/UI自然语言测试-UAT', 'F-ITTMP/功能测试-SIT', 'F-ITTMP/性能测试', 'F-ITTMP/安全测试']
writing_way_list = ['AI生成-用例库', '人工编写', '导入']
project_list = ['2026年IPM_年度版本项目', '2026年CRM_升级项目', '2026年ERP_重构项目']
user_list = ['陈芳芳(chenff24)', '张三(zhangsan)', '李四(lisi)', '王五(wangwu)']

# 生成20条数据
data = []
for i in range(20):
    # 生成随机日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    random_create_date = start_date + timedelta(days=random.randint(0, 30))
    random_update_date = random_create_date + timedelta(days=random.randint(0, 10))
    
    # 格式化日期
    create_date_str = random_create_date.strftime('%Y-%m-%d %H:%M:%S')
    update_date_str = random_update_date.strftime('%Y-%m-%d %H:%M:%S')
    
    # 生成随机ID
    random_id = f'AAAM{random.randint(100000, 999999)}'
    story_id = f'AAAM{random.randint(100000, 999999)}'
    
    # 生成随机测试步骤和预期结果
    step_count = random.randint(2, 5)
    steps = []
    expected_results = []
    for j in range(step_count):
        steps.append(f'【{j+1}】执行步骤{j+1}')
        expected_results.append(f'【{j+1}】预期结果{j+1}')
    
    # 组装数据
    row = [
        i+1,  # 序号
        random_id,  # ID
        f'测试用例标题_{i+1}',  # *用例标题
        f'前置条件_{i+1}',  # 前置条件
        '\n'.join(steps),  # *测试步骤
        '\n'.join(expected_results),  # *预期结果
        random.choice(priority_list),  # 优先级
        random.choice(catalog_list),  # *用例目录
        random.choice(case_type_list),  # *用例类型
        random.choice(execution_way_list),  # *执行方式
        story_id,  # 关联故事编号
        '',  # 关联产品需求编号
        f'测试用例描述_{i+1}',  # 描述
        f'标签_{i+1}',  # 标签
        random.choice(writing_way_list),  # 编写方式
        random.randint(0, 5),  # 关联自动化脚本数
        random.choice(project_list),  # 所属项目
        random.choice(user_list),  # 更新人
        update_date_str,  # 更新时间
        random.choice(user_list),  # 创建人
        create_date_str  # 创建时间
    ]
    data.append(row)

# 创建DataFrame
df = pd.DataFrame(data, columns=columns)

# 保存到Excel文件
file_path = 'testdata_1.xlsx'
df.to_excel(file_path, index=False, engine='openpyxl')

print(f'测试数据已成功生成并保存到 {file_path}，共 {len(df)} 条记录。')
