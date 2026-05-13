# -*- coding: utf-8 -*-
# 导入必要的库
import time
import datetime
import requests
import urllib3
import json
import hashlib
from collections import OrderedDict
from http.client import HTTPConnection
from urllib.parse import urlparse
from common.logger import logger
# 开启调试模式
HTTPConnection.debuglevel = 1

# 忽略警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 定义 RequestSender 类
class RequestSender:

    # 初始化方法
    def __init__(self, session=None):
        """

        @rtype: object
        """
        # 如果没有传入 Session，则新建临时 Session
        if session is None:
            self.session = requests.session()
        else:
            self.session = session
        # 定义接口的状态码、请求时间和响应时间
        self.apiStatus = "success"
        self.reqAt = int(round(time.time() * 1000))
        self.resAt = int(round(time.time() * 1000))
        self.result_file = "apiResults.json"
        # self.result_file = r"E:\MPLMApiTest\apiResults.json"
    
     # 签名生成方法
    def generate_signature(self, username, body, content_type, path=""):
        sb = username

        # 解析并排序请求体
        if content_type == "application/json" or content_type == "application/json;charset=UTF-8":
            try:
                body_params = json.loads(body)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON 解析失败: {e}")
        elif content_type == "application/x-www-form-urlencoded":
            body_params = self.object_to_sign_body_object(body)
        else:
            body_params = {}

        sorted_params = self.deep_sort_obj(body_params)

        # 拼接排序后的参数
        if isinstance(sorted_params, dict):
            for key, value in sorted_params.items():
                sb += f"{key}{value}"

        # 拼接路径信息
        sb += path
        logger.info('签名字符串:{}'.format(sb))

        # 生成 MD5 签名
        md5 = hashlib.md5(sb.encode('utf-8')).hexdigest()
        logger.debug('生成的签名:{}'.format(md5))
        return md5

    # 支持 form-urlencoded 的参数解析方法
    def object_to_sign_body_object(self, body):
        if isinstance(body, str) and '&' in body:
            return dict(param.split('=') for param in body.split('&'))
        return body

    # 深度排序方法
    def deep_sort_obj(self, obj):
        if isinstance(obj, dict):
            return OrderedDict(sorted(
                (k, self.deep_sort_obj(v)) for k, v in obj.items()
            ))
        elif isinstance(obj, list):
            return [self.deep_sort_obj(item) for item in obj]
        return obj


    # 发送请求方法
    def send_requests(self, requestdata):
        '''
        签名参数usname:取值为testcase对应的yaml文件中username
        无username字段时,默认shenjh40
        特殊业务流，比如审核流程,可以根据返回参数回写yaml文件中username,再调用requests.py
        '''
        username = requestdata.get("username", "shenjh40")
        logger.debug('签名参数：usname:{}'.format(username))
        content_type = requestdata.get("headers", {}).get("Content-Type", "application/x-www-form-urlencoded")
        logger.debug('签名参数：content_type:{}'.format(content_type))
        path = urlparse(requestdata.get("url", "")).path
        logger.debug('签名参数：path:{}'.format(path))
        body = requestdata.get("data", "")
        logger.debug('签名参数：body:{}'.format(body))

        # 生成签名
        signature = self.generate_signature(username, body, content_type, path)

        # 将签名添加到请求头
        requestdata["headers"]["AccessID"] = signature

        # 判断请求类型
        if requestdata["dataType"] == "json":
            # 请求类型为 JSON 格式的请求
            # 调用 request 的方法去发起一个请求。并得到响应结果
            response = self.session.request(requestdata["method"], requestdata["url"], headers=requestdata["headers"], params=requestdata["params"], json=requestdata["data"], allow_redirects=True, verify=False)
        # 文件上传请求
        elif requestdata["dataType"] == "file":
            # 使用上下文管理器处理文件上传
            with open(requestdata["filePath"], 'rb') as file:
                files = {'file': file}
                response = self.session.request(requestdata["method"], requestdata["url"], headers=requestdata["headers"], params=requestdata["params"], data=requestdata["data"], files=files, allow_redirects=True, verify=False)
        else:
            # 请求类型为非 JSON 格式的请求，例如 form、text、xml 等
            # 调用 request 的方法去发起一个请求。并得到响应结果
            response = self.session.request(requestdata["method"], requestdata["url"], headers=requestdata["headers"], params=requestdata["params"], data=requestdata["data"], allow_redirects=True, verify=False)

        # 读取结果文件
        resultJson = open(self.result_file, "r", encoding="utf-8")
        resultContent = json.load(resultJson)
        resultJson.close()

        # 判断响应状态码
        if response.status_code != 200:
            # self.apiStatus = "error"
            # # 当响应码不是 200 时，设置 resultContent 里相关 error 数 +1
            # resultContent["businesses"][0]["error"] += 1
            # resultContent["businesses"][0]["failed"] += 1
            # resultContent["versionRecordVo"]["errors"] += 1
            # resultContent["versionRecordVo"]["failures"] += 1
            # logger.info("当前接口相应状态不为 200，接口服务有问题")
            print(response.status_code)
        else:
            # 当响应码是 200 时，设置 resultContent 里相关 success 数 +1
            resultContent["versionRecordVo"]["successes"] += 1
            resultContent["businesses"][0]["success"] += 1

        # 将每次的请求记录详情追加到 resultContent 里 caseRecords 数组里
        resultContent["businesses"][0]["caseRecords"].append(
            {
                "metaElapsed": self.resAt - self.reqAt,
                "metaMethod": response.request.method,
                "metaRequestAt": self.reqAt,
                "metaRequestHeaders": format(requestdata["headers"]),
                "metaRequestBody": format(requestdata["data"]),
                "metaResponseAt": self.resAt,
                "metaResponseBody": response.text,
                "metaResponseHeaders": format(response.headers),
                "metaStatusCode": response.status_code,
                "metaUrl": requestdata["url"],
                # "metaValidation": "[{\"error\":\"false\",\"failure\":\"false\",\"failureMessage\":\"断言失败信息，例如 xx 数据期望值 100，实际返回 12\",\"name\":\"响应码校验\"}]",
                "name": requestdata["apiName"],
                "status": self.apiStatus,
                # 以后改这里 caseid
                "devopsUseCaseId": requestdata["devopsUseCaseId"]
            })

        existing_devopsUseCaseId = resultContent["businesses"][0].get("devopsUseCaseId", "")
        new_devopsUseCaseId = requestdata["devopsUseCaseId"]
        if existing_devopsUseCaseId:
            updated_devopsUseCaseId = f"{existing_devopsUseCaseId},{new_devopsUseCaseId}"
        else:
            updated_devopsUseCaseId = new_devopsUseCaseId
        resultContent["businesses"][0]["devopsUseCaseId"] = updated_devopsUseCaseId

        # 请求响应完成后，设置 resultContent 里 total 数 +1
        resultContent["businesses"][0]["total"] += 1
        resultContent["businesses"][0]["startAt"] = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        resultContent["versionRecordVo"]["caseTotal"] += 1

        # 将更新好的 resultContent 保存到结果文件 apiResults.json
        resultJson2 = open(self.result_file, "w", encoding="utf-8")
        json.dump(resultContent, resultJson2, indent=2, ensure_ascii=False)
        resultJson2.close()

        # print("更新用户信息响应状态码:", response.status_code)
        # print("更新用户信息响应内容:", response.text)

        return response
