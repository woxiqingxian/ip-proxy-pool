#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    拥有代理功能的爬虫request

"""
from datetime import datetime
from logger import Loggers
import requests
import time


global_proxy_request_url = 'http://127.0.0.1:5000'  # 计数
global_proxy_time_out_seconds = 60*3  # 代理使用时长
global_proxy_request_sleep_time = 1500  # 毫秒(获取新代理需要时间)
global_proxy_last_refresh_time = None
global_proxy_ip = None
global_request_sleep_time = 10  # 毫秒(每次发起请求需要休眠时间)


class ApiRequest(object):

    def __init__(self):
        pass

    def write_log(self, msg):
        # print msg
        log_params = {"msg": msg}
        Loggers('api_request').write('ApiRequest', log_params)
        return

    def _request_get_proxy_ip(self):
        global global_proxy_last_refresh_time
        global global_proxy_ip
        for i in range(100):
            try:
                resp = requests.get(global_proxy_request_url, timeout=2)
                if resp.status_code != 200:
                    raise Exception("resp.status_code != 200")
                resp_json = resp.json()
                if list(resp_json) == 0:
                    raise Exception("list(resp_json) == 0")
                proxy_ip = "%s:%s" % (resp_json[0]['ip'], resp_json[0]["port"])
                proxy_ip = proxy_ip.encode("utf8")
                # if  "ERROR" in resp.content:
                #     raise Exception("ERROR in resp.content")
                # proxy_ip = resp.content
                break
            except Exception, e:
                _sleep_time = global_proxy_request_sleep_time*int(i/15+1)/1000.0
                self.write_log("%s %s _sleep_time:%s" % ("ERROR", e, _sleep_time))
                proxy_ip = None
                time.sleep(_sleep_time)

        global_proxy_last_refresh_time = datetime.now()
        global_proxy_ip = proxy_ip
        self.write_log("获取新ip  %s" % (proxy_ip, ))
        return global_proxy_ip

    def _get_proxy_ip(self):
        global global_proxy_last_refresh_time
        global global_proxy_ip
        if not global_proxy_last_refresh_time:
            self.write_log("not global_proxy_last_refresh_time")
            return self._request_get_proxy_ip()

        if not global_proxy_ip:
            self.write_log("not global_proxy_ip")
            return self._request_get_proxy_ip()

        if (datetime.now()-global_proxy_last_refresh_time).total_seconds() >= global_proxy_time_out_seconds:
            self.write_log("global_proxy_ip time out %s %s" % (datetime.now(), global_proxy_last_refresh_time))
            return self._request_get_proxy_ip()

        return global_proxy_ip

    def _clear_proxy_ip(self):
        global global_proxy_ip
        global global_proxy_last_refresh_time
        self.write_log("清除proxy_ip")
        global_proxy_ip = None
        global_proxy_last_refresh_time = None
        return

    def request(self, url, params=None, method="GET", retry_times=20, timeout=3):
        """ 发起请求
        """
        resp = None
        _proxy_ip = None
        for i in range(retry_times):
            try:
                time.sleep(global_request_sleep_time/1000.0)
                proxies = None
                if i > 3:
                    # 前三次不使用代理
                    _proxy_ip = self._get_proxy_ip()
                    proxies = {
                        "http": "http://" + _proxy_ip,
                        "https": "http://"+ _proxy_ip,
                    }
                if method.upper() == "GET":
                    resp = requests.get(url, params=params, timeout=timeout, proxies=proxies)
                else:
                    resp = requests.post(url, params=params, timeout=timeout, proxies=proxies)
                if resp.status_code != 200:
                    raise Exception("status_code != 200")
                break
            except Exception as e:
                _sleep_time = i/3.0
                self.write_log("异常 _sleep_time %s  %s" % (_sleep_time, e))
                self._clear_proxy_ip()
                time.sleep(_sleep_time)

        log_params = {
            'url': url,
            'params': params,
            'method': method,
            '_proxy_ip': _proxy_ip,
        }
        self.write_log(str(log_params))
        return resp

if __name__ == "__main__":
    print ApiRequest().request("http://www.baidu.com").content
