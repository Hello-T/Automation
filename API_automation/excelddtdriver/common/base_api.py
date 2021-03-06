# coding:utf-8
import json
import requests
from API_automation.excelddtdriver.common.readexcel import ExcelUtil
from API_automation.excelddtdriver.common.writeexcel import copy_excel, Write_excel
import base64
import hashlib

def curlmd5(a):
    m = hashlib.md5()
    m.update(a.encode('UTF-8'))
    return m.hexdigest()


def send_requests(s, testdata):
    '''封装requests请求'''
    method = testdata["method"]
    url = testdata["url"]
    # url后面的params参数
    try:
        params = eval(testdata["params"])
    except:
        params = None
    # 请求头部headers
    try:
        headers = eval(testdata["headers"])
        print("请求头部：%s" % headers)
    except:
        headers = None
    # post请求body类型
    type = testdata["type"]

    test_nub = testdata['id']
    print("*******正在执行用例：-----  %s  ----**********" % test_nub)
    print("请求方式：%s, 请求url:%s" % (method, url))
    print("请求params：%s" % params)

    # post请求body内容
    try:
        bodydata = eval(testdata["body"])
    except:
        bodydata = {}

    # 判断此接口是否是加密请求
    try:
        encrypt = testdata["encrypt"]
    except:
        encrypt = None

    # 判断传data数据还是json
    if type == "data":
        body = bodydata
    elif type == "json":
        body = json.dumps(bodydata)
    else:
        body = bodydata

    #判断data是否需要加密
    if encrypt==0:
        bodya=body
    elif encrypt==1:
        ph = 17744332211
        pw = 'e10adc3949ba59abbe56e057f20f883e'
        a = {
            "phone": ph,
            "password": pw
        }
        r = requests.post("https://qaapi.maizicare.com/api/user/login", data=a)
        d = r.json()
        x = d.get("data")
        y = x.get("token")
        params["token"]=y
    else:
        bodydata_encrypt=base64.b64encode(str(curlmd5(json.dumps(body) + curlmd5('OWNjZGY0MmNmOE1U'))[0:10]+str(base64.b64encode(json.dumps(body).encode('utf-8')),'utf-8')).encode('utf-8')).decode()
        bodya={"param":bodydata_encrypt,"tokenid":"NzJmOTM5MTE4OE1UVXlPVGs0TWpZMk1EazBOQT09"}


    if method == "post":
        print("post请求body类型为：%s ,body内容为：%s" % (type, bodya))
    elif method=="get":
        print("get请求params类型为：%s,params内容为：%s" % (type, params))

    verify = False
    res = {}   # 接受返回数据

    try:
        r = s.request(method=method,
                      url=url,
                      params=params,
                      headers=headers,
                      data=bodya,
                      verify=verify
                       )
        print("页面返回信息：%s" % r.content.decode("utf-8"))
        res['id'] = testdata['id']
        res['rowNum'] = testdata['rowNum']
        res["statuscode"] = str(r.status_code)  # 状态码转成strsssss
        res["text"] = r.content.decode("utf-8")
        res["times"] = str(r.elapsed.total_seconds())   # 接口请求时间转str
        if res["statuscode"] != "200":
            res["error"] = res["text"]
        else:
            res["error"] = ""
        res["msg"] = ""
        if testdata["checkpoint"] in res["text"]:
            res["result"] = "pass"
            print("用例测试结果:   %s---->%s" % (test_nub, res["result"]))
        else:
            res["result"] = "fail"
        return res
    except Exception as msg:
        res["msg"] = str(msg)
        return res

def wirte_result(result, filename="result.xlsx"):
    # 返回结果的行数row_nub
    row_nub = result['rowNum']
    # 写入statuscode
    wt = Write_excel(filename)
    wt.write(row_nub, 8, result['statuscode'])       # 写入返回状态码statuscode,第8列
    wt.write(row_nub, 9, result['times'])            # 耗时
    wt.write(row_nub, 10, result['error'])            # 状态码非200时的返回信息
    wt.write(row_nub, 12, result['result'])           # 测试结果 pass 还是fail
    wt.write(row_nub, 13, result['msg'])           # 抛异常

if __name__ == "__main__":
    data = ExcelUtil("debug_api.xlsx").dict_data()
    print(data[0])
    s = requests.session()
    res = send_requests(s, data[0])
    copy_excel("debug_api.xlsx", "result.xlsx")
    wirte_result(res, filename="result.xlsx")