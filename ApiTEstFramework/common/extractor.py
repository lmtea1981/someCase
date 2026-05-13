# -*- coding: utf-8 -*-

import json
import re
from jsonpath_ng.ext import parse
from common.logger import logger


def extract_values(response, extract_config):
    """
    从响应中提取值
    :param response: 请求响应对象
    :param extract_config: 提取配置
    :return: 提取的变量字典
    """
    result = {}

    try:
        response_json = response.json()
    except:
        response_json = {}

    for var_name, extractor in extract_config.items():
        logger.info(f"======> 正在提取：{extractor}")
        if isinstance(extractor, str):
            if extractor.startswith("jsonpath:"):
                # 使用JSONPath提取
                json_path = extractor.replace("jsonpath:", "")

                jsonpath_expr = parse(json_path)
                matches = [match.value for match in jsonpath_expr.find(response_json)]
                if matches:
                    # 处理每个匹配项的多层引号
                    processed_matches = [
                        keep_inner_quotes(match) if isinstance(match, str) else match
                        for match in matches
                    ]
                    # 保持 null 并转换为 JSON 字符串
                    result_null = json.dumps(
                        processed_matches[0] if len(processed_matches) == 1 else processed_matches,
                        ensure_ascii=False
                    )
                    result[var_name] = result_null.strip('"')
            elif extractor.startswith("regex:"):
                # 使用正则表达式提取
                pattern = extractor.replace("regex:", "")
                logger.info(f"{pattern}")
                # logger.debug(f"response.text: {response.text}")
                match = re.search(pattern, response.text)
                logger.info(f"使用正则表达式提取 结果：{match}")
                if match:
                    result[var_name] = match.group(1) if match.groups() else match.group(0)
            elif extractor.startswith("fix:"):
                pattern = extractor.replace("fix:", "")
                result[var_name] = pattern
            # 处理beanshell脚本逻辑
            elif extractor.startswith("fun_"):
                pattern = extractor.replace("fun_", "")
                # 同一次请求参数转换
                if pattern.startswith("v_replace:"):
                    pattern = pattern.replace("v_replace:", "")
                    var = pattern.split(",")
                    key, old, new = var[0], var[1].strip('"'), var[2].strip('"')
                    ree = result[key].replace(f'{old}', f'{new}')
                    logger.debug(f"v_replace 的debug：{ree}")
                    result[var_name] = ree
                # 同一次请求参数dict增加元素
                elif pattern.startswith("v_update:"):
                    pattern = pattern.replace("v_update:", "")
                    var = pattern.split("&")
                    key, elem = var[0], var[1]
                    elem_json = json.loads(elem)
                    ree = json.loads(result[key]).copy()
                    ree.update(elem_json)
                    result_null = json.dumps(ree, ensure_ascii=False)  # 保持 null
                    result[var_name] = result_null
            else:
                # 直接从JSON响应中提取字段
                if extractor in response_json:
                    result[var_name] = response_json[extractor]
            logger.info(f"提取 {var_name}：{extractor} 成功 ==> {result[var_name]}")
        if var_name not in result:
            result[var_name] = ''
        logger.info(f"所所有变量：{result}")
    return result

def keep_inner_quotes(text):
    """
    保留字符串最内层引号（如果有多层引号）
    例如：'"洗碗机"' -> "洗碗机"
    """
    if isinstance(text, str):
        # 正则匹配最内层的单/双引号对
        match = re.search(r"""(['"])(.*?)\1""", text)
        if match:
            return f"{match.group(1)}{match.group(2)}{match.group(1)}"
    return text  # 非字符串或无引号时原样返回
