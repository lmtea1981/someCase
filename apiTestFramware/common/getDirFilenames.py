# -*- coding: utf-8 -*-
import os


class FileHandler:

    def list_files_with_pattern(self, directory, prefix=None, suffix=None):
        """
        列出指定目录中符合特定前缀和后缀的文件

        参数:
            directory: 要搜索的目录路径
            prefix: 文件名开头(可选)
            suffix: 文件名结尾(可选)

        返回:
            符合条件的所有文件的完整路径列表
        """
        if not os.path.isdir(directory):
            raise ValueError(f"目录不存在: {directory}")

        matched_files = []

        for filename in os.listdir(directory):
            # 检查是否是文件(排除目录)
            filepath = os.path.join(directory, filename)
            if not os.path.isfile(filepath):
                continue

            # 检查前缀和后缀条件
            match = True

            if prefix and not filename.startswith(prefix):
                match = False

            if suffix and not filename.endswith(suffix):
                match = False

            if match:
                matched_files.append(filepath)

        return matched_files

if __name__ == "__main__":
    # 示例用法
    search_dir = input("请输入要搜索的目录路径: ").strip()
    file_prefix = input("请输入文件名前缀(可选，直接回车跳过): ").strip() or None
    file_suffix = input("请输入文件名后缀(可选，直接回车跳过): ").strip() or None

    try:
        a = FileHandler()
        result = a.list_files_with_pattern(search_dir, file_prefix, file_suffix)

        if not result:
            print("没有找到符合条件的文件")
        else:
            print(f"找到 {len(result)} 个符合条件的文件:")
            for filepath in result:
                print(filepath)
    except Exception as e:
        print(f"发生错误: {e}")
