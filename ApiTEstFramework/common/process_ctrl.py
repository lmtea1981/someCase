# -*- coding: utf-8 -*-
import json
import time
from common.requests_mplm import RequestSender
from common.extractor import extract_values
from common.condition import check_condition, wait_until
from common.validator import validate_response
from common.replace_placeholders import replace_placeholders
from common.signature_auth import generate_signature
from common.logger import logger
import yaml
import pytest
import allure
from typing import Dict, List, Any


class ProcessCtrl:
    def __init__(self):
        pass
    
    def _signature_auth(self, request, ctx):
        logger.info(f"----------{replace_placeholders(request, ctx)}")
        try:
            # 生成签名
            if 'username' in replace_placeholders(request, ctx)['data']:
                username = replace_placeholders(request, ctx)['data']['username']
                logger.info(f"用户名：{username}")
                if 'data' in replace_placeholders(request, ctx):
                    body = replace_placeholders(request, ctx)['data']
                    content_type = f"'{replace_placeholders(request, ctx)['headers']['content-Type']}'"
                    path = replace_placeholders(request, ctx)['url']
                    logger.debug(f"body: {body}, contype: {content_type}, url: {path}")
                    sign = generate_signature(username, content_type, body, "", path)
                    sign_dict = {"sign": sign}
                    ctx.update(sign_dict)
                    logger.info(f"生成签名{sign}")
            if ctx['sign']:
                # 将签名添加到请求头
                request["headers"]["AccessID"] = ctx['sign']
                logger.info(f"正在使用签名{ctx['sign']}")
        except Exception as e:
            logger.info(f"---没有Data~")

        return ctx

    def _req_normal(self, reqeustSender, request, ctx):
        logger.info(f"***执行：{replace_placeholders(request['apiName'], ctx)}")
        logger.info(f"***执行参数：{replace_placeholders(request['data'], ctx)}")

        with allure.step(request["apiName"]):
            response = reqeustSender.send_requests(replace_placeholders(request, ctx))
            # 响应结果处理
            try:
                # 提取变量
                if "extract" in request:
                    extracted_vars = extract_values(response, replace_placeholders(request["extract"], ctx))
                    ctx.update(extracted_vars)
                    # logger.info(f"%%%+++新增变量: {extracted_vars}\n%%%所有变量：{ctx}")
                    logger.info(f"%%%+++新增变量: {extracted_vars}")

                # 条件判断
                if "condition" in request:
                    return check_condition(request["condition"], ctx)

                response_json = response.json()  # 直接获取JSON字典
                logger.info(f"****** 响应：{response_json}")
            except Exception as e:
                logger.info(f"***--- 响应：{response.text}")

            # 验证响应
            if "validate" in request:
                assert validate_response(response, request['validate'])
            else:
                assert response.status_code == 200
        return ctx

    def _req_normal_withValidate(self, reqeustSender, request, ctx):
        logger.info(f"***执行：{replace_placeholders(request['apiName'], ctx)}")
        logger.info(f"***执行参数：{replace_placeholders(request['data'], ctx)}")

        with allure.step(request["apiName"]):
            response = reqeustSender.send_requests(replace_placeholders(request, ctx))
            # 响应结果处理
            try:
                # 提取变量
                if "extract" in request:
                    extracted_vars = extract_values(response, replace_placeholders(request["extract"], ctx))
                    ctx.update(extracted_vars)
                    # logger.info(f"%%%+++新增变量: {extracted_vars}\n%%%所有变量：{ctx}")
                    logger.info(f"%%%+++新增变量: {extracted_vars}")

                # 条件判断
                if "condition" in request:
                    return check_condition(request["condition"], ctx)

                response_json = response.json()  # 直接获取JSON字典
                logger.info(f"****** 响应：{response_json}")
            except Exception as e:
                logger.info(f"***--- 响应：{response.text}")

            # 验证响应
            if "validate" in request:
                assert validate_response(response, request['validate'])
            else:
                assert response.status_code == 200
                assert response.json().get("status") == "ok"  # mplm
        return ctx

