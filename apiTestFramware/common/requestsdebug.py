import time
import datetime
import requests
import urllib3
import json

# 忽略警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RequestSender:

    def __init__(self):
        self.session = requests.session()
        #定义接口的状态码、请求时间和响应时间
        self.apiStatus="success"
        self.reqAt=int(round(time.time()*1000))
        self.resAt=int(round(time.time()*1000))


    def send_requests(self, requestdata):
        if requestdata["dataType"] == "json":
            # 请求类型为json格式的请求
            # 调用request的方法去发起一个请求。并得到响应结果
            self.reqAt=int(round(time.time()*1000))
            response = self.session.request(requestdata["method"],requestdata["url"],headers=requestdata["headers"], params=requestdata["params"], json=requestdata["data"], allow_redirects=True, verify=False)
        # 文件上传请求
        elif requestdata["dataType"] == "file":
            files = {'file': open(requestdata["filePath"], 'rb')}
            self.reqAt=int(round(time.time()*1000))
            response = self.session.request(requestdata["method"],requestdata["url"],headers=requestdata["headers"], params=requestdata["params"], data=requestdata["data"], files=files, allow_redirects=True, verify=False)
        else:
            # 请求类型为非json格式的请求，例如form、text、xml等
            # 调用request的方法去发起一个请求。并得到响应结果
            self.reqAt=int(round(time.time()*1000))
            response = self.session.request(requestdata["method"],requestdata["url"],headers=requestdata["headers"], params=requestdata["params"], data=requestdata["data"], allow_redirects=True, verify=False)
            print()
        self.resAt=int(round(time.time()*1000))

        resultJson=open("apiResults.json","r",encoding="utf-8")
        resultContent=json.load(resultJson)
        resultJson.close()

        if response.status_code != 200:
            self.apiStatus="error"
            #当响应码不是200时,设置resultContent里相关error数+1
            resultContent["businesses"][0]["error"]+=1
            resultContent["businesses"][0]["failed"]+=1
            resultContent["versionRecordVo"]["errors"]+=1
            resultContent["versionRecordVo"]["failures"]+=1
            logger.info("当前接口相应状态不为200,接口服务有问题")
        else:
            #当响应码是200时,设置resultContent里相关success数+1
            resultContent["versionRecordVo"]["successes"]+=1
            resultContent["businesses"][0]["success"]+=1

        #将每次的请求记录详情追加到resultContent里的caseRecords数组里
        resultContent["businesses"][0]["caseRecords"].append(
            {
            "metaElapsed": self.resAt-self.reqAt,
            "metaMethod": response.request.method,
            "metaRequestAt": self.reqAt,
            "metaRequestHeaders": format(requestdata["headers"]),
            "metaRequestBody": format(requestdata["data"]),
            "metaResponseAt": self.resAt,
            "metaResponseBody": response.text,
            "metaResponseHeaders": format(response.headers),
            "metaStatusCode": response.status_code,
            "metaUrl": requestdata["url"],
            "metaValidation": "[{\"error\":\"false\",\"failure\":\"false\",\"failureMessage\":\"断言失败信息，例如xx数据期望值100，实际返回12\",\"name\":\"响应码校验\"}]",
            "name": requestdata["apiName"],
            "status": self.apiStatus
        })


        #请求响应完成后,设置resultContent里total数+1
        resultContent["businesses"][0]["total"]+=1
        resultContent["businesses"][0]["startAt"]=datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
        resultContent["versionRecordVo"]["caseTotal"]+=1

        #将更新好的resultContent保存到结果文件apiResults.json
        resultJson2=open("apiResults.json","w",encoding="utf-8")
        json.dump(resultContent,resultJson2,indent=2,ensure_ascii=False)
        resultJson2.close()

        return response
