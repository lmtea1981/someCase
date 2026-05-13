# -*- coding: utf-8 -*-

import sys, os.path
import json
import pytest

def run_tests():
    if "--org" in sys.argv:
        org_index = sys.argv.index("--org") + 1
        if org_index < len(sys.argv):
            org_script = sys.argv[org_index]
        else:
            raise ValueError("--org 参数后必须指定脚本名字")
    else:
        print("缺少‘--org’参数！")
        return 0
    # 解析命令行参数（示例格式：python runtest.py --tc /path/to/tc_1.yaml）
    if "--tc" in sys.argv:
        tc_index = sys.argv.index("--tc") + 1
        if tc_index < len(sys.argv):
            tc_path = sys.argv[tc_index]
            # print(f"this is what i want:::{tc_path}")
            # 步骤1：提取文件名（含扩展名）
            filename_with_ext = os.path.basename(tc_path)  # 输出：'列表查询.yaml'
            # 步骤2：分割文件名与扩展名
            filename, file_extension = os.path.splitext(filename_with_ext)  # filename='列表查询', file_extension='.yaml'
            # 最终结果
            target_part = filename  # 输出：'列表查询
            print(f"从入参获取用例名称: {target_part}")
            # 先删除上一次执行生成的结果文件
            if os.path.exists("apiResults.json"):
                os.remove("apiResults.json")
                print("删除成功")
            else:
                print('apiResults.json文件不存在')
            #然后复制模板生成一个新的结果文件apiResults.json
            with open("apiResults_template.json") as src, open("apiResults.json", 'w') as dest:
                # 一次性完成：读取 → 修改 → 写入
                data = json.load(src)          # 解析为字典
                data["businesses"][0]["name"] = target_part  # 精准修改目标字段
                json.dump(data, dest, indent=4)  # 保持格式写入新文件

            # 将参数格式化为 pytest 可识别的形式（如 --tc=path）
            pytest_args = [
                # f"-s",
                # f"--log-cli-level=INFO",
                f"testcases/testcaselist/{org_script}.py",
                f"--tc=testcases/apis/mplm/{tc_path}.yaml",          # 传递自定义参数
                "--alluredir=allure-report",
                "--clean-alluredir"
            ]
            # 移除已处理的参数，避免冲突
            sys.argv = [sys.argv[0]] + sys.argv[tc_index+1:]
        else:
            raise ValueError("--tc 参数后必须指定 YAML 文件路径")
        
    pytest.main(pytest_args)

if __name__ == "__main__":
    run_tests()
