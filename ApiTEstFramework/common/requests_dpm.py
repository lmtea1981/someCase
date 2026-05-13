# -*- coding: utf-8 -*-

# 导入必要的库
import time
import datetime
from urllib.parse import unquote
import pprint
import requests
import urllib3
import json

from common.logger import logger

from http.client import HTTPConnection
# 开启调试模式
HTTPConnection.debuglevel = 1

# 忽略警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 定义 RequestSender 类
class RequestSender:

    # 初始化方法
    def __init__(self, session=None):
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
        # self.result_file = r"E:\apiTestProj_1\apiResults.json"

    # 发送请求方法
    def send_requests(self, requestdata):
        # 判断请求类型
        if requestdata["dataType"] == "json":
            # 请求类型为 JSON 格式的请求
            # 调用 request 的方法去发起一个请求。并得到响应结果
            self.reqAt = int(round(time.time() * 1000))
            response = self.session.request(requestdata["method"], requestdata["url"], headers=requestdata["headers"], params=requestdata["params"], json=requestdata["data"], allow_redirects=True, verify=False)
        # 文件上传请求
        elif requestdata["dataType"] == "file":
            # files = {'file': open(requestdata["filePath"], 'rb')}  # old
            files = {'uploadFile': open(requestdata["filePath"], 'rb')}  # 解决上传文件参数问题
            self.reqAt = int(round(time.time() * 1000))
            response = self.session.request(requestdata["method"], requestdata["url"], headers=requestdata["headers"], params=requestdata["params"], data=requestdata["data"], files=files, allow_redirects=True, verify=False)
        else:
            # 请求类型为非 JSON 格式的请求，例如 form、text、xml 等
            # 调用 request 的方法去发起一个请求。并得到响应结果
            self.reqAt = int(round(time.time() * 1000))
            # 增加复杂form json格式处理
            if isinstance(requestdata['data'], dict):
                # 将所有值转为字符串
                # requestdata['data'] = {key: str(value) for key, value in requestdata['data'].items()}
                for k, v in requestdata['data'].items():
                    requestdata['data'][k] = (((str(v).replace(" ", "")
                                              .replace("'", '"'))
                                              .replace('False', 'false'))
                                              .replace('True', 'true')
                                              .replace('\\\\', '\\'))
            logger.debug(f"----------请求传入的data:{requestdata['data']}")
            response = self.session.request(requestdata["method"], requestdata["url"], headers=requestdata["headers"], params=requestdata["params"], data=requestdata["data"], allow_redirects=True, verify=False)
            # 拿到 PreparedRequest
            preq = response.request

            # 获取 body，bytes 解码成 str
            body = preq.body
            if isinstance(body, bytes):
                try:
                    body = body.decode("utf-8")
                except UnicodeDecodeError:
                    pass
            logger.debug(">>> Request Body:\n%s", pprint.pformat(body))
        self.resAt = int(round(time.time() * 1000))

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
