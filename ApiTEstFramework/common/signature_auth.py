# -*- coding: utf-8 -*-
import hashlib
import json
from urllib.parse import parse_qs
from typing import Union, Dict, List, Any
from common.logger import logger
import os

def object2sign_body_object(body: str) -> Union[Dict, List, str]:
    """尝试解析 JSON，失败则返回原始字符串"""
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body

def deep_sort_obj(obj: Any) -> Any:
    """深度排序对象（字典按键排序，列表递归排序）"""
    if isinstance(obj, dict):
        return {k: deep_sort_obj(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        return sorted(deep_sort_obj(x) for x in obj)
    return obj

def generate_signature(
        username: str,
        content_type: str,
        request_body: str = "",
        file_path: str = "",
        api_path: str = ""
) -> str:
    """
    生成请求签名
    :param username: 用户名
    :param content_type: 请求Content-Type
    :param request_body: 请求体内容
    :param file_path: 文件路径（用于计算MD5）
    :param api_path: 接口路径
    :return: MD5签名
    """
    sb = username
    print(sb)
    logger.info(f"用户：{sb}，类型：{content_type},{request_body},{api_path}")

    # 处理请求体
    body_params = {}
    if "application/json" in content_type:
        body_params = object2sign_body_object(request_body)
        sb += request_body
    elif "x-www-form-urlencoded" in content_type:
        print(type(request_body), request_body)
        logger.info(f"请求体：{type(request_body)}")
        if isinstance(request_body, str):
            # 表单数据去掉等号拼接
            form_data = parse_qs(request_body)
            # sb += "".join(f"{k}{v[0]}" for k, v in form_data.items())
            body_params = form_data
        elif isinstance(request_body, dict):
            body_params = request_body
        print(type(body_params), body_params)
        print(f"1:{sb}")

    # 处理文件MD5
    file_md5 = ""
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            file_md5 = hashlib.md5(f.read(1024 * 1024)).hexdigest()  # 读取前1MB
    sb += file_md5

    # 排序并拼接参数
    if isinstance(body_params, dict):
        sorted_params = deep_sort_obj(body_params)
        for k, v in sorted_params.items():
            sb += str(k)
            if isinstance(v, list):
                sb += str(v[0])
            else:
                sb += str(v)
    print(f"2:{sb}")
    # 添加API路径
    url = api_path.split("com")
    sb += url[1]
    print(f"3:{sb}")
    logger.info(f"11111签名：{sb}")
    # 计算MD5签名
    sign_str = "".join(sb)
    # sign_str1 = "shenjh40buildClasscom.midea.ext.exp.panel.ExpProductToExplodedViewPanelBuilder/PDM-Server/PanelController/buildPanel"
    # sign_str1 = "shenjh40buildClasscom.midea.ext.exp.builder.ExpProductToExplodedViewTableBuilderisSearch0pageNumber1perPageSize500tableIdcom.midea.ext.exp.builder.ExpProductToExplodedViewTableBuildertotal0/PDM-Server/TableController/buildCount"
    # print(hashlib.md5(sign_str1.encode("utf-8")).hexdigest())
    logger.info(f"签名：{sign_str}")
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest()
