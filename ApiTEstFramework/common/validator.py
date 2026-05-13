# -*- coding: utf-8 -*-

from common.logger import logger

def validate_response(response, validate_config):
    """
    验证响应内容
    :param response: 响应对象
    :param validate_config: 验证配置
    :return: 验证是否通过
    """
    all_passed = True

    try:
        response_json = response.json()
    except:
        response_json = {}

    for validation in validate_config:
        for check, expected_value in validation.items():
            if check == "status_code":
                assert response.status_code == expected_value
                if response.status_code != expected_value:
                    logger.error(f"Status code validation failed: expected {expected_value}, got {response.status_code}")
                    all_passed = False
            elif check == "contains":
                assert expected_value not in response.text
                if expected_value not in response.text:
                    logger.error(f"Content validation failed: expected '{expected_value}' to be in response")
                    all_passed = False
            elif check == "json_key_exists":
                keys = expected_value.split(".")
                temp = response_json
                key_exists = True
                for key in keys:
                    if key not in temp:
                        key_exists = False
                        break
                    temp = temp[key]
                if not key_exists:
                    logger.error(f"JSON key validation failed: expected key '{expected_value}' not found")
                    all_passed = False
            elif check == "json_key_value":
                key, value = expected_value.split("=", 1)
                logger.info(f"正在处理json_key_value，key：{key}，expect value：{value}")
                # logger.info(f"实际得到的key值：{response_json.get(key)}")
                keys = key.split(".")
                temp = response_json
                for k in keys:
                    if k in temp:
                        temp = temp[k]
                    else:
                        temp = None
                        break
                if str(temp) != value:
                    logger.error(f"JSON value validation failed: expected '{key}={value}', got '{key}={temp}'")
                    all_passed = False

    return all_passed
