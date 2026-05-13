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
        # 处理提取过程变量传递
        if '{' in extractor:
            extractor = {k: v.format(**extractor) for k, v in result.items()}
        logger.info(f"======> 正在提取：{var_name} - {extractor}")
        if isinstance(extractor, str):
            if extractor.startswith("jsonpath:"):
                # 使用JSONPath提取
                json_path = extractor.replace("jsonpath:", "")

                jsonpath_expr = parse(json_path)
                matches = [match.value for match in jsonpath_expr.find(response_json)]
                if matches:
                    # # 处理list响应，注意：只取第1个元素！！！！
                    # if isinstance(matches, list) and len(matches) > 0:
                    #     for ii in range(len(matches)):
                    #         matches.append(json.loads(matches[ii]))
                    # 处理每个匹配项的多层引号
                    logger.debug(f"json匹配到:{matches}")
                    processed_matches = [
                        # keep_inner_quotes(match) if isinstance(match, str) else match
                        # for match in matches
                        keep_inner_quotes(match) if isinstance(match, str) else
                        [keep_inner_quotes(item) if isinstance(item, str) else
                         item for item in match] if isinstance(match, list) else
                        match
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
                match = re.search(pattern, response.text)  #
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
                    logger.debug(f"{ree}")
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
                # 将变量整合成一个dict，用于组合system_parameter
                elif pattern.startswith("v_combine:"):
                    pattern = pattern.replace("v_combine:", "")
                    keys = pattern.split("&")
                    var_dict = {}
                    try:
                        for key in keys:
                            if key in result:
                                var_dict[key] = (result[key])
                        result[var_name] = var_dict
                    except Exception as e:
                        logger.error("合并时发生错误:{}".format(e))
            else:
                # 直接从JSON响应中提取字段
                if extractor in response_json:
                    result[var_name] = response_json[extractor]
        if var_name not in result:
            result[var_name] = ''
        # logger.info(f"所所有变量：{result}")
    return result

def keep_inner_quotes(text):
    """
    保留字符串最内层引号（如果有多层引号）
    例如：'"洗碗机"' -> "洗碗机"
    """
    try:
        text = json.loads(text)
    except:
        if isinstance(text, str):
            # 正则匹配最内层的单/双引号对
            match = re.search(r"""(['"])(.*?)\1""", text)
            if match:
                return f"{match.group(1)}{match.group(2)}{match.group(1)}"
    return text  # 非字符串或无引号时原样返回
