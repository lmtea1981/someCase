import json
from typing import Any, Dict
from urllib.parse import unquote, urlencode
from common.requests_mplm import RequestSender
from common.extractor import extract_values
from common.condition import check_condition, wait_until
from common.validator import validate_response
from common.replace_placeholders import replace_placeholders
from common.signature_auth import generate_signature
from common.logger import logger
import yaml
import os
import allure
import pytest


@allure.feature('测试-DPM-功能')
class TestMPLM:
    # 定义过程变量
    context = {}
    # 替换全局变量、过程变量

    @pytest.mark.parametrize("ud_var", [{"plantOid": 21}, {"containerName": "INV_M45_厨电洗碗机公司_制造库存组织"}])
    @allure.story('dpm-login')
    def test_dpm_login(self, ud_var, dpm_env_config, shared_session):
        base_vars = {
            "AUTH_URL": dpm_env_config.AUTH_URL,
            "BASE_URL": dpm_env_config.BASE_URL,
            "USERNAME": dpm_env_config.USERNAME,
            "PASSWORD": dpm_env_config.PASSWORD
            # 添加其他需要的变量...
        }
        self.context.update(ud_var)
        self.context.update(base_vars)
        # 读取YAML文件
        with open('./testcases/apis/dpm/dpm_login.yaml', 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        reqeustSender = RequestSender(shared_session)
        # 循环发送请求
        for request in data['requests']:
            # 添加全局请示头
            request['headers'].update(dpm_env_config.global_headers)
            with allure.step(request["apiName"]):
                # 处理循环等待
                if "wait_until" in request:
                    response = wait_until(reqeustSender.send_requests, replace_placeholders(request, self.context), request["wait_until"])
                else:
                    response = reqeustSender.send_requests(
                        replace_placeholders(request, self.context))
                # 响应结果处理
                try:
                    # 生成签名
                    if 'username' in replace_placeholders(request, self.context)['data']:
                        username = replace_placeholders(request, self.context)['data']['username']
                        logger.info(f"用户名：{username}")
                        if 'data' in replace_placeholders(request, self.context):
                            body = replace_placeholders(request, self.context)['data']
                            content_type = f"'{replace_placeholders(request, self.context)['headers']['content-Type']}'"
                            path = replace_placeholders(request, self.context)['url']
                            logger.debug(f"body: {body}, contype: {content_type}, url: {path}")
                            sign = generate_signature(username, body, content_type, path)
                            sign_dict = {"sign": sign}
                            self.context.update(sign_dict)
                            logger.info(f"生成签名{sign}")
                    if 'sign' in self.context:
                        # 将签名添加到请求头
                        request["headers"]["AccessID"] = self.context['sign']
                        logger.info(f"正在使用签名{self.context['sign']}")

                    # 提取变量
                    if "extract" in request:
                        extracted_vars = extract_values(response, request["extract"])
                        self.context.update(extracted_vars)
                        logger.info(f"新增变量: {extracted_vars}\n所有变量：{self.context}")

                    # 条件判断
                    if "condition" in request:
                        return check_condition(request["condition"], self.context)

                    # 测试平台日志记录
                    # response_json = response.json()  # 直接获取JSON字典
                    # logger.info(f"****** 响应：{response_json}")
                    print(request["apiName"]+"\n"+response.json())
                except Exception as e:
                    print(request["apiName"]+"\n"+response.text)
                    # logger.info(f"***--- 响应：{response.text}")

                # 验证响应
                if "validate" in request:
                    assert validate_response(response, request['validate'])
                else:
                    assert response.status_code == 200

  @allure.story('dpm-通用操作')
    def test_dpm_normal(self, request, dpm_env_config, shared_session):
        # 获取命令行传入的 --tc 参数值
        tc_path = request.config.getoption("--tc")
        # 验证文件是否存在
        if not os.path.exists(tc_path):
            raise FileNotFoundError(f"YAML 文件不存在：{tc_path}")
        # 读取YAML文件
        with open(tc_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        reqeustSender = RequestSender(shared_session)
        # 循环发送请求
        for request in data['requests']:
            logger.info(f"***执行：{request['apiName']}")
            # logger.info(f"***执行参数：{request['data']}")
            # 添加全局请示头
            request['headers'].update(dpm_env_config.global_headers)
            with allure.step(request["apiName"]):
                # 处理循环等待
                if "wait_until" in request:
                    response = wait_until(reqeustSender.send_requests,
                                          replace_placeholders(request, self.context),
                                          request["wait_until"])
                else:
                    response = reqeustSender.send_requests(
                        replace_placeholders(request, self.context))
                # 响应结果处理
                try:
                    # 使用签名
                    if self.context['sign']:
                        # 将签名添加到请求头
                        request["headers"]["AccessID"] = self.context['sign']
                        logger.info(f"正在使用签名{self.context['sign']}")
                    # 提取变量
                    if "extract" in request:
                        extracted_vars = extract_values(response, request["extract"])
                        self.context.update(extracted_vars)
                        logger.info(f"%%%+++新增变量: {extracted_vars}\n%%%所有变量：{self.context}")

                    # 条件判断
                    if "condition" in request:
                        return check_condition(request["condition"], self.context)

                    response_json = response.json()  # 直接获取JSON字典
                    logger.info(f"****** 响应：{response_json}")
                    print(request["apiName"]+"\n"+json.dumps(response_json))
                except Exception as e:
                    print(request["apiName"]+"\n"+response.text)
                    logger.info(f"***--- 响应：{response.text}")

                # 验证响应
                if "validate" in request:
                    assert validate_response(response, request['validate'])
                else:
                    assert response.status_code == 200
                    assert response.json()['status'] == 'ok'
