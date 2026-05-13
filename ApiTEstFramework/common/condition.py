import time
from common.logger import logger

def check_condition(condition_config, variables):
    """
    检查条件是否满足
    :param condition_config: 条件配置
    :param variables: 变量字典
    :return: 满足条件时返回下一步，否则返回None
    """
    condition_type = condition_config.get("type")
    var_name = condition_config.get("variable")
    value = condition_config.get("value")
    next_step = condition_config.get("next_step")

    if var_name not in variables:
        logger.warning(f"Variable '{var_name}' not found in context")
        return None

    var_value = variables[var_name]

    if condition_type == "eq" and var_value == value:
        return next_step
    elif condition_type == "neq" and var_value != value:
        return next_step
    elif condition_type == "contains" and value in var_value:
        return next_step
    elif condition_type == "gt" and var_value > value:
        return next_step
    elif condition_type == "lt" and var_value < value:
        return next_step

    return None

def wait_until(request_func, request_config, wait_config):
    """
    循环等待直到条件满足
    :param request_func: 请求函数
    :param request_config: 请求配置
    :param wait_config: 等待配置
    :param variables: 变量字典
    :return: 满足条件时返回响应对象，否则返回最后一次响应
    """
    max_retries = wait_config.get("max_retries", 5)
    interval = wait_config.get("interval", 1)
    expect_key = wait_config.get("expect_key")
    expect_value = wait_config.get("expect_value")
    logger.info(f"Wait condition {expect_key}: {expect_value}")
    # logger.info(f"request config {request_config}")

    for i in range(max_retries):
        response = request_func(request_config)

        try:
            response_json = response.json()
            if expect_key in response_json and response_json[expect_key] == expect_value:
                logger.info(f"Wait condition met after {i+1} retries")
                return response
        except:
            pass

        logger.info(f"Waiting for condition ({expect_key}={expect_value}), retry {i+1}/{max_retries}")
        time.sleep(interval)

    logger.warning(f"Condition not met after {max_retries} retries")
    return response

def check_loop_condition(condition: str, response_data: dict, saved_vars: dict) -> bool:
    """检查循环终止条件"""
    if not condition:
        return False

    # 简单实现：支持 $.field == value 格式
    if '==' in condition:
        left, right = condition.split('==', 1)
        left = left.strip()
        right = right.strip().strip("'\"")

        # 从响应或保存变量中取值
        if left.startswith('$.'):
            value = _extract_json_value(response_data, left)
        elif left.startswith('saved.'):
            var_name = left[6:]
            value = saved_vars.get(var_name)
        else:
            value = left

        # 类型转换
        if right.lower() == 'true':
            right_value = True
        elif right.lower() == 'false':
            right_value = False
        elif right.isdigit():
            right_value = int(right)
        else:
            right_value = right
        return value == right_value

    return False

def _extract_json_value(data: dict, json_path: str):
    """从JSON响应中提取数据"""
    # 简化实现，实际应使用jsonpath库
    if json_path.startswith('$.'):
        path = json_path[2:]
    else:
        path = json_path

    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, list) and key.isdigit():
            index = int(key)
            if index < len(value):
                value = value[index]
            else:
                return None
        elif isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    print(f"ex: {value}")
    return value
