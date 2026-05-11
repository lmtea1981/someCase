# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
from typing import Dict, List, Tuple

# 线程组类型
THREAD_GROUP_TYPES = {
    "ThreadGroup": "标准线程组",
    "SetupThreadGroup": "前置线程组",
    "PostThreadGroup": "后置线程组"
}

# 完全匹配你的JMX真实结构
THREAD_GROUP_PARAMS = [
    {"name": "线程数", "prop": "ThreadGroup.num_threads", "type": "string"},
    {"name": "启动时间(秒)", "prop": "ThreadGroup.ramp_time", "type": "string"},
    {"name": "循环次数", "prop": "LoopController.loops", "type": "string"},
    {"name": "启用调度器", "prop": "ThreadGroup.scheduler", "type": "bool"},
    {"name": "持续时间(秒)", "prop": "ThreadGroup.duration", "type": "string"},
    {"name": "启动延迟(秒)", "prop": "ThreadGroup.delay", "type": "string"},
]

def parse_jmx_file(file_path: str) -> Tuple[ET.ElementTree, ET.Element]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")
    if not file_path.endswith(".jmx"):
        raise ValueError("仅支持 .jmx 后缀的JMeter脚本")
    tree = ET.parse(file_path)
    root = tree.getroot()
    return tree, root

def find_all_thread_groups(root: ET.Element) -> List[Dict]:
    thread_groups = []
    for group_tag in THREAD_GROUP_TYPES.keys():
        groups = root.findall(f".//{group_tag}")
        for idx, group in enumerate(groups):
            name_elem = group.get("testname", "未命名")
            enabled = group.get("enabled", "true")
            group_info = {
                "type": group_tag,
                "type_name": THREAD_GROUP_TYPES[group_tag],
                "index": idx + 1,
                "element": group,
                "name": name_elem,
                "enabled": enabled
            }
            thread_groups.append(group_info)
    return thread_groups

# ====================== 修复核心：正确获取循环次数 ======================
def get_thread_group_params(group_element: ET.Element) -> Dict[str, str]:
    params = {}
    for param in THREAD_GROUP_PARAMS:
        prop_name = param["prop"]
        prop_type = param["type"]

        # 正确定位 LoopController.loops
        if prop_name == "LoopController.loops":
            controller = group_element.find(".//elementProp[@name='ThreadGroup.main_controller']")
            if controller is not None:
                elem = controller.find(f".//stringProp[@name='{prop_name}']")
            else:
                elem = None
        # 普通节点
        elif prop_type == "string":
            elem = group_element.find(f".//stringProp[@name='{prop_name}']")
        elif prop_type == "bool":
            elem = group_element.find(f".//boolProp[@name='{prop_name}']")

        params[prop_name] = elem.text.strip() if (elem is not None and elem.text) else ""
    return params

# ====================== 修复核心：正确修改循环次数 ======================
def modify_param_value(group_elem: ET.Element, prop_name: str, new_val: str, prop_type: str):
    try:
        # 重点修复：LoopController.loops 必须进入子层级
        if prop_name == "LoopController.loops":
            controller = group_elem.find(".//elementProp[@name='ThreadGroup.main_controller']")
            if controller is None:
                return False
            elem = controller.find(f".//stringProp[@name='{prop_name}']")
        else:
            if prop_type == "string":
                elem = group_elem.find(f".//stringProp[@name='{prop_name}']")
            elif prop_type == "bool":
                elem = group_elem.find(f".//boolProp[@name='{prop_name}']")
            else:
                return False

        if elem is not None:
            elem.text = new_val
            return True
    except:
        return False
    return False

def show_all_thread_groups(thread_groups: List[Dict]):
    print("\n" + "=" * 70)
    print("📊 JMeter脚本线程组参数一览")
    print("=" * 70)
    for i, group in enumerate(thread_groups):
        print(f"\n🔹 编号【{i + 1}】{group['type_name']} ｜ 名称：{group['name']} ｜ 启用：{group['enabled']}")
        print("-" * 65)
        params = get_thread_group_params(group["element"])
        for param in THREAD_GROUP_PARAMS:
            val = params[param["prop"]]
            val_display = val if val != "" else "(空)"
            print(f"  {param['name']:12s} => {val_display:6s}")
    print("\n" + "-" * 70)

# ====================== 修复自动设置永远循环 ======================
def auto_set_infinite_loop(group_elem: ET.Element):
    # 正确设置：循环次数=-1
    modify_param_value(group_elem, "LoopController.loops", "-1", "string")
    # 启用调度器
    modify_param_value(group_elem, "ThreadGroup.scheduler", "true", "bool")

def main():
    print("🚀 JMeter JMX 线程组参数修改工具（完全匹配你的JMeter 5.4.3）")
    print("✅ 修改持续时间 → 自动设置：循环次数=-1（永远循环）+ 启用调度器=true\n")

    while True:
        jmx_path = input("请粘贴JMX文件完整路径：").strip().strip('"').strip("'")
        try:
            tree, root = parse_jmx_file(jmx_path)
            print("✅ JMX文件解析成功！")
            break
        except Exception as e:
            print(f"❌ 错误：{e}，请重新输入\n")

    groups = find_all_thread_groups(root)
    if not groups:
        print("❌ 未找到任何线程组，脚本退出")
        return

    show_all_thread_groups(groups)

    while True:
        choice = input("\n是否修改参数？(y/n，直接回车=不修改)：").strip().lower()
        if choice not in ["y", "yes"]:
            break

        try:
            g_idx = int(input(f"请输入要修改的线程组编号(1-{len(groups)})：")) - 1
            if not 0 <= g_idx < len(groups):
                print("❌ 编号超出范围")
                continue
        except ValueError:
            print("❌ 请输入数字")
            continue

        selected = groups[g_idx]
        print(f"\n🎯 已选择：{selected['type_name']} - {selected['name']}")

        print("\n可修改参数：")
        for j, p in enumerate(THREAD_GROUP_PARAMS):
            print(f"  {j + 1}. {p['name']}")

        try:
            p_idx = int(input(f"请选择参数编号(1-{len(THREAD_GROUP_PARAMS)})：")) - 1
            if not 0 <= p_idx < len(THREAD_GROUP_PARAMS):
                print("❌ 编号超出范围")
                continue
        except ValueError:
            print("❌ 请输入数字")
            continue

        param = THREAD_GROUP_PARAMS[p_idx]
        current = get_thread_group_params(selected["element"])[param["prop"]]
        current = current if current != "" else "(空)"

        new_val = input(f"\n当前值：{current}\n请输入新值：").strip()

        if modify_param_value(selected["element"], param["prop"], new_val, param["type"]):
            print(f"✅ 修改成功：{param['name']} = {new_val}")

            # 自动设置永远循环 + 调度器
            if param["prop"] == "ThreadGroup.duration" and new_val.strip() != "":
                auto_set_infinite_loop(selected["element"])
                print("🔧 自动设置：循环次数=-1（永远循环），启用调度器=true")
        else:
            print("❌ 修改失败：未找到对应参数节点")

    save = input("\n是否保存修改后的脚本？(y/n)：").strip().lower()
    if save == "y":
        folder = os.path.dirname(jmx_path)
        filename = os.path.basename(jmx_path)
        new_file = os.path.join(folder, f"modified_{filename}")
        tree.write(new_file, encoding="utf-8", xml_declaration=True)
        print(f"\n🎉 文件已保存：{new_file}")
    else:
        print("\nℹ️ 未保存，已退出")

if __name__ == "__main__":
    main()