def _req_timeWait(self, reqeustSender, request, ctx):
        logger.info(f"***执行：{replace_placeholders(request['apiName'], ctx)}")
        logger.info(f"***执行参数：{replace_placeholders(request['data'], ctx)}")
        with allure.step(request["apiName"]):
            # 处理循环等待
            if "wait_until" in request:
                response = wait_until(reqeustSender.send_requests, replace_placeholders(request, ctx), request["wait_until"])
            else:
                response = reqeustSender.send_requests(replace_placeholders(request, ctx))
            try:
                # 提取变量
                if "extract" in request:
                    extracted_vars = extract_values(response, replace_placeholders(request["extract"], ctx))
                    ctx.update(extracted_vars)
                    # logger.info(f"%%%+++新增变量: {extracted_vars}\n%%%所有变量：{ctx}")
                    logger.info(f"%%%+++新增变量: {extracted_vars}")

                # 条件判断
                if "condition" in request:
                    return check_condition(request["condition"], ctx)

                response_json = response.json()  # 直接获取JSON字典
                logger.info(f"****** 响应：{response_json}")
            except Exception as e:
                logger.info(f"***--- 响应：{response.text}")

            # 验证响应
            if "validate" in request:
                assert validate_response(response, request['validate'])
            else:
                assert response.status_code == 200
                # assert response.json().get("status") == "ok"  # mplm

        return ctx

    def _workflow_normal(self, reqeustSender, data, ctx):
        # 开始走流程，判断流程是否完成状态
        if "complete" in ctx and ctx['complete'] == "false":
            # 第一层：循环10+1次，多循环一次确保状态变为“已批准”
            flow_loop_time = 10
            while ctx['complete'] == "false" and flow_loop_time != 0:
                # 处理审批流程循环
                steps = data['requests_WF1']
                # 刷新taskId，16次间隔10秒
                if ctx['taskId'] == "":
                    for i in range(10):
                        logger.info(f"正在重试第{i+1}次，共10次...")
                        time.sleep(10)
                        step = steps[0]  # 执行流程状态刷新 '3.13: 设计变更流程审批-提交流程-刷流程状态'
                        step_name = step.get('apiName', f'step_{i}')
                        if 'procName' in ctx:
                            # 处理存在多个procName的列表
                            if isinstance(ctx['procName'], str) and "[" in ctx['procName']:
                                list_data = eval(ctx['procName'])
                                ctx['procName'] = list_data[0]
                            elif isinstance(ctx['procName'], list):
                                ctx['procName'] = ctx['procName'][0]
                            else:
                                logger.info(f"---{type(ctx['procName'])}: {ctx['procName']}")
                            logger.info(f"***执行：{replace_placeholders(step_name, ctx)}--procName: {ctx['procName']}")
                        else:
                            logger.info(f"***执行：{replace_placeholders(step_name, ctx)}")

                        # 添加全局请示头
                        step['headers'].update(env_config.global_headers)
                        # 使用签名
                        if ctx['sign']:
                            # 将签名添加到请求头
                            step["headers"]["AccessID"] = ctx['sign']
                            logger.info(f"正在使用签名{ctx['sign']}")
                        # 输出执行参数
                        logger.info(f"***执行参数：{replace_placeholders(step, ctx)['data']}")
                        with allure.step(step["apiName"]):
                            # 处理循环等待
                            if "wait_until" in step:
                                response = wait_until(reqeustSender.send_requests,
                                                      replace_placeholders(step, ctx),
                                                      step["wait_until"])
                            else:
                                response = reqeustSender.send_requests(
                                    replace_placeholders(step, ctx))
                            # 响应结果处理
                            try:
                                # 提取变量
                                if "extract" in step:
                                    extracted_vars = extract_values(response, replace_placeholders(step["extract"], ctx))
                                    ctx.update(extracted_vars)
                                    # logger.info(f"%%%+++新增变量: {extracted_vars}\n%%%所有变量：{ctx}")

                                response_json = response.json()  # 直接获取JSON字典
                                logger.info(f"****** 响应：{response_json}")
                            except Exception as e:
                                logger.info(f"***--- 响应：{response.text}")

                            # 验证响应
                            if "validate" in step:
                                assert validate_response(response, step['validate'])
                            else:
                                assert response.status_code == 200
                        if ctx['taskId']:
                            break
                        if ctx['complete'] == "true":
                            break

                # 处理存在多个taskId的列表
                if isinstance(ctx['taskId'], str) and "[" in ctx['taskId']:
                    list_data = eval(ctx['taskId'])
                    ctx['taskId'] = list_data[0]
                elif isinstance(ctx['taskId'], list):
                    ctx['taskId'] = ctx['taskId'][0]
                else:
                    logger.info(f"---{type(ctx['taskId'])}: {ctx['taskId']}")

                # 更换签名
                if 'userId' in ctx and ctx['userId'] != "":
                    if ctx['userId']:
                        # 处理存在多个taskId的列表
                        if ctx['userId'].startswith("["):
                            list_data = eval(ctx['userId'])
                            ctx['userId'] = list_data[0]
                    if ctx['userId'] != ctx['userName']:
                        logger.info(f"》》》审批用户更换为：{ctx['userId']}")
                        if 'data' in replace_placeholders(steps[1], ctx):
                            body = replace_placeholders(steps[1], ctx)['data']
                            content_type = f"'{replace_placeholders(steps[1], ctx)['headers']['content-type']}'"
                            path = replace_placeholders(steps[1], ctx)['url']
                            logger.debug(f"body: {body}, contype: {content_type}, url: {path}")
                            sign = generate_signature(ctx['userName'], content_type, body, "", path)
                            sign_dict = {"sign": sign}
                            ctx.update(sign_dict)
                            logger.info(f"生成签名{sign}")
                    # 更换用户
                    steps = data['requests_WF1']
                    step = steps[1]
                    step_name = step.get('apiName')
                    logger.info(f"***执行：{replace_placeholders(step_name, ctx)}")

                    # 添加全局请示头
                    step['headers'].update(env_config.global_headers)
                    # 使用签名
                    if ctx['sign']:
                        # 将签名添加到请求头
                        step["headers"]["AccessID"] = ctx['sign']
                        logger.info(f"正在使用签名{ctx['sign']}")
                    # 输出执行参数
                    logger.info(f"***执行参数：{replace_placeholders(step, ctx)['data']}")
                    with allure.step(step["apiName"]):
                        # 处理循环等待
                        if "wait_until" in step:
                            response = wait_until(reqeustSender.send_requests,
                                                  replace_placeholders(step, ctx),
                                                  step["wait_until"])
                        else:
                            response = reqeustSender.send_requests(
                                replace_placeholders(step, ctx))
                        # 响应结果处理
                        try:
                            # 提取变量
                            if "extract" in step:
                                extracted_vars = extract_values(response, replace_placeholders(step["extract"], ctx))
                                ctx.update(extracted_vars)
                                # logger.info(f"%%%+++新增变量: {extracted_vars}\n%%%所有变量：{ctx}")

                            response_json = response.json()  # 直接获取JSON字典
                            logger.info(f"****** 响应：{response_json}")
                        except Exception as e:
                            logger.info(f"***--- 响应：{response.text}")

                        # 验证响应
                        if "validate" in step:
                            assert validate_response(response, step['validate'])
                        else:
                            assert response.status_code == 200

                  # 跳过刷新步骤'3.13: 设计变更流程审批-提交流程-刷流程状态'、'3.14: 设计变更流程审批-提交流程-切换账号'
                i = 2
                # 循环提交审批动作
                while i < len(steps):
                    step = steps[i]
                    step_name = step.get('apiName', f'step_{i}')
                    # logger.info(f"***执行：{replace_placeholders(step_name, ctx)}")
                    if 'procName' in ctx:
                        # 处理存在多个procName的列表
                        if isinstance(ctx['procName'], str) and "[" in ctx['procName']:
                            list_data = eval(ctx['procName'])
                            ctx['procName'] = list_data[0]
                        elif isinstance(ctx['procName'], list):
                            ctx['procName'] = ctx['procName'][0]
                        else:
                            logger.info(f"---{type(ctx['procName'])}: {ctx['procName']}")
                        logger.info(f"***执行：{replace_placeholders(step_name, ctx)}--procName: {ctx['procName']}")
                    else:
                        logger.info(f"***执行：{replace_placeholders(step_name, ctx)}")

                    # 添加全局请示头
                    step['headers'].update(env_config.global_headers)

                    # 更新签名
                    if 'userId' in ctx and ctx['userId'] != "":
                        if 'data' in replace_placeholders(step, ctx):
                            body = replace_placeholders(step, ctx)['data']
                            content_type = f"'{replace_placeholders(step, ctx)['headers']['content-type']}'"
                            path = replace_placeholders(step, ctx)['url']
                            logger.debug(f"body: {body}, contype: {content_type}, url: {path}")
                            sign = generate_signature(ctx['userId'], content_type, body, "", path)
                            sign_dict = {"sign": sign}
                            ctx.update(sign_dict)
                            logger.info(f"生成签名{sign}")

                        # 将签名添加到请求头
                        step["headers"]["AccessID"] = ctx['sign']
                        logger.info(f"正在使用签名{ctx['sign']}")
                    # 输出执行参数
                    logger.info(f"***执行参数：{replace_placeholders(step, ctx)['data']}")

                    with allure.step(step["apiName"]):
                        # 处理循环等待
                        if "wait_until" in step:
                            response = wait_until(reqeustSender.send_requests,
                                                  replace_placeholders(step, ctx),
                                                  step["wait_until"])
                        else:
                            response = reqeustSender.send_requests(
                                replace_placeholders(step, ctx))
                        # 响应结果处理
                        try:
                            # 提取变量
                            if "extract" in step:
                                extracted_vars = extract_values(response, replace_placeholders(step["extract"], ctx))
                                ctx.update(extracted_vars)
                                # logger.info(f"%%%+++新增变量: {extracted_vars}\n%%%所有变量：{ctx}")

                            response_json = response.json()  # 直接获取JSON字典
                            logger.info(f"****** 响应：{response_json}")
                        except Exception as e:
                            logger.info(f"***--- 响应：{response.text}")

                        # 验证响应
                        if "validate" in step:
                            assert validate_response(response, step['validate'])
                        else:
                            assert response.status_code == 200

                        logger.info(f"********流程完成状态：{ctx['complete']}")
                        if ctx['complete'] == "true":
                            break

                    # 循环递增——循环提交审批动作
                    i += 1
                # 循环递增——第一层：循环10次
                flow_loop_time -= 1

