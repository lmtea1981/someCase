# -*- coding: utf-8 -*-

import json
import re
from common.logger import logger


def replace_placeholders(data, context):
    """递归替换数据中的占位符 {var}，缺失变量时保持原样"""
    # 打印 context 键，方便排查
    # logger.debug(f"ready to replace data: {data}")
    # logger.debug(f"context keys: {context.keys()!r}")
    import pprint
    logger.debug("full context:\n" + pprint.pformat(context))


    from string import Formatter

    if isinstance(data, dict):
        return {k: replace_placeholders(v, context) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_placeholders(item, context) for item in data]
    elif isinstance(data, str): # and "," not in data:
        if '"{' in data and '\\' not in data:
            if '(.+?)' not in data:
                try:
                    data = json.loads(data)
                    if isinstance(data, list):
                        return [replace_placeholders(item, context) for item in data]
                    else:
                        return {k: replace_placeholders(v, context) for k, v in data.items()}
                except Exception as e:
                    logger.error(f"字符串转字典失败！详细：{e}\n%%%===>{data}")

        # 查看进入字符串处理分支时的上下文
        # logger.debug(f"[str-branch] ready to replace in: {data}, context={list(context.keys())}")
        # 使用 string.Formatter 安全处理
        formatter = Formatter()
        parts = []

        try:
            # 解析字符串并处理每个部分
            for literal_text, field_name, format_spec, conversion in formatter.parse(data):
                # 添加字面文本
                if literal_text is not None:
                    parts.append(literal_text)

                # 处理占位符
                if field_name is not None:
                    # 检查变量是否存在
                    if field_name in context:
                        # 获取变量值
                        value = context[field_name]

                        # 处理转换和格式规范
                        if conversion is not None:
                            value = formatter.convert_field(value, conversion)
                        if format_spec:
                            value = formatter.format_field(value, format_spec)

                        # 在最终拼接前，再次确认有没有命中期望的字段
                        # logger.debug(f"[str-branch] fields found in this string: {list(formatter.parse(data))}")
                        parts.append(str(value))
                    else:
                        # 变量不存在，保留原始占位符
                        original_field = "{" + field_name
                        if conversion:
                            original_field += "!" + conversion
                        if format_spec:
                            original_field += ":" + format_spec
                        original_field += "}"
                        parts.append(original_field)
                

            # 组合所有部分
            logger.debug(f"***替换后内容：{''.join(parts)}")
            return ''.join(parts)

        except (KeyError, ValueError):
            # 格式错误时保持原样
            logger.error(f"{data}替换失败！")
            return data
    else:
        logger.debug(f"***替换后内容：{data}")
        return data
